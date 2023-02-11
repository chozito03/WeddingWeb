from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.template import context
from django.urls import reverse_lazy
from django.views import generic


class SignUpForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


# our signup view
class SignUpView(generic.CreateView):
    # připojíme vytvořený formulář
    form_class = SignUpForm
    success_url = reverse_lazy('home')  # kam nás to přesměruje v případě úspěchu
    template_name = 'signup.html'  # použije se tento template


# Create your views here.
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
