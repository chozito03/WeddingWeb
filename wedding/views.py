from datetime import datetime
from urllib.parse import urlencode
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import pytz
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
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
from wedding.models import InvitedGuests, Song, Requests, Gifts, New, Drinks, Meal, DrinksCourse, MealCourse, UserProfile
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import spotipy
from django.conf import settings
from weddingweb.settings import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SPOTIFY_SCOPES
from django.forms.models import model_to_dict
from django.db.models import Model, CharField, ForeignKey, CASCADE, IntegerField, ManyToManyField, DateTimeField, \
    BooleanField, PositiveSmallIntegerField
from django.forms import DateTimeField


class UsernameForm(forms.Form):
    username = forms.CharField(label='Username')


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class ChooseMealOneForm(forms.Form):
    meal1 = forms.ModelChoiceField(
        queryset=Meal.objects.filter(food_type__name='předkrm'),
        empty_label=None,
        widget=forms.RadioSelect
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['meal1'].widget.attrs.update({'class': 'form-check-input'})

class ChooseMealTwoForm(forms.Form):
    meal2 = forms.ModelChoiceField(
        queryset=Meal.objects.filter(food_type__name='polévka'),
        empty_label=None,
        widget=forms.RadioSelect
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['meal2'].widget.attrs.update({'class': 'form-check-input'})

class ChooseMealThreeForm(forms.Form):
    meal3 = forms.ModelChoiceField(
        queryset=Meal.objects.filter(food_type__name='hlavní chod'),
        empty_label=None,
        widget=forms.RadioSelect
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['meal3'].widget.attrs.update({'class': 'form-check-input'})

class ChooseDrinksOneForm(forms.Form):
    drink1 = forms.ModelChoiceField(
        queryset=Drinks.objects.filter(drink_type__name='přípitek'),
        empty_label=None,
        widget=forms.RadioSelect
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['drink1'].widget.attrs.update({'class': 'form-check-input'})

class ChooseDrinksTwooForm(forms.Form):
    drink2 = forms.ModelChoiceField(
        queryset=Drinks.objects.filter(drink_type__name='hlavní chod'),
        empty_label=None,
        widget=forms.RadioSelect
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['drink2'].widget.attrs.update({'class': 'form-check-input'})

class ChooseDrinksTwooChildForm(forms.Form):
    drink2 = forms.ModelChoiceField(
        queryset=Drinks.objects.filter(drink_type__name='hlavní chod', only_for_adult=False),
        empty_label=None,
        widget=forms.RadioSelect
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['drink2'].widget.attrs.update({'class': 'form-check-input'})



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

        message = "Dotazník jste již vyplnil!"
        return render(request, 'home.html', {'message': message})
    if request.method == 'POST':
        form = RequestsForm(request.POST)
        if form.is_valid():
            request_object = form.save(commit=False)
            request_object.username = request.user
            request_object.completed = True
            request_object.save()

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

            user_profile = UserProfile.objects.create(user=user)

            message = "Váš účet byl vytvořen. Můžete se přihlásit!"
            return render(request, 'home.html', {'message': message})
    else:
        form = UserRegistrationForm(initial={
            'username': username,
            'first_name': invited_guest.first_name,
            'last_name': invited_guest.last_name,
            'email': invited_guest.email,
        })

    return render(request, 'registration.html', {'form': form, 'invited_guest': invited_guest})

def set_your_vegechildmenu(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if UserProfile.objects.filter(user=request.user, completed=True).exists():

        message = "Dotazník jste již vyplnil!"
        return render(request, 'home.html', {'message': message})

    vege_meal1 = Meal.objects.filter(food_type__name='předkrm', for_vegetarian=True).first()

    user_profile.chosen_meal_1 = vege_meal1
    user_profile.save()

    vege_meal2 = Meal.objects.filter(food_type__name='polévka', for_vegetarian=True).first()

    user_profile.chosen_meal_2 = vege_meal2
    user_profile.save()

    vege_meal3 = Meal.objects.filter(food_type__name='hlavní chod', for_vegetarian=True).first()

    user_profile.chosen_meal_3 = vege_meal3
    user_profile.save()

    child_drink1 = Drinks.objects.filter(drink_type__name='přípitek', only_for_adult=False).first()

    user_profile.chosen_drink_1 = child_drink1
    user_profile.save()

    form_1 = None

    if request.method == 'POST':

        form_1 = ChooseDrinksTwooChildForm(request.POST)
        if form_1.is_valid():
            chosen_drink_2 = form_1.cleaned_data['drink2']
            user_profile.chosen_drink_2 = chosen_drink_2
            user_profile.completed = True
            user_profile.save()


        return redirect('success')

    else:
        form_1 = ChooseDrinksTwooChildForm()


    context = {
        'user_profile': user_profile,
        'vege_meal1': vege_meal1,
        'vege_meal2': vege_meal2,
        'vege_meal3': vege_meal3,
        'child_drink1': child_drink1,
        'form_1': form_1,
    }

    return render(request, 'vegechildmenu.html', context)

def set_your_vegemenu(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if UserProfile.objects.filter(user=request.user, completed=True).exists():

        message = "Dotazník jste již vyplnil!"
        return render(request, 'home.html', {'message': message})

    vege_meal1 = Meal.objects.filter(food_type__name='předkrm', for_vegetarian=True).first()

    user_profile.chosen_meal_1 = vege_meal1
    user_profile.save()

    vege_meal2 = Meal.objects.filter(food_type__name='polévka', for_vegetarian=True).first()

    user_profile.chosen_meal_2 = vege_meal2
    user_profile.save()

    vege_meal3 = Meal.objects.filter(food_type__name='hlavní chod', for_vegetarian=True).first()

    user_profile.chosen_meal_3 = vege_meal3
    user_profile.save()

    form_1 = None
    form_2 = None

    if request.method == 'POST':

        form_1 = ChooseDrinksOneForm(request.POST)
        if form_1.is_valid():
            chosen_drink_1 = form_1.cleaned_data['drink1']
            user_profile.chosen_drink_1 = chosen_drink_1
            user_profile.save()

        form_2 = ChooseDrinksTwooForm(request.POST)
        if form_2.is_valid():
            chosen_drink_2 = form_2.cleaned_data['drink2']
            user_profile.chosen_drink_2 = chosen_drink_2
            user_profile.completed = True
            user_profile.save()

        return redirect('success')

    else:
        form_1 = ChooseDrinksOneForm()
        form_2 = ChooseDrinksTwooForm()

    context = {
        'user_profile': user_profile,
        'vege_meal1': vege_meal1,
        'vege_meal2': vege_meal2,
        'vege_meal3': vege_meal3,
        'form_1': form_1,
        'form_2': form_2,
    }

    return render(request, 'vegemenu.html', context)

def set_your_childmenu(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if UserProfile.objects.filter(user=request.user, completed=True).exists():
        message = "Dotazník jste již vyplnil!"
        return render(request, 'home.html', {'message': message})

    child_drink1 = Drinks.objects.filter(drink_type__name='přípitek', only_for_adult=False).first()

    user_profile.chosen_drink_1 = child_drink1
    user_profile.save()

    form_1 = None
    form_2 = None
    form_3 = None
    form_4 = None

    if request.method == 'POST':

        form_1 = ChooseMealOneForm(request.POST)
        if form_1.is_valid():
            chosen_meal_1 = form_1.cleaned_data['meal1']
            user_profile.chosen_meal_1 = chosen_meal_1
            user_profile.save()

        form_2 = ChooseMealTwoForm(request.POST)
        if form_2.is_valid():
            chosen_meal_2 = form_2.cleaned_data['meal2']
            user_profile.chosen_meal_2 = chosen_meal_2
            user_profile.save()

        form_3 = ChooseMealThreeForm(request.POST)
        if form_3.is_valid():
            chosen_meal_3 = form_3.cleaned_data['meal3']
            user_profile.chosen_meal_3 = chosen_meal_3
            user_profile.save()

        form_4 = ChooseDrinksTwooChildForm(request.POST)
        if form_4.is_valid():
            chosen_drink_2 = form_4.cleaned_data['drink2']
            user_profile.chosen_drink_2 = chosen_drink_2
            user_profile.completed = True
            user_profile.save()

        return redirect('success')

    else:
        form_1 = ChooseMealOneForm()
        form_2 = ChooseMealTwoForm()
        form_3 = ChooseMealThreeForm()
        form_4 = ChooseDrinksTwooChildForm()

    context = {
        'user_profile': user_profile,
        'child_drink1': child_drink1,
        'form_1': form_1,
        'form_2': form_2,
        'form_3': form_3,
        'form_4': form_4,
    }

    return render(request, 'childmenu.html', context)

def set_your_menu(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    # Check if user has filled out the basic wedding questionnaire
    if not Requests.objects.filter(username=request.user).exists():
        message = "Pro výběr svatebního menu musíte nejprve vyplnit svatební dotazník!"
        return render(request, 'home.html', {'message': message})

    # kontrola, zda už to dříve nevyplnil menu
    if UserProfile.objects.filter(user=request.user, completed=True).exists():

        message = "Dotazník jste již vyplnil!"
        return render(request, 'home.html', {'message': message})


    user_vegetarian_and_child = Requests.objects.filter(username=request.user, vegetarian_food=True, age__lt=18).exists()
    user_vegetarian = Requests.objects.filter(username=request.user, vegetarian_food=True).exists()
    user_child = Requests.objects.filter(age__lt=18, username=request.user).exists()

    context = {
        'user_profile': user_profile,
        'user_vegetarian_and_child': user_vegetarian_and_child,
        'user_vegetarian': user_vegetarian,
        'user_child': user_child,
        }

    if user_vegetarian_and_child:
        return redirect('set_your_vegechildmenu')

    if user_vegetarian:
        return redirect('set_your_vegemenu')

    if user_child:
        return redirect('set_your_childmenu')

    else:
        form_1 = None
        form_2 = None
        form_3 = None
        form_4 = None
        form_5 = None

        if request.method == 'POST':

            form_1 = ChooseMealOneForm(request.POST)
            if form_1.is_valid():
                chosen_meal_1 = form_1.cleaned_data['meal1']
                user_profile.chosen_meal_1 = chosen_meal_1
                user_profile.save()

            form_2 = ChooseDrinksOneForm(request.POST)
            if form_2.is_valid():
                chosen_drink_1 = form_2.cleaned_data['drink1']
                user_profile.chosen_drink_1 = chosen_drink_1
                user_profile.save()

            form_3 = ChooseMealTwoForm(request.POST)
            if form_3.is_valid():
                chosen_meal_2 = form_3.cleaned_data['meal2']
                user_profile.chosen_meal_2 = chosen_meal_2
                user_profile.save()

            form_4 = ChooseMealThreeForm(request.POST)
            if form_4.is_valid():
                chosen_meal_3 = form_4.cleaned_data['meal3']
                user_profile.chosen_meal_3 = chosen_meal_3
                user_profile.save()

            form_5 = ChooseDrinksTwooForm(request.POST)
            if form_5.is_valid():
                chosen_drink_2 = form_5.cleaned_data['drink2']
                user_profile.chosen_drink_2 = chosen_drink_2
                user_profile.completed = True
                user_profile.save()

            return redirect('success')

        else:
            form_1 = ChooseMealOneForm()
            form_2 = ChooseDrinksOneForm()
            form_3 = ChooseMealTwoForm()
            form_4 = ChooseMealThreeForm()
            form_5 = ChooseDrinksTwooForm()

        context = {
            'user_profile': user_profile,
            'user_vegetarian': user_vegetarian,
            'user_child': user_child,
            'form_1': form_1,
            'form_2': form_2,
            'form_3': form_3,
            'form_4': form_4,
            'form_5': form_5,
            }

        return render(request, 'menu.html', context)
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
    with open('data/about_us.txt', 'r', encoding='utf-8') as file:
        file_contents = file.read()
        lines = file_contents.splitlines()
    context = {'lines': lines}
    return render(request, 'about_us.html', context)


def about_wedding(request):
    with open('data/about_wedding.txt', 'r', encoding='utf-8') as file:
        file_contents = file.read()
        lines = file_contents.splitlines()
    context = {'lines': lines}
    return render(request, 'about_wedding.html', context)


def news(request):
    all_news = New.objects.all().order_by('-created')
    # získať označené príspevky z sessions
    user_likes = request.session.get('user_likes', [])
    if request.method == 'POST':
        new_id = request.POST.get('new_id')
        if new_id and int(new_id) not in user_likes:
            new = New.objects.get(id=int(new_id))
            new.likes += 1
            new.save()
            user_likes.append(int(new_id))
            # aktualizovať sessions
            request.session['user_likes'] = user_likes
    return render(request, 'news.html', {'all_news': all_news, 'user_likes': user_likes})





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
        message = "Již jste si vybral(a) dárek."
        return render(request, 'home.html', {'message': message})


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
        song_id = request.POST.get('song_id')
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
            song_id=song_id,
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




# def add_song_to_spotify(request):
#     # Get the song ID from the submitted form
#     song_id = '6lknMmJZALXxx7emwwZWLX'
#     client_id = SPOTIPY_CLIENT_ID
#     client_secret = SPOTIPY_CLIENT_SECRET
#     # Get the authenticated user's Spotify credentials
#     sp_oauth = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri='http://localhost:8000/spotify_callback')
#     token_info = sp_oauth.get_cached_token()
#     if not token_info:
#         auth_url = sp_oauth.get_authorize_url()
#         return redirect(auth_url)
#     sp = spotipy.Spotify(auth=token_info['BQDhWFJGCBPFeuTQZ2kgXiitQ8pjK7e3-rtZL15cA04916XuhycfIsb1hm_1IuqxknZZfDiZ8eBRzKQhNLVQn0mJd4A_oB5cJqPqCdArfik_6gsHWVS4MRojN7zNJzDa0Z_67peq5sG2e-q8DRDTAEIu6enLPWagjFlNEVzxCDs1JIVX4LO7RDYDox3IUsckiGOx5OAGzl2FBQcqQHNpJE02gM0_mBPfZXF3AJRuFCG7otZa7tCR7CiNC9eLCKBBEQ'])
#     playlist_id = '65Gg8X7NVU3g95Az5aXHgo'
#
#     # Add the song to the user's playlist
#     sp.user_playlist_add_tracks(user='21lspgptue3pev6hbwr7fq3ti', playlist_id=playlist_id, tracks=[song_id])
#
#     # Render a success message
#     message = f"The song with ID {song_id} was added to the playlist."
#     return render(request, 'search.html', {'message': message})



#
# def add_song_to_spotify(request):
#     song_id = '6lknMmJZALXxx7emwwZWLX'
#     client_id = SPOTIPY_CLIENT_ID
#     client_secret = SPOTIPY_CLIENT_SECRET
#     redirect_uri = SPOTIPY_REDIRECT_URI
#     username = '21lspgptue3pev6hbwr7fq3ti'
#     scope = []
#
#     token = util.prompt_for_user_token(username, scope, client_id=client_id, client_secret=client_secret,
#                                        redirect_uri="https://open.spotify.com/playlist/65Gg8X7NVU3g95Az5aXHgo")
#
#     if token:
#         sp = spotipy.Spotify(auth=token)
#         playlist_id = '65Gg8X7NVU3g95Az5aXHgo'
#         # Add the song to the user's playlist
#         sp.playlist_add_items(playlist_id, '6lknMmJZALXxx7emwwZWLX')
#
#     # Render a success message
#     message = f"The song with ID {song_id} was added to the playlist."
#     return render(request, 'search.html', {'message': message})


