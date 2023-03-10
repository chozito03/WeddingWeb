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
from django.urls import path, include
from django.contrib.auth.decorators import login_required


from wedding.views import home, about_us, news, invitation, about_wedding, verify_username, registration, search_song, \
    add_to_playlist, requests_form, success_view, GiftsView, GiftDetailView, gift_select, song_list, set_your_menu, \
    set_your_vegemenu, set_your_childmenu, set_your_vegechildmenu, MessageCreateView, MessagesView, success2_view, \
    success3_view

urlpatterns = [
    path('admin/', admin.site.urls),
    # app wedding
    path('', home, name='home'),
    path('about_us/', about_us, name='about_us'),
    path('about_wedding/', about_wedding, name='about_wedding'),
    path('news/', news, name='news'),
    path('invitation/', invitation, name='invitation'),
    path('verify_or_login/', include('django.contrib.auth.urls')),
    path('verify_or_login/verify_username', verify_username, name='verify_username'),
    path('playlist/', song_list, name='playlist'),
    path('search/', search_song, name='search_song'),
    path('add_to_playlist/', add_to_playlist, name='add_to_playlist'),
    path('registration/<username>/', registration, name='registration'),
    path('requests/', login_required(requests_form), name='requests_form'),
    path('requests/success/', success_view, name='success'),
    path('menu/success2/', success2_view, name='success2'),
    path('gifts/success3/', success3_view, name='success3'),
    path('gifts/', login_required(GiftsView.as_view()), name='gifts'),
    path('gifts/<pk>/', login_required(GiftDetailView.as_view()), name='gift-detail'),
    path('gifts/<int:pk>/select/', gift_select, name='gift-select'),
    path('menu/', login_required(set_your_menu), name='set_your_menu'),
    path('menu/vegemenu/', set_your_vegemenu, name='set_your_vegemenu'),
    path('menu/childmenu/', set_your_childmenu, name='set_your_childmenu'),
    path('menu/vegechildmenu/', set_your_vegechildmenu, name='set_your_vegechildmenu'),
    path('add_message/', MessageCreateView.as_view(), name='add_message'),
    path('messages/', MessagesView.as_view(), name='messages'),
]


