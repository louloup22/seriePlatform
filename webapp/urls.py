#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 20:01:57 2018

@author: LouiseP
"""
from django.urls import path
from . import views, controllers
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
               path('',views.home),
               path('login/',auth_views.login,{'template_name': 'webapp/login.html'}),
               path('logout/',auth_views.logout,{'template_name': 'webapp/logout.html'}),
               path('signup/', views.signup, name= 'signup'),
               path('search/',views.search, name = 'search'),
               path('search/<str:query>/<int:page_number>',views.search_query, name = 'search'),
               path('search/<int:id>/add_favorites/<int:user_id>',controllers.add_favorite, name='add_favorite'),
               path('search/<int:id>/remove_favorites/<int:user_id>',controllers.remove_favorite, name='remove_favorite'),
               path('favorites/',views.display_favorites, name = 'favorites'),
               path('trending/<int:number_page>',views.trending, name = 'trending'),
               path('serieinfo/<int:serie_id>',views.serieinfo, name = 'serie_info'),
               path('serieinfo/<int:serie_id>/seasoninfo/<int:season_number>',views.seasoninfo, name = 'season_info'),
               # path('profile/',views.profile, name = 'profile'),
               path('genre/<str:genre_name>/<int:genre_id>/<int:page_number>',views.genre,name='genre')
        ]

