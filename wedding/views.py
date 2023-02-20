from datetime import datetime
from urllib.parse import urlencode
from django.utils import timezone
import pytz
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from django.urls import reverse_lazy, reverse
from django.views import generic

from django import forms
from wedding.models import InvitedGuests, Song
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from django.shortcuts import render
from django.conf import settings
from weddingweb.settings import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SPOTIFY_SCOPES
from django.forms import DateTimeField


class UsernameForm(forms.Form):
    username = forms.CharField(label='Username')


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


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
    # getting the user's time zone
    user_tz = request.META.get('TZ', 'UTC')
    user_timezone = pytz.timezone(user_tz)

    # Getting the current date and time in the user's timezone.
    wedding_date = datetime(2023, 3, 2, 12, tzinfo=pytz.utc)
    current_date = timezone.now().astimezone(user_timezone)
    time_left = wedding_date - current_date

    days_left = time_left.days
    # The conditions for correct inflection of the text
    if days_left == 1:
        days_text = "den"
    else:
        days_text = "dní"

    hours, remainder = divmod(time_left.seconds, 3600)
    # The conditions for correct inflection of the text in Slovak
    if hours == 1:
        hours_text = "hodina"
    elif 1 < hours < 5:
        hours_text = "hodiny"
    else:
        hours_text = "hodín"

    minutes, seconds = divmod(remainder, 60)
    # The conditions for correct inflection of the text
    if minutes == 1:
        minutes_text = "minúta"
    elif 1 < minutes < 5:
        minutes_text = "minúty"
    else:
        minutes_text = "minút"

    if seconds == 1:
        seconds_text = "sekunda"
    else:
        seconds_text = "sekúnd"

    context = {
        'days': days_left,
        'days_text': days_text,
        'hours': hours,
        'hours_text': hours_text,
        'minutes': minutes,
        'minutes_text': minutes_text,
        'seconds': seconds,
        'seconds_text': seconds_text,
    }
    return render(request, 'home.html', context)


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

        # Save the last values of the search field to the session
        request.session['last_artist'] = artist
        request.session['last_track'] = track

        client_id = SPOTIPY_CLIENT_ID
        client_secret = SPOTIPY_CLIENT_SECRET
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

        if artist and track:
            results = sp.search(q='artist:' + artist + ' track:' + track, limit=30, type='track')
        elif artist:
            results = sp.search(q='artist:' + artist, limit=50, type='track')
        elif track:
            results = sp.search(q='track:' + track, limit=50, type='track')
        else:
            message = "Prosím, zadajte aspoň jedno kritérium."
            return render(request, 'search.html', {'message': message})

        if results['tracks']['total'] == 0:
            message = "Zadana skladba sa nenasla na Spotify."
            return render(request, 'search.html', {'message': message})
        else:
            return render(request, 'results.html', {'results': results})
    return render(request, 'search.html')


def add_to_playlist(request):
    if request.method == 'POST':
        # Get values from the submitted form
        name = request.POST.get('name')
        artist = request.POST.get('artist')
        album = request.POST.get('album')
        spotify_id = request.POST.get('spotify_id')
        preview_url = request.POST.get('preview_url')
        external_urls = request.POST.get('external_urls')
        image_url = request.POST.get('image_url')


        # Check if the song already exists in the database
        if Song.objects.filter(name=name, artist=artist, album=album).exists():
            message = f"Hupps, skladba {name} od {artist} už je v svadobnom playliste!"
            return render(request, 'search.html', {'message': message})

        # Check whether the user has already added the maximum number of songs
        user = request.user
        if user.user_song.count() >= 4:
            message = "Nemôžete pridať viac ako 4 piesní."
            return render(request, 'search.html', {'message': message})

        # Creating a Song instance for a new track
        new_song = Song(
            name=name,
            artist=artist,
            album=album,
            spotify_id=spotify_id,
            preview_url=preview_url,
            external_urls=external_urls,
            image_url=image_url,
            created=datetime.now(),
            user=user,
        )
        new_song.save()
        message = f"Vyborne! Skladba {name} od {artist} sa pridala do svadobneho playlistu."
        return render(request, 'search.html', {'message': message})
    return render(request, 'search.html')


@login_required
def song_list(request):
    songs = Song.objects.all().order_by('-created')
    return render(request, 'playlist.html', {'songs': songs})



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



