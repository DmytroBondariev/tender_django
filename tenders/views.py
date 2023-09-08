from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy


class IndexView(LoginView):
    template_name = "pages/index.html"
    form_class = UserLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("tenders:tender-list")
