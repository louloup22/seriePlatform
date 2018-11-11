#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 20:01:57 2018

@author: LouiseP
"""
from django.urls import path
from webapp.views import Views
from . import controllers
from django.contrib.auth import views as auth_views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static


#Dans ce fichier nous spécifions les liens entre les urls des pages du site et nos fonctions de notre programme python
#Ainsi quand l'utilisateur clique sur une page, cela déclenche bien la fonction python associée
urlpatterns = [
               path('',Views.home),
               path('login/',auth_views.login,{'template_name': 'webapp/login.html'}),
               path('logout/',auth_views.logout,{'template_name': 'webapp/logout.html'}),
               path('signup/', Views.signup, name= 'signup'),
               path('search/',Views.search, name = 'search'),
               path('search/<str:query>/<int:page_number>',Views.search_query, name = 'search'),
               path('search/<int:id>/add_favorites/<int:user_id>',controllers.add_favorite, name='add_favorite'),
               path('search/<int:id>/remove_favorites/<int:user_id>',controllers.remove_favorite, name='remove_favorite'),
               path('favorites/',Views.display_favorites, name = 'favorites'),
               path('trending/<int:number_page>',Views.trending, name = 'trending'),
               path('serieinfo/<int:serie_id>',Views.serieinfo, name = 'serie_info'),
               path('serieinfo/<int:serie_id>/seasoninfo/<int:season_number>/<int:nb_seasons>',Views.seasoninfo, name = 'season_info'),
               path('genre/<str:genre_name>/<int:genre_id>/<int:page_number>',Views.genre,name='genre')
        ]
