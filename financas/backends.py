from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # procurar usuário pelo e-mail
            user = User.objects.get(email=username)
        except User.DoesNotExist:
            return None
        else:
            if password is not None and user.check_password(password):
                return user
        return None
