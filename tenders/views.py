import logging

import requests
from django.contrib.auth import get_user_model, forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
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


def get_tenders_info_all(url):
    response = requests.get(API_URL)
    response.raise_for_status()

    data = response.json()
    for item in data['data'][:BATCH_SIZE]:
        if not Tender.objects.filter(tender_id=item['id']).exists():
            tender_page = requests.get(f"{DETAIL_API_URL}{item['id']}")
            tender_page.raise_for_status()
            tender_data = tender_page.json()
            tender_id = tender_data['data']["plans"][0]["id"]
            date_modified = tender_data['data']['dateModified']
            if tender_data['data']['value']['amount'] not in (None, ""):
                amount = tender_data['data']['value']['amount']
            else:
                amount = 0
            if "description" in tender_data['data'].keys() and tender_data['data']['description'] not in (None, ""):
                description = tender_data['data']['description']
            else:
                description = "Опис не надано"
            tender = Tender(
                tender_id=tender_id,
                date_modified=date_modified,
                amount=amount,
                description=description

            )
            tender.save()


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


class ButtonToGetTenderView(generic.View):
    @staticmethod
    def post(request):
        try:
            get_tenders_info_all(API_URL)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching tenders: {e}")

        finally:
            return HttpResponseRedirect(reverse_lazy("tenders:tender-list"))
