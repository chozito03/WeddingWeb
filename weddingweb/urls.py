"""weddingweb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from wedding.views import home, about_us, news, invitation, about_wedding, verify_username, registration, search_song, \
    add_to_playlist, song_list

urlpatterns = [
    path('admin/', admin.site.urls),
    # app wedding
    path('', home, name='home'),
    path('about_us/', about_us, name='about_us'),
    path('about_wedding/', about_wedding, name='about_wedding'),
    path('news/', news, name='news'),
    path('invitation/', invitation, name='invitation'),
    path('verify_username/', verify_username, name='verify_username'),
    path('playlist/', song_list, name='playlist'),
    path('search/', search_song, name='search_song'),
    path('add_to_playlist/', add_to_playlist, name='add_to_playlist'),
    path('registration/<username>/', registration, name='registration'),
]


