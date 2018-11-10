#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 20:02:21 2018

@author: LouiseP
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from webapp.models import Search,Profil

#Dans ce fichier nous formatons les différents formulaires que l'utilisateur va devoir remplir
#Nous nous basons sur des modules Django déjà existants que nous reformatons

#Formatage du formulaire d'inscription
class SignUpForm(UserCreationForm):
    #On spécificie les attentes sur le nom, prénom et email
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    email = forms.EmailField(max_length=255, help_text="Enter a valid email")

    #Définition de la class Meta grâce au model Django préexistant en spécifiant les paramètres retenus à remplir par l'utilisateur
    class Meta:
        model = User
        fields = ('username','first_name','last_name','email','password1','password2',)

#Formatage du formulaire de recherche
class SearchForm(forms.Form):
    #On spécifie les attentes sur la recherche 
    query = forms.CharField(max_length=30,required=True,label=None)
    

        
