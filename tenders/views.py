import requests
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from django.views import generic


from tenders.models import Tender

api_url = 'https://public.api.openprocurement.org/api/0/tenders?descending=1'
response = requests.get(api_url)
data = response.json()
for item in data['data'][:10]:
    if Tender.objects.filter(tender_id=item['id']).exists():
        continue
    tender = Tender(
        tender_id=item['id'],
        date_modified=item['dateModified']
    )
    tender.save()


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
