from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from tenders.forms import UserLoginForm
from tenders.models import Tender


class IndexView(LoginView):
    template_name = "pages/index.html"
    form_class = UserLoginForm
    redirect_authenticated_user = True

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("tenders:tender-list")
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("tenders:tender-list")


class TenderListView(generic.ListView, LoginRequiredMixin):
    model = Tender
    paginate_by = 10
    template_name = "pages/tender_list.html"

    def get_queryset(self):
        tenders = Tender.objects.all()
        total_tender_amount = Tender.objects.aggregate(total_amount=Sum('amount'))['total_amount']
        return tenders, total_tender_amount

