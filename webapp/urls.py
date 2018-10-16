#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 20:01:57 2018

@author: LouiseP
"""
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
               path('',views.home),
               path('login/',auth_views.login,{'template_name': 'webapp/login.html'}),
               path('logout/',auth_views.logout,{'template_name': 'webapp/logout.html'}),
               path('signup/', views.signup, name= 'signup'),
               path('search/',views.search, name = 'search')
               path('favorites/',views.favorites, name = 'favorites')
        ]

