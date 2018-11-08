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
    to_edit = Profil.objects.get(user_id=user_id)
    # info de la série à partir d'un appel à l'API
    serie = Search.get_attributes_for_serie(id)


    create_serie = Serie(id=id,name=serie['name'],poster_path=serie['poster_path'],alert=serie['alert'],nb_episodes=serie['nb_episodes'],nb_seasons=serie['nb_seasons'],genres=serie['genres'],overview=serie['overview'],last_episode_date=serie['last_episode_date'],last_episode=serie['last_episode'],next_episode_date=serie['next_episode_date'],next_episode=serie['next_episode'],video=serie['video'])
    create_serie.save()
    if type(create_serie.alert) != int:
        create_serie.alert = 999999
        create_serie.save()
    print(create_serie)
    
    create_serie.nb_fav_users += 1
    create_serie.save()
    
    if to_edit.favorites == '[]':
        to_edit.favorites = '[{}]'.format(id)
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
    # Supprimmer l'id de la série dans la liste de favoris de l'utilisateur
    to_edit=Profil.objects.get(user_id=user_id)
    to_edit.remove_favorite(id)

    # Supprimmer la ligne de la série dans la table série SI JAMAIS il n'y a plus d'autres utilisateurs l'ayant en favori
    to_delete = Serie.objects.get(id = id) 
    to_delete.nb_fav_users -= 1
    if to_delete.nb_fav_users == 0 : 
        to_delete.delete()
    
    return JsonResponse({'status':'OK'})
