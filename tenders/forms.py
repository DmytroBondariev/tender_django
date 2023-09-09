from django.contrib.auth.forms import AuthenticationForm, UsernameField, UserCreationForm


from tenders.models import User


class UserCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields
