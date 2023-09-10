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
from tenders.models import Tender, User

API_URL = 'https://public.api.openprocurement.org/api/0/tenders?descending=1'
DETAIL_API_URL = "https://public.api.openprocurement.org/api/0/tenders/"
BATCH_SIZE = 10

logger = logging.getLogger()


@sync_to_async
def check_tender_exists(tender_id):
    return Tender.objects.filter(tender_id=tender_id).exists()


@sync_to_async
@transaction.atomic
def save_tender(tender):
    tender.save()


async def get_tenders_info_all(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        tasks = []

        for item in data['data'][:BATCH_SIZE]:
            if not await check_tender_exists(item['id']):
                tasks.append(fetch_tender_details(item['id'], client))

        await asyncio.gather(*tasks)


async def fetch_tender_details(tender_id, client):
    try:
        tender_page = await client.get(f"{DETAIL_API_URL}{tender_id}")
        tender_page.raise_for_status()
        tender_data = tender_page.json()
        date_modified = tender_data['data']['dateModified']
        amount = tender_data['data']['value']['amount'] or 0
        description = tender_data['data'].get('description') or 'Опис не надано'

        tender = Tender(
            tender_id=tender_id,
            date_modified=date_modified,
            amount=amount,
            description=description
        )
        await save_tender(tender)
    except httpx.RequestError as e:
        logger.error(f"Error fetching tender {tender_id}: {e}")


class RegisterView(generic.CreateView):
    model = get_user_model()
    template_name = 'registration/register.html'
    success_url = reverse_lazy('tenders:index')
    form_class = UserCreateForm

    @staticmethod
    def create_user(form):
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                raise forms.ValidationError("Username already exists")
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            user.save()
            return user


class IndexView(LoginView):
    template_name = "pages/index.html"
    redirect_authenticated_user = True


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


async def button_to_fetch_tender(request):
    try:
        await get_tenders_info_all(API_URL)
    except httpx.RequestError as e:
        logger.error(f"Error fetching tenders: {e}")
    return HttpResponseRedirect(reverse_lazy("tenders:tender-list"))
