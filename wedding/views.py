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
from wedding.models import InvitedGuests, Song, Requests, Gifts, New, Drinks, Meal, DrinksCourse, MealCourse, \
    UserProfile, Messages
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import spotipy
from django.conf import settings
from weddingweb.settings import SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, SPOTIFY_SCOPES
from django.forms.models import model_to_dict
from django.db.models import Model, CharField, ForeignKey, CASCADE, IntegerField, ManyToManyField, DateTimeField, \
    BooleanField, PositiveSmallIntegerField
from django.forms import DateTimeField
from django.views.generic import TemplateView, ListView, FormView, \
    CreateView, UpdateView, DeleteView


class UsernameForm(forms.Form):
    username = forms.CharField(label='Ověřovací kód:')


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class ChooseMealOneForm(forms.Form):
    meal1 = forms.ModelChoiceField(
        queryset=Meal.objects.filter(food_type__name='předkrm'),
        empty_label=None,
        widget=forms.RadioSelect,
        label='',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['meal1'].widget.attrs.update({'class': 'form-check-input'})


class ChooseMealTwoForm(forms.Form):
    meal2 = forms.ModelChoiceField(
        queryset=Meal.objects.filter(food_type__name='polévka'),
        empty_label=None,
        widget=forms.RadioSelect,
        label='',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['meal2'].widget.attrs.update({'class': 'form-check-input'})


class ChooseMealThreeForm(forms.Form):
    meal3 = forms.ModelChoiceField(
        queryset=Meal.objects.filter(food_type__name='hlavní chod'),
        empty_label=None,
        widget=forms.RadioSelect,
        label='',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['meal3'].widget.attrs.update({'class': 'form-check-input'})


class ChooseDrinksOneForm(forms.Form):
    drink1 = forms.ModelChoiceField(
        queryset=Drinks.objects.filter(drink_type__name='přípitek'),
        empty_label=None,
        widget=forms.RadioSelect,
        label='',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['drink1'].widget.attrs.update({'class': 'form-check-input'})


class ChooseDrinksTwooForm(forms.Form):
    drink2 = forms.ModelChoiceField(
        queryset=Drinks.objects.filter(drink_type__name='hlavní chod'),
        empty_label=None,
        widget=forms.RadioSelect,
        label='',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['drink2'].widget.attrs.update({'class': 'form-check-input'})


class ChooseDrinksTwooChildForm(forms.Form):
    drink2 = forms.ModelChoiceField(
        queryset=Drinks.objects.filter(drink_type__name='hlavní chod', only_for_adult=False),
        empty_label=None,
        widget=forms.RadioSelect,
        label='',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['drink2'].widget.attrs.update({'class': 'form-check-input'})


class RequestsForm(forms.ModelForm):
    # basic wedding form
    age = forms.IntegerField(required=False, label='Zadejte svůj věk')
    hotel = forms.BooleanField(required=False, label='Potřebujete zajistit ubytování?')
    kids = forms.BooleanField(required=False, label='Berete na svatbu děti?')
    vegetarian_food = forms.BooleanField(required=False, label='Požadujete vegetariánské jídlo?')
    takeaway_to_restaurant = forms.BooleanField(required=False, label='Potřebujete odvoz z kostela na hostinu?')
    takeaway_to_home = forms.BooleanField(required=False, label='Potřebujete odvoz z hostiny domů?')

    class Meta:
        model = Requests
        fields = ['age', 'hotel', 'kids', 'vegetarian_food', 'takeaway_to_restaurant', 'takeaway_to_home']


@receiver(pre_save, sender=Requests)
def set_request_user(sender, instance, **kwargs):

    if not instance.username:
            instance.username = instance.user


def success_view(request):
    return render(request, 'success.html')


def success2_view(request):
    return render(request, 'success2.html')


def success3_view(request):
    return render(request, 'success3.html')


@login_required
def requests_form(request):
    # basic wedding questionnaire
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
    # the user enters his invitation code and it is compared with the code in the model InvitedGuests
    if request.method == 'POST':
        form = UsernameForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            try:
                invited_guest = InvitedGuests.objects.get(username=username)
            except InvitedGuests.DoesNotExist:
                invited_guest = None
            # if the code agrees, the user is redirected to the registration
            if invited_guest:
                return redirect('registration', username=username)

            else:
                messages.error(request, 'Invalid username')
    else:
        form = UsernameForm()

    return render(request, 'verify_username.html', {'form': form})


def registration(request, username):
    # basic user data is taken from the model InvitedGuests
    try:
        invited_guest = InvitedGuests.objects.get(username=username)
    except InvitedGuests.DoesNotExist:
        return HttpResponse('Invalid invitation URL')

    if request.method == 'POST':
        # inserts values from the model InvitedGuests to the user
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
            # at the same time the user_profile model is created
            # user_profile saved information about select menu from each user
            user_profile = UserProfile.objects.create(user=user)

            return redirect('login')

    else:
        form = UserRegistrationForm(initial={
            'username': username,
            'first_name': invited_guest.first_name,
            'last_name': invited_guest.last_name,
            'email': invited_guest.email,
        })

    return render(request, 'registration.html', {'form': form, 'invited_guest': invited_guest})


def set_your_vegechildmenu(request):
    # condition that the user is under 18 years of age and requests a vegetarian meal
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if UserProfile.objects.filter(user=request.user, completed=True).exists():

        message = "Své menu jste si již vybral!"
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


        return redirect('success2')

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
    #  condition that the user requests a vegetarian meal
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if UserProfile.objects.filter(user=request.user, completed=True).exists():

        message = "Své menu jste si již vybral!"
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

        return redirect('success2')

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
    # condition that the user is under 18 years
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if UserProfile.objects.filter(user=request.user, completed=True).exists():
        message = "Své menu jste si již vybral!"
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

        return redirect('success2')

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


@login_required
def set_your_menu(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    # Check if user has filled out the basic wedding questionnaire
    if not Requests.objects.filter(username=request.user).exists():
        message = "Pro výběr svatebního menu musíte nejprve vyplnit svatební dotazník!"
        return render(request, 'home.html', {'message': message})

    # check if it hasn't filled the wedding menu before
    if UserProfile.objects.filter(user=request.user, completed=True).exists():
        message = "Své menu jste si již vybral!"
        return render(request, 'home.html', {'message': message})
    # conditions were taken from the basic wedding questionnaire
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

            return redirect('success2')

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


def home(request):
    # getting the user's time zone
    user_tz = request.META.get('TZ', 'UTC')
    user_timezone = pytz.timezone(user_tz)

    # Getting the current date and time in the user's timezone.
    wedding_date = datetime(2023, 3, 18, 12, tzinfo=pytz.utc)
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
        hours_text = "hodin"

    minutes, seconds = divmod(remainder, 60)
    # The conditions for correct inflection of the text
    if minutes == 1:
        minutes_text = "minuta"
    elif 1 < minutes < 5:
        minutes_text = "minuty"
    else:
        minutes_text = "minut"

    if seconds == 1:
        seconds_text = "vteřina"
    else:
        seconds_text = "vteřin"

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
    gift = get_object_or_404(Gifts, pk=pk)
    # Verify that the user has not already selected a gift
    if Gifts.objects.filter(sorted_by=request.user).exists():
        message = "Již jste si vybral(a) dárek."
        return render(request, 'home.html', {'message': message})

    gift.selected = True
    gift.sorted_by = request.user
    gift.save()

    return redirect('success3')


class MessagesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Messages
        fields = '__all__'
        labels = {
            'author': 'Vaše jméno:',
            'message': 'Váš vzkaz:',
        }



class MessagesView(generic.ListView):
    # overview of all messages
    template_name = 'messages.html'
    model = Messages


class MessageCreateView(generic.CreateView):
    # entering a message by a visitor
  template_name = 'add_message.html'
  form_class = MessagesForm
  success_url = reverse_lazy('messages')
  permission_required = 'wedding.add_message'


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
            message = "Prosím, zadejte alespoň jedno kritérium."
            return render(request, 'search.html', {'message': message})

        if results['tracks']['total'] == 0:
            message = "Zadaná skladba nebyla nalezena na Spotify."
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
            message = f"Hupps, skladba {name} od {artist} už je ve svatebním playlistu!"
            return render(request, 'search.html', {'message': message})

        # Check whether the user has already added the maximum number of songs
        user = request.user
        if user.user_song.count() >= 4:
            message = "Nemůžete přidat více než 4 písničky."
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

        message = f"Vyborně!! Skladba {name} od {artist} se přidala do svatebního playlistu."
        return render(request, 'search.html', {'message': message})
    return render(request, 'search.html')


@login_required
def song_list(request):
    songs = Song.objects.all().order_by('-created')
    return render(request, 'playlist.html', {'songs': songs})


