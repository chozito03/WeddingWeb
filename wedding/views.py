from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template import context
from django.urls import reverse_lazy, reverse
from django.views import generic
from spotipy import util

from weddingweb import settings
from django import forms
from wedding.models import InvitedGuests, Song
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.shortcuts import render
from django.conf import settings
from weddingweb.settings import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SPOTIFY_SCOPES


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



