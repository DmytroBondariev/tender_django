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


def get_detailed_tender_info(tender_id):
    try:
        response = requests.get(f"{DETAIL_API_URL}{tender_id}")
        response.raise_for_status()
        data = response.json()
        if data['data']['value']['amount'] not in (None, ""):
            amount = data['data']['value']['amount']
        else:
            amount = 0
        if "description" in data['data'].keys() and data['data']['description'] not in (None, ""):
            description = data['data']['description']
        else:
            description = "Опис не надано"
        return dict(amount=amount, description=description)
    except requests.exceptions.RequestException as e:
        print(e)


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

    def get_queryset(self):
        tenders = Tender.objects.all()
        # total_tender_amount = Tender.objects.aggregate(total_amount=Sum('amount'))['total_amount']
        return tenders


class ButtonToGetTenderView(generic.View):
    @staticmethod
    def post(request):
        try:
            response = requests.get(API_URL)
            response.raise_for_status()

            data = response.json()

            for item in data['data'][:BATCH_SIZE]:
                if not Tender.objects.filter(tender_id=item['id']).exists():
                    amount, description = get_detailed_tender_info(item['id']).values()
                    tender = Tender(
                        tender_id=item['id'],
                        date_modified=item['dateModified'],
                        amount=amount,
                        description=description

                    )
                    tender.save()

        except requests.exceptions.RequestException as e:
            print(e)

        finally:
            return HttpResponseRedirect(reverse_lazy("tenders:tender-list"))
