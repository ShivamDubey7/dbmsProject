from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user) + six.text_type(timestamp)) +  six.text_type(user)

account_activation_token = AccountActivationTokenGenerator()