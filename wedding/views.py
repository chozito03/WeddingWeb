from urllib.parse import urlencode
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import context
from django.urls import reverse_lazy, reverse
from django.views import generic
from spotipy import util
from django.dispatch import receiver
from django.db.models.signals import pre_save
from weddingweb import settings
from django import forms
from django.views.decorators.http import require_POST
from wedding.models import InvitedGuests, Song, Requests, Gifts
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.shortcuts import render
from django.conf import settings
from weddingweb.settings import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SPOTIFY_SCOPES
from django.forms.models import model_to_dict
from django.db.models import Model, CharField, ForeignKey, CASCADE, IntegerField, ManyToManyField, DateTimeField, \
    BooleanField, PositiveSmallIntegerField



class UsernameForm(forms.Form):
    username = forms.CharField(label='Username')


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class RequestsForm(forms.ModelForm):

    age = forms.IntegerField(required=False, label='Zadejte svůj věk')
    hotel = forms.BooleanField(required=False, label='Potřebujete zajistit ubytování?')
    kids = forms.BooleanField(required=False, label='Berete na svatbu děti?')
    vegetarian_food = forms.BooleanField(required=False, label='Požadujete vegetariánské jídlo?')
    takeaway_to_restaurant = forms.BooleanField(required=False, label='Potřebujete odvoz z kostela na hostinu?')
    takeaway_to_home = forms.BooleanField(required=False, label='Potřebujete odvoz z hostiny domů?')

    class Meta:
        model = Requests
        fields = ['age', 'hotel', 'kids', 'vegetarian_food', 'takeaway_to_restaurant', 'takeaway_to_home']
"""
@login_required
def requests_form(request):
    if request.method == 'POST':
        form = RequestsForm(request.POST)
        if form.is_valid():
            request = form.save(commit=False)
            request.username = request.user
            request.save()
            return redirect('success')
    else:
        form = RequestsForm()
    return render(request, 'requests.html', {'form': form})
"""



@receiver(pre_save, sender=Requests)
def set_request_user(sender, instance, **kwargs):
    # if not instance.user:
        # instance.user = get_user_model().objects.get(pk=instance.username.pk)
    if not instance.username:
            instance.username = instance.user
def success_view(request):
    return render(request, 'success.html')

@login_required
def requests_form(request):
    if Requests.objects.filter(username=request.user, completed=True).exists():
        messages.error(request, 'Dotazník již byl vyplněn!')
        return redirect('home')
    if request.method == 'POST':
        form = RequestsForm(request.POST)
        if form.is_valid():
            request_object = form.save(commit=False)
            request_object.username = request.user
            request_object.completed = True
            request_object.save()
            messages.success(request, 'Formulář byl úspěšně odeslán!')
            return redirect('success')
    else:
        form = RequestsForm()
    return render(request, 'requests.html', {'form': form})


def verify_username(request):
    if request.method == 'POST':
        form = UsernameForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            try:
                invited_guest = InvitedGuests.objects.get(username=username)
            except InvitedGuests.DoesNotExist:
                invited_guest = None

            if invited_guest:
                # data = {
                    # 'username': invited_guest.username,
                    # 'first_name': invited_guest.first_name,
                    # 'last_name': invited_guest.last_name,
                    # 'email': invited_guest.email,
                # }
                # user_form = UserRegistrationForm(data)

                # return render(request, 'registration.html', {'form': user_form})
                # return redirect(reverse('registration', kwargs={'username': username}))
                return redirect('registration', username=username)


            else:
                messages.error(request, 'Invalid username')
    else:
        form = UsernameForm()

    return render(request, 'verify_username.html', {'form': form})


