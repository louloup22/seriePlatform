# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 01:07:00 2018

@author: t-lopica
"""


from django.shortcuts import render,redirect
from django.http import JsonResponse
from webapp.models import Search, Serie, Profil

def add_favorite(request, id, user_id):
    print("this is the id: {0}".format(id))
    print("this is the user_id: {0}".format(user_id))
    to_edit=Profil.objects.get(user_id=user_id)
    search_class = Search('hello')
    serie = search_class._get_attributes_for_serie_in_list([id])[0]
    print('this is the serie {}'.format(serie))
    create_serie=Serie(id=id,name=serie['name'],poster_path=serie['poster_path'],alert=serie['alert'],nb_episodes=serie['nb_episodes'],nb_seasons=serie['nb_seasons'])
    create_serie.save()
    print(create_serie)
    
    if create_serie.favorites_user=='[]':
        create_serie.favorites_user= '[{}]'.format(user_id)
        create_serie.save()
    else:
        create_serie.favorites_user = [int(item) for item in create_serie.favorites_user[1:-1].split(',')]
        print(to_edit)
        if int(id) in create_serie.favorites_user:
            pass
        else:
            create_serie.favorites_user.append(id)
            create_serie.save()
    
    
    if to_edit.favorites=='[]':
        to_edit.favorites= '[{}]'.format(id)
        to_edit.save()
    else:
        to_edit.favorites = [int(item) for item in to_edit.favorites[1:-1].split(',')]
        print(to_edit)
        #si l'id est deja dans les favoris de l'utilisateur
        if int(id) in to_edit.favorites:
            pass
        else:
            to_edit.favorites.append(id)
            to_edit.save()    
            
            
    
    return JsonResponse({'status':'OK'})

def remove_favorite(request, id, user_id):
    print("this is the id: {0}".format(id))
    print("this is the user_id: {0}".format(user_id))
    to_edit=Profil.objects.get(user_id=user_id)
    to_edit.favorites.remove(id)
    to_edit.save()
    
    
    serie_change=Serie.objects.get(id=id)
    serie_change.favorites_user.remove(user_id)
    serie_change.save()
    
    
    
    
    
    
    
    
    return JsonResponse({'status':'OK'})

#def add_to_serie(request,)