import logging
import httpx
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic


from tenders.forms import UserCreateForm
from tenders.models import Tender
from tenders.utils import get_tenders_info_all

API_URL = 'https://public.api.openprocurement.org/api/0/tenders?descending=1'

logger = logging.getLogger()

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
