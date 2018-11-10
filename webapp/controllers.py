# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 01:07:00 2018

@author: t-lopica
"""

from django.shortcuts import render,redirect
from django.http import JsonResponse
from webapp.models import Search, Serie, Profil

#Cette fonction permet d'ajouter des séries favorites pour un utilisateur et d'enregistrer cette donnée dans notre base de données
def add_favorite(request, id, user_id):
    print("this is the id: {0}".format(id))
    print("this is the user_id: {0}".format(user_id))

    # 1. Récupération et formatage de la série
    #On récupère les informations de la série
    serie = Search.get_attributes_for_serie(id)
    #On crée la nouvelle série en ne conservant que les données qui vont être enrigistrées dans notre base
    create_serie=Serie(id=id,name=serie['name'],poster_path=serie['poster_path'],alert=serie['alert'],nb_episodes=serie['nb_episodes'],nb_seasons=serie['nb_seasons'],genres=serie['genres'],overview=serie['overview'],last_episode_date=serie['last_episode_date'],last_episode=serie['last_episode'],next_episode_date=serie['next_episode_date'],next_episode=serie['next_episode'],video=serie['video'])
    #On l'enregistre dans notre base de données
    create_serie.save()
    #On met une valeur par défaut de l'alerte si elle n'existe pas
    if type(create_serie.alert)!=int:
        create_serie.alert=999999
        create_serie.save()

    # 2. Traitement dans la base de données du côté série
    #Si il n'y a pas d'utilisateur qui ont la série comme favoris alors on ajouter l'utilisateur dans la liste des utilisateurs favoris de la série
    if create_serie.favorites_user=='[]':
        create_serie.favorites_user= '[{}]'.format(user_id)
        create_serie.save()
    #Si il existe déjà des utilisateurs qui ont la série en favoris, ajoute notre nouvel utilisateur dans la liste des utlisateurs qui ont la série en favoris (en vérifiant que l'utilisateur n'est pas déjà dans cette liste).
    else:
        create_serie.favorites_user = [int(item) for item in create_serie.favorites_user[1:-1].split(',')]
        if int(id) in create_serie.favorites_user:
            pass
        else:
            create_serie.favorites_user.append(id)
            create_serie.save()

    # 3. Traitement dans la base données du côté utilisateur
    #On récupère le profil de l'utilisateur dans to_edit
    to_edit=Profil.objects.get(user_id=user_id)
    #Si l'utilisateur n'a pas encore de séries favorites, on crée sa liste et on ajoute la série dans ses favoris
    if to_edit.favorites=='[]':
        to_edit.favorites= '[{}]'.format(id)
        to_edit.save()
    #Si l'utilisateur a déjà une liste de favoris dans la base de données, on ajoute simplement l'id de la nouvelle série favorite à cette liste (en vérifiant qu'il n'y est pas déjà).
    else:
        to_edit.favorites = [int(item) for item in to_edit.favorites[1:-1].split(',')]
        if int(id) in to_edit.favorites:
            pass
        else:
            to_edit.favorites.append(id)
            to_edit.save()
            
    return JsonResponse({'status':'OK'})


#Cette fonction permet à l'utilisateur de supprimer une série de sa liste de favoris lorsqu'il clique sur le bouton "remove favorites"
def remove_favorite(request, id, user_id):
    print("this is the id: {0}".format(id))
    print("this is the user_id: {0}".format(user_id))
    
    # 1. Traitement de la modification dans la base de données du côté utilisateur
    #On récupère le profil de l'utilisateur dans to_edit
    to_edit=Profil.objects.get(user_id=user_id)
    #On formate la liste de favoris de l'utilisateur
    to_edit.favorites = [int(item) for item in to_edit.favorites[1:-1].split(',')]
    #On enlève la série 
    to_edit.favorites.remove(id)
    #On enregistre la liste de 
    to_edit.save()
    
    # 2. Traitement de la modification dans la base de données du côté série
    #On récupère la série où on doit faire la modification
    serie_change=Serie.objects.get(id=id)
    #On formate la liste d'utilisateurs favoris de la série
    serie_change.favorites_user=[int(item) for item in serie_change.favorites_user[1:-1].split(',')]
    #On enlève l'utilisateur
    serie_change.favorites_user.remove(user_id)
    #On sauvegarde la nouvelle liste d'utilisateurs favoris
    serie_change.save()

    return JsonResponse({'status':'OK'})
