#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 11 20:02:21 2018

@author: LouiseP
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from webapp.models import Search

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional')
    email = forms.EmailField(max_length=255, help_text="Enter a valid email")
    
    class Meta:
        model = User
        fields = ('username','first_name','last_name','email','password1','password2',)

class SearchForm(forms.Form):
    query = forms.CharField(max_length=30,required=True,help_text='Search TV shows here')
    class Meta:
        model = Search
        fields = ('query',)
        
