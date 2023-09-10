import requests
from django.contrib.auth import get_user_model, forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from django.urls import reverse_lazy
from django.views import generic

from tenders.forms import UserCreateForm
from tenders.models import Tender, User

API_URL = 'https://public.api.openprocurement.org/api/0/tenders?descending=1'
# response = requests.get(api_url)
# data = response.json()
# for item in data['data'][:10]:
#     if Tender.objects.filter(tender_id=item['id']).exists():
#         continue
#     tender = Tender(
#         tender_id=item['id'],
#         date_modified=item['dateModified']
#     )
#     tender.save()


class RegisterView(generic.CreateView):
    model = User
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


# class ToggleAssignToTaskView(generic.View):
#     @staticmethod
#     def post(request, pk):
#         worker = Worker.objects.get(id=request.user.id)
#         task = Task.objects.get(id=pk)
#         if task in worker.tasks.all():
#             worker.tasks.remove(task)
#         else:
#             worker.tasks.add(task)
#         return HttpResponseRedirect(
#             reverse_lazy("task_manager:task-detail", args=[pk])
#         )

class ButtonToGetTenderView(generic.View):
    @staticmethod
    def post(request):
        response = requests.get(API_URL)
        data = response.json()
        for item in data['data'][:10]:
            if Tender.objects.filter(tender_id=item['id']).exists():
                continue
            tender = Tender(
                tender_id=item['id'],
                date_modified=item['dateModified']
            )
            tender.save()
