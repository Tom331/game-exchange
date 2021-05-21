from django import forms

from django.contrib.auth import get_user_model
User = get_user_model()
from django.conf import settings
# User = settings.AUTH_USER_MODEL
# from users.models import User

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from django.template import Context, Template
from django.contrib.auth.mixins import LoginRequiredMixin


print('~~~top of users/forms.py~~~')
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        # collect lat and long from Maps API
        fields = ['username', 'email', 'lat', 'long', 'travel_radius', 'location_name', 'activation_key', 'conf_trade_opt_out_key', 'password1', 'password2']
        widgets = {'lat': forms.HiddenInput(), 'long': forms.HiddenInput(), 'travel_radius': forms.HiddenInput(), 'location_name': forms.HiddenInput(),
                   'activation_key': forms.HiddenInput(), 'conf_trade_opt_out_key': forms.HiddenInput()}

    # The email is written in a text file (it contains templatetags which are populated by the method below)
    def sendEmail(self, reg_data):
        link = reg_data['activation_url'] + reg_data['activation_key']
        c = Context({'activation_link': link, 'username': reg_data['username']})
        f = open(settings.MEDIA_ROOT + reg_data['email_path'], 'r')
        t = Template(f.read())
        f.close()
        message = t.render(c)
        # print unicode(message).encode('utf8')
        send_mail(reg_data['email_subject'], message, 'Game Exchange <no-reply@GameExchange.com>', [reg_data['email']],
                  fail_silently=False)


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'confirmed_trade_email_opt_in', 'lat', 'long', 'travel_radius', 'location_name']
        labels = {
            'confirmed_trade_email_opt_in': 'Receive email when another user confirms one of your offers',
        }
        widgets = {'lat': forms.HiddenInput(), 'long': forms.HiddenInput(),
                   'travel_radius': forms.HiddenInput(), 'location_name': forms.HiddenInput()}


class MyUserPasswordResetForm(PasswordResetForm):

    class Meta:
        model = User


# login required for this form. Calls user/views.py/new_activation_link()
class ResendEmailConfirmationForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['activation_key']
        widgets = {'activation_key': forms.HiddenInput()}

    def resendEmail(self, reg_data):
        # link = "http://localhost:8000/activate/" + reg_data['activation_key']
        link = reg_data['activation_url'] + reg_data['activation_key']
        c = Context({'activation_link': link, 'username': reg_data['username']})
        f = open(settings.MEDIA_ROOT + reg_data['email_path'], 'r')
        t = Template(f.read())
        f.close()
        message = t.render(c)
        # print unicode(message).encode('utf8')
        print('~~~ABOUT TO FINISH RESEND EMAIL~~~')
        send_mail(reg_data['email_subject'], message, 'Game Exchange Help <no-reply@GameExchange.com>', [reg_data['email']],
                  fail_silently=False)

print('~~~bottom of users/forms.py~~~')

