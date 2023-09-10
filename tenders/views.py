import asyncio
import logging
import httpx
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model, forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic

from tenders.forms import UserCreateForm
from tenders.models import Tender

API_URL = 'https://public.api.openprocurement.org/api/0/tenders?descending=1'
DETAIL_API_URL = "https://public.api.openprocurement.org/api/0/tenders/"
BATCH_SIZE = 10

logger = logging.getLogger()

""" Check if a tender with the given ID exists in the database. """


@sync_to_async
def check_tender_exists(tender_id):
    return Tender.objects.filter(tender_id=tender_id).exists()


""" Save a tender object to the database. """


@sync_to_async
@transaction.atomic
def save_tender(tender):
    tender.save()


""" Update an existing tender's information in the database if it has changed since the last update. """


@sync_to_async
@transaction.atomic
def update_tender(tender_id, date_modified, amount, description):
    tender = Tender.objects.get(tender_id=tender_id)
    if tender.date_modified != date_modified or tender.amount != amount or tender.description != description:
        tender.date_modified = date_modified
        tender.amount = amount
        tender.description = description
        tender.save()
    else:
        logger.info(f"Tender {tender_id} is up to date")


""" Fetch information about tenders from the specified API URL. """


async def get_tenders_info_all(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        tasks = []

        for item in data['data'][:BATCH_SIZE]:
            if not await check_tender_exists(item['id']):
                tasks.append(fetch_tender_details(item['id'], client))
            else:
                tasks.append(fetch_tender_details(item['id'], client, update=True))

        await asyncio.gather(*tasks)


""" Fetch details of a tender from the API and update the database. """


async def fetch_tender_details(tender_id, client, update=False):
    try:
        tender_page = await client.get(f"{DETAIL_API_URL}{tender_id}")
        tender_page.raise_for_status()
        tender_data = tender_page.json()
        date_modified = tender_data['data']['dateModified']
        amount = tender_data['data']['value']['amount'] or 0
        description = tender_data['data'].get('description') or 'Опис не надано'

        if update:
            await update_tender(tender_id, date_modified, amount, description)
        else:
            tender = Tender(
                tender_id=tender_id,
                date_modified=date_modified,
                amount=amount,
                description=description
            )
            await save_tender(tender)
    except httpx.RequestError as e:
        logger.error(f"Error fetching tender {tender_id}: {e}")


""" User registration view. """


class RegisterView(generic.CreateView):
    model = get_user_model()
    template_name = 'registration/register.html'
    success_url = reverse_lazy('tenders:index')
    form_class = UserCreateForm


class IndexView(LoginView):
    template_name = "pages/index.html"
    redirect_authenticated_user = True


""" Add the total amount of all tenders to the context. This is done in a separate view because the total amount is
displayed on every page, and it would be inefficient to calculate it every time a page is loaded.
Login url is set to "/" to redefine the default account/login/ url. """


class TenderListView(LoginRequiredMixin, generic.ListView):
    model = Tender
    paginate_by = 10
    template_name = "pages/tender_list.html"
    login_url = "/"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        if Tender.objects.exists():
            total_tender_amount = round(Tender.objects.aggregate(Sum('amount'))['amount__sum'], 2)
            context['total_tender_amount'] = total_tender_amount
        return context


""" Button handler view to initiate the process of fetching tenders from the API. """


async def button_to_fetch_tender(request):
    try:
        await get_tenders_info_all(API_URL)
    except httpx.RequestError as e:
        logger.error(f"Error fetching tenders: {e}")
    return HttpResponseRedirect(reverse_lazy("tenders:tender-list"))
