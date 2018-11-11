from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate
from webapp.forms import SignUpForm, SearchForm
from webapp.models import Search, Serie, Profil,SearchThread
from pandas import DataFrame as df
import pandas as pd
from django.http import JsonResponse
from django.template.context import RequestContext
import numpy as np
import time

"""
This is a list of different views
"""

#IMPORTANT
#Sur cette page nous détaillons les différentes actions lancées lorsque l'utilisateur se positionne sur une page
#Chaque définition détaille les actions de la page concernée
#Toutes ces définitions sont enregistrées dans la même classe: Views
#IMPORTANT
#Seule la page login n'est pas détaillée puisque sa gestion est prise en charge directement par le module django

class Views():

    #Cette fonction permet de lancer les actions pour afficher la page home
    #Cette page s'affiche quand l'utilisateur clique sur Home dans la barre de navigation
    def home(request):
        #On lance les threads pour récupérer les séries qui sortent le jour même ou dans la semaine
        #On pourra ensuite les afficher (cf HTML)
        try:
            dict_seriesT1 = SearchThread(Search.get_tv_airing_today)
            dict_seriesT2 = SearchThread(Search.get_tv_airing_week)
            dict_seriesT1.start()
            dict_seriesT2.start()
            dict_seriesT1.join()
            dict_seriesT2.join()
            dict_series1 = dict_seriesT1.result()
            dict_series2 = dict_seriesT2.result()
        #Si problème dans l'exécution des threads, nous renvoyons des dictionnaires vides
        except:
            dict_series1 = []
            dict_series2 = []

        #Gestion des notifications: création de dictionnaires contenant les séries favorites de l'utilisateur
        #qui sortent le jour-même (dict_now) ou dans un délai de 4 jours (dict_soon).
        #Puis calcul du nombre total
        try:
            if request.user.is_authenticated:
                #On capte l'utilisateur
                this_user = request.user.profil
                if this_user.favorites == '[]':
                    dict_soon = {}
                    dict_now = {}
                else:
                    dict_soon = {}
                    dict_now = {}
                    for item in this_user.favorites[1:-1].split(','):
                        item = int(item)
                        this_serie = Serie.objects.get(id = item)
                        if this_serie.alert < 4 and this_serie.alert > 1:
                            dict_soon[item] = this_serie
                        elif this_serie.alert < 2:
                            dict_now[item] = this_serie
                    nb_soon = len(dict_soon)
                    nb_now = len(dict_now)
                    nb_total = nb_soon + nb_now
        #Si erreur dans les notifications:
        except:
            dict_soon = {}
            dict_now = {}

        #On redirige les éléments calculés vers le modèle html qui va l'afficher (cf code HTML)
        return render(request, 'webapp/home.html',locals())


    #Cette fonction permet de lancer les actions pour afficher la page signup
    #Cette page s'affiche lorsque l'utilisateur clique sur signup situé dans la barre de navigation lorsqu'il arrive sur le site
    def signup(request):
        #Enregistrement du formulaire rempli par l'ulisateur et connection automatique si le formulaire est valide.
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                user = form.save()
                user.refresh_from_db()
                user.save()
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password1')
                user = authenticate(username = username, password = password)
                login(request,user)
                return redirect('/')
        #Redirection sur le questionnaire s'il y a une erreur dans les éléments entrés par l'utilisateur
        else:
            form = SignUpForm()

        #Gestion des notifications: idem que précédemment
        try:
            if request.user.is_authenticated:
                #On capte l'utilisateur
                this_user = request.user.profil
                if this_user.favorites == '[]':
                    dict_soon = {}
                    dict_now = {}
                else:
                    dict_soon = {}
                    dict_now = {}
                    for item in this_user.favorites[1:-1].split(','):
                        item = int(item)
                        this_serie = Serie.objects.get(id = item)
                        if this_serie.alert < 4 and this_serie.alert > 1:
                            dict_soon[item] = this_serie
                        elif this_serie.alert < 2:
                            dict_now[item] = this_serie
                    nb_soon = len(dict_soon)
                    nb_now = len(dict_now)
                    nb_total = nb_soon + nb_now
        except:
            dict_soon = {}
            dict_now = {}

        #On redirige les éléments calculés vers le modèle html qui va l'afficher (cf code HTML)
        return render(request,'webapp/signup.html',locals())


    #Cette fonction permet de lancer les actions pour afficher la page search (au moment où l'utilisateur clique dessus)
    #Cette page est la page qui s'affiche par défaut quand l'utilisateur se connecte
    #Elle peut également s'afficher lorsque l'utilisateur clique sur Search dans la barre de navigation
    def search(request):
        #On s'assure de la validité de la recherche entrée sinon on renvoie le formulaire de recherche
        if request.method == 'POST':
            form = SearchForm(request.POST)
            if form.is_valid():
                query = form.cleaned_data.get('query')
                print('/search/' + query)
                envoi = True
                return redirect('/search/' + query + '/1')
        else:
            form = SearchForm()

        #Lorsque l'utilisateur se connecte, il est directement redirigé sur la page search.
        #Nous mettons alors à jour ses séries favorites
        #Tout d'abord nous récupérons le profil de l'utilisateur avec this_user
        this_user = request.user.profil
        #S'il n'a pas de séries favorites rien n'est mis à jour
        if this_user.favorites == '[]':
            dict_series = {}
        #Sinon nous traitons à la fois la mise à jour des informations sur ses séries favorites et les notifications
        else:
            #Nous récupérons au bon format (nombre) les ids des séries favorites de l'utilisateur
            favorite_seriesid = [int(item) for item in this_user.favorites[1:-1].split(',')]
            #Nous créons une liste qui va contenir nos threads lancés pour chaque ids
            threads = []
            #Pour chaque ids, nous créons un thread qui va récupérer les informations de l'épisode avec un appel à l'API
            #Puis nous lançons le thread et l'enregistrons dans threads
            for ids in favorite_seriesid:
                update_serie = SearchThread(Search.get_attributes_for_serie, ids)
                update_serie.start()
                threads.append(update_serie)
            #Nous attendons que tous les threads se soient exécutés
            for thread in threads:
                thread.join()
            #Nous récupérons tous les résultats des threads dans dict_séries qui contient toutes les informations actualisées des séries favorites de l'utilisateur
            dict_series = [thread.result() for thread in threads]
            print(dict_series)
            #Nous actualisons ensuite notre base de donnée en faisant appel à update_serie
            for el in dict_series:
                if el !=None:
                    this_serie = Serie.objects.get(id = el['id'])
                    this_serie = this_serie.update_serie(el['nb_episodes'], el['nb_seasons'], el['last_episode_date'],el['last_episode'], el['next_episode_date'], el['next_episode'], el['seasons'], el['video'], el['alert'])
                    this_serie.save()

            #Gestion des notifications: idem
            try:
                dict_soon = {}
                dict_now = {}
                for item in favorite_seriesid:
                    this_serie = Serie.objects.get(id = item)
                    if this_serie.alert < 4 and this_serie.alert > 1:
                        dict_soon[item] = this_serie
                    elif this_serie.alert < 2:
                        dict_now[item] = this_serie
            except:
                dict_soon = {}
                dict_now = {}
            nb_soon = len(dict_soon)
            nb_now = len(dict_now)
            nb_total = nb_soon + nb_now

        #On redirige les éléments calculés vers le modèle html qui va l'afficher (cf code HTML)
        return render(request, 'webapp/search_result.html', locals())


    #Cette fonction permet de lancer les actions pour afficher la page des résultats d'une recherche
    #Cette page s'affiche une fois que l'utilisateur a entré sa recherche et cliqué sur le bouton Search sur la page de recherche
    def search_query(request, query, page_number=1):
        #Nous allons dans cette fonction lancer les méthodes pour obtenir les résultats
        #de la recherche d'un utilisateur pour pouvoir les afficher selon le nombre de pages
        form = SearchForm()
        page = page_number
        previous_page = page - 1
        next_page = page + 1
        envoi = True
        try:
            #Création des threads :
            # 1) Trouver les séries liés à la recheche
            # 2) Trouver le nombre total de résultats de la recherche
            # 3) Trouver le nombre de pages de la recherche
            respT=SearchThread(Search.get_serie_by_name_with_space, query, page)
            number_resultsT=SearchThread(Search.get_number_of_result,query,page)
            number_pagesT=SearchThread(Search.get_number_of_pages, query,page)
            #Lancement des threads
            respT.start()
            number_resultsT.start()
            number_pagesT.start()
            #Attente jusqu'à la fin de l'exécution de tous les threads
            respT.join()
            number_resultsT.join()
            number_pagesT.join()
            #Récupération des résultats des threads
            resp = respT.result()
            number_results = number_resultsT.result()
            number_pages = number_pagesT.result()

        #Si il y a une erreur dans la recherche : exception, on renvoie la page d'erreur
        except:
            error_message="The search did not succeed."
            return render(request, 'webapp/error.html',locals())

        #Gestion des favoris: idem
        try:
            this_user = request.user.profil
            if this_user.favorites == '[]':
                dict_soon = {}
                dict_now = {}
            else:
                dict_soon = {}
                dict_now = {}
                for item in this_user.favorites[1:-1].split(','):
                    item = int(item)
                    this_serie = Serie.objects.get(id = item)
                    if this_serie.alert < 4 and this_serie.alert > 1:
                        dict_soon[item] = this_serie
                    elif this_serie.alert < 2:
                        dict_now[item] = this_serie
        except:
            dict_soon = {}
            dict_now = {}
        nb_soon = len(dict_soon)
        nb_now = len(dict_now)
        nb_total = nb_soon + nb_now

        #On redirige les éléments calculés vers le modèle html qui va l'afficher (cf code HTML)
        return render(request, 'webapp/search_result.html', locals())


    #Cette fonction permet de lancer les actions menant à l'affichage de la page Favorites
    #Cette page s'affiche quand l'utilisateur clique sur Favorites dans l'onglet de navigation
    def display_favorites(request):
        try:
            #On capte notre utilisateur
            this_user = request.user.profil
            if this_user.favorites == '[]':
                dict_series = {}
            #Si l'utilisateur a des séries favorites
            else:
                favorite_seriesid= [int(item) for item in this_user.favorites[1:-1].split(',')]
                dict_series = {}
                #On enregistre dans dict_series toutes les informations nécessaires à l'affichage
                for el in favorite_seriesid :
                    this_serie = Serie.objects.get(id = el)
                    dict_series[el] = this_serie.display_favorites()

                #Gestion des notifications : idem
                try:
                    dict_soon = {}
                    dict_now = {}
                    for item in favorite_seriesid:
                        this_serie = Serie.objects.get(id = item)
                        if this_serie.alert < 4 and this_serie.alert > 1:
                            dict_soon[item] = this_serie
                        elif this_serie.alert < 2:
                            dict_now[item] = this_serie
                except:
                    dict_soon = {}
                    dict_now = {}
                nb_soon = len(dict_soon)
                nb_now = len(dict_now)
                nb_total = nb_soon + nb_now

        #Exception si erreur dans la récupération des favoris: on retourne la page d'erreur
        except:
            error_message="Could not load your favorite shows."
            return render(request, 'webapp/error.html',locals())

        #On redirige les éléments calculés vers le modèle html qui va l'afficher (cf code HTML)
        return render(request, 'webapp/favorites.html',locals())


    #Cette fonction permet de lancer les opérations nécessaires au chargement des séries du même genre
    #Cette page s'affiche quand l'utilisateur clique sur le nom d'un genre sur une page d'information d'une série
    def genre(request, genre_id, genre_name, page_number=1):
        name = genre_name
        page = page_number
        previous_page = page_number - 1
        next_page = page_number + 1

        try:
            #On crée les threads en utilisants les méthodes de Search puis on les lance
            number_pageT=SearchThread(Search.get_genre_total_page, genre_id)
            dict_seriesT = SearchThread(Search.get_tv_by_genre, genre_id, page)
            number_pageT.start()
            dict_seriesT.start()
            #Attente de la fin des threads puis récupération des résultats
            number_pageT.join()
            dict_seriesT.join()
            number_page=number_pageT.result()
            dict_series=dict_seriesT.result()

            #Gestion des notifications: idem
            try:
                this_user = request.user.profil
                if this_user.favorites == '[]':
                    dict_soon = {}
                    dict_now = {}
                else:
                    dict_soon = {}
                    dict_now = {}
                    for item in this_user.favorites[1:-1].split(','):
                        item = int(item)
                        this_serie = Serie.objects.get(id = item)
                        if this_serie.alert < 4 and this_serie.alert > 1:
                            dict_soon[item] = this_serie
                        elif this_serie.alert < 2:
                            dict_now[item] = this_serie
            except:
                dict_soon = {}
                dict_now = {}
            nb_soon = len(dict_soon)
            nb_now = len(dict_now)
            nb_total = nb_soon + nb_now

        #Si erreur dans la récupération des séries du même genre, on renvoie la page d'erreur
        except:
            error_message="The search did not succeed."
            return render(request, 'webapp/error.html',locals())

        #On redirige les éléments calculés vers le modèle html qui va l'afficher (cf code HTML)
        return render(request,'webapp/genre.html',locals())


    #Cette fonction permet de lancer les opérations nécessaires à l'affichage de la page info d'une série
    #Cette page s'affiche quand l'utilisateur clique sur le poster d'une série
    def serieinfo(request, serie_id):
        #Construction et lancement des threads selon les méthodes de Search et récupération des résulats
        try:
            serie_infoT=SearchThread(Search.get_attributes_for_serie, serie_id)
            similar_seriesT=SearchThread(Search.get_similar_series, serie_id)
            serie_infoT.start()
            similar_seriesT.start()
            serie_infoT.join()
            similar_seriesT.join()
            serie_info=serie_infoT.result()
            similar_series = similar_seriesT.result()

        #Si on arrive pas à récupérer les informations de la séries, on renvoie une page d'erreur
        except:
            error_message="The show info could not be reached."
            return render(request, 'webapp/error.html',locals())

        #Gestion des utilisateurs : idem
        try:
            this_user = request.user.profil
            if this_user.favorites == '[]':
                dict_soon = {}
                dict_now = {}
            else:
                dict_soon = {}
                dict_now = {}
                for item in this_user.favorites[1:-1].split(','):
                    item = int(item)
                    this_serie = Serie.objects.get(id = item)
                    if this_serie.alert < 4 and this_serie.alert > 1:
                        dict_soon[item] = this_serie
                    elif this_serie.alert < 2:
                        dict_now[item] = this_serie
        except:
            dict_soon = {}
            dict_now = {}
        nb_soon = len(dict_soon)
        nb_now = len(dict_now)
        nb_total = nb_soon + nb_now

        #On redirige les éléments calculés vers le modèle html qui va l'afficher (cf code HTML)
        return render(request, 'webapp/serieinfo.html',locals())


    #Cette fonction permet de lancer les opérations nécessaires à l'affichage de la page info d'une saison
    #Cette page s'affiche quand l'utilisateur clique sur le numéro de la saison depuis la page d'information de la série
    def seasoninfo(request, serie_id, season_number):
        #Gestion des pages
        id = serie_id
        page = season_number
        previous_page = season_number - 1
        next_page = season_number + 1
        nb_seasons = nb_seasons

        #Threading pour récupérer les résultats nécessaires grâce aux méthodes du module Search
        try:
            season_infoT=SearchThread(Search.get_attributes_for_season, serie_id, season_number)
            season_infoT.start()
            season_infoT.join()
            season_info=season_infoT.result()

        #Si on arrive pas à récupérer les informations sur la saison, on renvoie une page d'erreur
        except:
            error_message="The season info could not be reached."
            return render(request, 'webapp/error.html',locals())

        #Gestion des notifications: idem
        try:
            this_user = request.user.profil
            search_class = Search('hello')
            if this_user.favorites == '[]':
                dict_series = {}
            else:
                dict_soon = {}
                dict_now = {}
                for item in this_user.favorites[1:-1].split(','):
                    item = int(item)
                    this_serie = Serie.objects.get(id = item)
                    if this_serie.alert < 4 and this_serie.alert > 1:
                        dict_soon[item] = this_serie
                    elif this_serie.alert < 2:
                        dict_now[item] = this_serie
        except:
            dict_soon = {}
            dict_now = {}
        nb_soon = len(dict_soon)
        nb_now = len(dict_now)
        nb_total = nb_soon + nb_now

        #On redirige les éléments calculés vers le modèle html qui va l'afficher (cf code HTML)
        return render(request, 'webapp/seasoninfo.html',locals())


    #Cette fonction permet de lancer les opérations nécessaire à l'affichage de la page trending
    #Cette page s'affiche quand l'utilisateur clique sur Trending dans la barre de navigation
    def trending(request, number_page=1):
        try:
            page = number_page
            previous_page = page - 1
            next_page = page + 1
            #Threading pour récupérer les résultats nécessaires grâce aux méthodes du module Search
            number_pagesT=SearchThread(Search.get_number_of_trending_page, page)
            dict_seriesT=SearchThread(Search.get_series_trending, page)
            number_pagesT.start()
            dict_seriesT.start()
            number_pagesT.join()
            dict_seriesT.join()
            number_pages = number_pagesT.result()
            dict_series=dict_seriesT.result()

        #Si on arrive pas à récupréer les séries du moment, on renvoie une page d'erreur
        except:
            error_message="Could not get trending TV shows."
            return render(request, 'webapp/error.html',locals())

        #Gestion des notifications: idem
        try:
            this_user = request.user.profil
            search_class = Search('hello')
            if this_user.favorites == '[]':
                dict_soon = {}
                dict_now = {}
            else:
                dict_soon = {}
                dict_now = {}
                for item in this_user.favorites[1:-1].split(','):
                    item = int(item)
                    this_serie = Serie.objects.get(id = item)
                    if this_serie.alert < 4 and this_serie.alert > 1:
                        dict_soon[item] = this_serie
                    elif this_serie.alert < 2:
                        dict_now[item] = this_serie

        except:
            dict_soon = {}
            dict_now = {}
        nb_soon = len(dict_soon)
        nb_now = len(dict_now)
        nb_total = nb_soon + nb_now

        #On redirige les éléments calculés vers le modèle html qui va l'afficher (cf code HTML)
        return render(request, 'webapp/trending.html',locals())
