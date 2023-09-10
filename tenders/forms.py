from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


"""Forms for authentication and user creation with model User."""


class UserCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields
