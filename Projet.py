#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  7 10:28:04 2018

@author: paullavest
"""
import config
import json
import requests
from pandas import DataFrame as df
import re
import socket
import select


class Users_inventory:
    def __init(self):
        self._dict_users = {}
        self._user_name_dico = {}
        self._email_dico = {}
        self._password_dico = {}
    
    def _add_user(self, user_id, user):
        self._dict_users[user_id]=user
        
    def _return_dataframe_users(self):
        dataframe = df.from_dict(self._dict_users, orient='index')
        return dataframe

class Users:
    
    _compteur = 0
    
    def __init__(self,):
        self.id = Users._compteur
        self.name = input("enter your first and last name")
        self.name = str(self.name)
        self.email = ""
        self.user_name = ""
        self.password = ""
        expression1 = ^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9]).{8,}
        expression2 = ^[a-z0-9._-]+@[a-z0-9._-]+\.[(com|fr)]+
        while re.search(expression1, self.user_name) is None:
            self.user_name = input("Enter a valid user_name :")
            if self.user_name is not in self._user_name_dico.values():
                return self.user_name
            else:
                self.user_name = "$ user_name already used $"
                print(self.user_name)
        while re.search(expression1, self.password) is None:
            self.password = input("Enter a valid password :")
        while re.search(expression2, self.email) is None:
            self.email = input("enter your email adress")
            if self.email is not in self._email_dico.values():
                return self.email
            else:
                self.email = "$ an account with this email already exist $"
                print(self.email)
#il faut ici traiter le fait qu'on envoie un email de confirmation avec le username et le mot de passe
        user_id = self.id
        user=(self.name, self.email, self.user_name, self.password)
        self._user_name_dico["user_id"] = self.user_name
        self._email_dico["user_id"] = self.email
        self._password_dico["user_id"] = self.password
        self.favorites = {}
        Users._compteur+=1
        
        
    def user_login(self):
        entered_user_name = input("Enter your username")
        entered_password = input("Enter your password")
        for user_id, user_name in self._user_name_dico:
            if user_name == entered_user_name:
                return checked_user_id = user_id
            else:
                return("this user_name doesn't exist")
        for user_id, password in self._password_dico:
            if user_id == checked_user_id and password == entered_password:
                print("the account has been successfully identified")
#Donner ici l'accès au compte, je sais pas trop comment faire...
            else:
                return("You entered the wrong password")
                
#Fonction qui doit intégrer une communication avec le user, format à définir
    def password_reset(self, user.email):
        msg_recu = user.recv(1024)
        msg_recu = msg_recu.decode()
        reset_email = ""
        if msg_recu == "reset_password":
            while reset_email is not in self._email_dico.values():
                reset_email = input("please enter the email address you registered with")
        for user_id, user_email in self._email_dico:
            if user_email == reset_email:
                return user_id as reset_user_id
        for user_id, password in self._password_dico:
            if user_id == reset_user_id:
                return password
        

            
        
        
        
        
        
        
        
        
        
        
        