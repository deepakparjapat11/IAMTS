from django import forms
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
import random
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives


class UserModelForm(forms.ModelForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'autocomplete': 'off',
            'class': 'form-control',
            'required': 'required'
        }),
        error_messages={'invalid': 'Please enter a valid email address.'}
    )

    def __init__(self, *args, **kwargs):
        super(UserModelForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserModelForm, self).save(commit=False)
        user.first_name = user.first_name.capitalize()
        user.last_name = user.last_name.capitalize()
        if user.id is None:
            sample = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?"
            password = "".join(random.sample(sample, 8))
            user.set_password(password)
            user.save()
            try:
                data = {

                    'email': user.email,
                    'domain': self.request.META['HTTP_HOST'],
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'user': user,
                    'token': default_token_generator.make_token(user),
                    'protocol': 'https' if self.request.is_secure() else 'http',
                    # 'frontend_url': settings.FRONTEND_URL
                }
                email_from = "<%s>" % (settings.EMAIL_FROM)
                # subject_template_name = 'email/password_set_subject.txt'
                subject = "Welcome to IAMTS"
                # subject = ''.join(subject.splitlines())
                html_content = get_template('email/welcome_email.html').render(data)
                msg = EmailMultiAlternatives(subject, '', email_from, [user.email])
                msg.attach_alternative(html_content, 'text/html')
                msg.send()
            except Exception as e:
                print(e)

        user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=254, required=True, widget=forms.TextInput(attrs={'class': 'cus-box'}))
    password = forms.CharField(widget=forms.PasswordInput(), required=True)


class PasswordRestForm(forms.Form):
    """
    reset password form
    """
    email = forms.EmailField(max_length=254, required=True)