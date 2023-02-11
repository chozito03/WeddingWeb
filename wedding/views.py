from django.shortcuts import render
from django.template import context


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
