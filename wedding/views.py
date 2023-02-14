from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import context
from django.urls import reverse_lazy, reverse
from django.views import generic

from django import forms

from wedding.models import InvitedGuests


class UsernameForm(forms.Form):
    username = forms.CharField(label='Username')


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)

        # get the InvitedGuests instance for the current user
        try:
            invited_guest = InvitedGuests.objects.get(username=self.initial['username'])
            self.fields['first_name'].initial = invited_guest.first_name
            self.fields['last_name'].initial = invited_guest.surname
            self.fields['email'].initial = invited_guest.email
        except InvitedGuests.DoesNotExist:
            pass


def verify_username(request):
    if request.method == 'POST':
        form = UsernameForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if InvitedGuests.objects.filter(username=username).exists():
                registration_url = reverse('registration', args=[username])
                return HttpResponseRedirect(registration_url)
            else:
                messages.error(request, 'Invalid username')
    else:
        form = UsernameForm()

    return render(request, 'verify_username.html', {'form': form})


def registration(request, username):
    invited_guests = InvitedGuests.objects.get(username=username)
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserCreationForm(initial={
            'username': invited_guests.username,
            'first_name': invited_guests.first_name,
            'last_name': invited_guests.surname,
            'email': invited_guests.email,
        })

    return render(request, 'registration.html', {'form': form})

"""
class SignUpForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2',)


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('home')
    template_name = 'signup.html'
"""


def home(request):
    return render(request, 'home.html')


def about_us(request):
    return render(request, 'about_us.html')


def about_wedding(request):
    return render(request, 'about_wedding.html')


def news(request):
    return render(request, 'news.html')


def invitation(request):
    return render(request, 'invitation.html')
# Create your views here.