def registration(request, username):
    try:
        invited_guest = InvitedGuests.objects.get(username=username)
    except InvitedGuests.DoesNotExist:
        return HttpResponse('Invalid invitation URL')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, initial={
            'username': username,
            'first_name': invited_guest.first_name,
            'last_name': invited_guest.last_name,
            'email': invited_guest.email,
        })

        if form.is_valid():
            user = form.save(commit=False)
            user.username = invited_guest.username
            user.email = invited_guest.email
            user.first_name = invited_guest.first_name
            user.last_name = invited_guest.last_name
            user.save()

            messages.success(request, 'Your account has been created! You are now able to log in.')
            return redirect('home')
    else:
        form = UserRegistrationForm(initial={
            'username': username,
            'first_name': invited_guest.first_name,
            'last_name': invited_guest.last_name,
            'email': invited_guest.email,
        })

    return render(request, 'registration.html', {'form': form, 'invited_guest': invited_guest})


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
    with open('data/about_us.txt', 'r') as file:
        file_contents = file.read()
        lines = file_contents.splitlines()
    context = {'lines': lines}
    return render(request, 'about_us.html', context)


def about_wedding(request):
    return render(request, 'about_wedding.html')


def news(request):
    return render(request, 'news.html')


def invitation(request):
    return render(request, 'invitation.html')

class GiftsForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
    class Meta:
        model = Gifts
        fields = '__all__'

class GiftsView(generic.ListView):
    template_name = 'gifts.html'
    model = Gifts

class GiftDetailView(generic.DetailView):
    model = Gifts
    template_name = 'gift_detail.html'  # specify the name of the template to use
    context_object_name = 'gift'  # specify the name of the variable to use in the template

@require_POST
@login_required
def gift_select(request, pk):
    # Získání dárku, který má být vybrán
    gift = get_object_or_404(Gifts, pk=pk)
    # Ověření, zda uživatel již nějaký dar vybral
    if Gifts.objects.filter(sorted_by=request.user).exists():
        messages.warning(request, "Již jste si vybral(a) dárek.")
        return redirect('gift-detail', pk=pk)

    # Uložení výběru dárku pro daného uživatele
    gift.selected = True
    gift.sorted_by = request.user
    gift.save()

    # Přesměrování na detail dárku
    return redirect('gift-detail', pk=gift.pk)

"""
def gifts(request):
    gifts = Gifts.objects.all()
    context = {'gifts': gifts}
    return render(request, 'gifts.html', context)
"""

def search_song(request):
    if request.method == 'POST':
        artist = request.POST.get('artist')
        track = request.POST.get('track')

        client_id = SPOTIPY_CLIENT_ID
        client_secret = SPOTIPY_CLIENT_SECRET
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        results = sp.search(q='artist:' + artist + ' track:' + track, limit=10, type='track')

        return render(request, 'results.html', {'results': results})
    return render(request, 'search.html')


def add_to_playlist(request):
    if request.method == 'POST':
        # Získajte hodnoty z odoslaného formulára
        name = request.POST.get('name')
        artist = request.POST.get('artist')
        album = request.POST.get('album')
        spotify_id = request.POST.get('spotify_id')
        preview_url = request.POST.get('preview_url')
        image_url = request.POST.get('image_url')

        # Vytvorte inštanciu Song pre novú skladbu
        new_song = Song(
            name=name,
            artist=artist,
            album=album,
            spotify_id=spotify_id,
            preview_url=preview_url,
            image_url=image_url,
        )
        new_song.save()
        return render(request, 'search.html')
    return render(request, 'search.html')
# def add_to_playlist(request, track_id):
#     client_id = SPOTIPY_CLIENT_ID
#     client_secret = SPOTIPY_CLIENT_SECRET
#     redirect_uri = SPOTIPY_REDIRECT_URI
#     username = '21lspgptue3pev6hbwr7fq3ti'
#     scope = SPOTIFY_SCOPES
#
#     token = util.prompt_for_user_token(username, scope, client_id=client_id, client_secret=client_secret,
#                                        redirect_uri=redirect_uri)
#
#     if token:
#         sp = spotipy.Spotify(auth=token)
#         playlist_id = '65Gg8X7NVU3g95Az5aXHgo?si=de5a72aba64d4d65'
#         sp.user_playlist_add_tracks(user=sp.current_user()['id'], playlist_id=playlist_id, tracks=[track_id])
#         return redirect('search.html')
#     return redirect('search.html')



