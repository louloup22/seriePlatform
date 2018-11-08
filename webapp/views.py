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

# class Views(Search, Profil, Serie):
#     def __init__(self):
#         Profil.__init__(self, id, user_id, favorites)
#         Search.__init__(self, API_KEY, query="")
#         Serie.__init__(self, id, name, nb_episodes, nb_seasons, genres, overview, last_episode_date, last_episode, next_episode_date, next_episode, alert, poster_path, seasons, video, video_title, favorites_user)

#     def home(request): 


def notification(request):
    if request.user.is_authenticated: 
        this_user = request.user.profil
        # search_class = Search('hello')
        if this_user.favorites == '[]':
            dict_series = {}
        else:
            dict_soon = {} 
            dict_now = {}       
            for item in this_user.favorites[1:-1].split(','): 
                item = int(item)
                print(item)
                this_serie = Serie.objects.get(id = item)
                if this_serie.alert < 4 and this_serie.alert > 1:
                    dict_soon[item] = this_serie
                elif this_serie.alert < 2:
                    dict_now[item] = this_serie

            nb_soon = len(dict_soon)
            nb_now = len(dict_now)
            nb_total = nb_soon + nb_now
    return nb_total


def home(request):

    dict_seriesT1 = SearchThread(Search.get_tv_airing_today)
    dict_seriesT2 = SearchThread(Search.get_tv_airing_week)
    dict_seriesT1.start()
    dict_seriesT2.start()
    dict_seriesT1.join()
    dict_seriesT2.join()
    dict_series1 = dict_seriesT1.result()
    dict_series2 = dict_seriesT2.result()

    if request.user.is_authenticated: 
        this_user = request.user.profil
        if this_user.favorites == '[]':
            dict_series = {}
        else:
            dict_soon = {} 
            dict_now = {}       
            for item in this_user.favorites[1:-1].split(','): 
                item = int(item)
                print(item)
                this_serie = Serie.objects.get(id = item)
                if this_serie.alert < 4 and this_serie.alert > 1:
                    dict_soon[item] = this_serie
                elif this_serie.alert < 2:
                    dict_now[item] = this_serie

            nb_soon = len(dict_soon)
            nb_now = len(dict_now)
            nb_total = nb_soon + nb_now

    return render(request, 'webapp/home.html',locals())



def signup(request):
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
    else:
        form = SignUpForm()

    if request.user.is_authenticated: 
        this_user = request.user.profil
        if this_user.favorites == '[]':
            dict_series = {}
        else:
            dict_soon = {} 
            dict_now = {}       
            for item in this_user.favorites[1:-1].split(','): 
                item = int(item)
                print(item)
                this_serie = Serie.objects.get(id = item)
                if this_serie.alert < 4 and this_serie.alert > 1:
                    dict_soon[item] = this_serie
                elif this_serie.alert < 2:
                    dict_now[item] = this_serie

            nb_soon = len(dict_soon)
            nb_now = len(dict_now)
            nb_total = nb_soon + nb_now

    return render(request,'webapp/signup.html',locals())

def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            print('/search/' + query)
            envoi = True
            return redirect('/search/' + query + '/1')
    else:
        form = SearchForm()

    # capte l'utilisateur connecté
    this_user = request.user.profil
    if this_user.favorites == '[]':
        dict_series = {}
    else:
        dict_soon = {} 
        dict_now = {}   

        favorite_seriesid= [int(item) for item in this_user.favorites[1:-1].split(',')]
        threads=[]
        for ids in favorite_seriesid:
            update_serie = SearchThread(Search.get_attributes_for_serie, ids)
            update_serie.start()
            threads.append(update_serie)
        for thread in threads:
            thread.join()
        #time.sleep(2)
        dict_series = [thread.result() for thread in threads]
        print(dict_series)

        for el in dict_series:
            if el !=None:
                this_serie = Serie.objects.get(id = el['id'])
                print("1er essai {}".format(this_serie))
                this_serie = this_serie.update_serie(el['nb_episodes'], el['nb_seasons'], el['last_episode_date'],el['last_episode'], el['next_episode_date'], el['next_episode'], el['seasons'], el['video'], el['alert'])
                print("2eme essai {}".format(this_serie))
                this_serie.save()


        for item in favorite_seriesid:
            this_serie = Serie.objects.get(id = item)
            if this_serie.alert < 4 and this_serie.alert > 1:
                dict_soon[item] = this_serie
            elif this_serie.alert < 2:
                dict_now[item] = this_serie

        nb_soon = len(dict_soon)
        nb_now = len(dict_now)
        nb_total = nb_soon + nb_now
       
            
    return render(request, 'webapp/search_result.html', locals())
        

def search_query(request, query, page_number=1):
    form = SearchForm()
    page = page_number
    previous_page = page - 1
    next_page = page + 1
    envoi = True
    

    respT=SearchThread(Search.get_serie_by_name_with_space, query, page)
    number_resultsT=SearchThread(Search.get_number_of_result,query,page)
    number_pagesT=SearchThread(Search.get_number_of_pages, query,page)
    respT.start()
    number_resultsT.start()
    number_pagesT.start()
    respT.join()
    number_resultsT.join()
    number_pagesT.join()
    resp = respT.result()
    number_results = number_resultsT.result()
    number_pages = number_pagesT.result()


    this_user = request.user.profil
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

        nb_soon = len(dict_soon)
        nb_now = len(dict_now)
        nb_total = nb_soon + nb_now


    return render(request, 'webapp/search_result.html', locals())


"""
- récupérer les IDs des séries favories dans la table webapp_profil puis chercher les lignes de ces ids dans la table webapp_serie
"""

def display_favorites(request):
    this_user = request.user.profil

    if this_user.favorites == '[]':
        dict_series = {}
    else:
        favorite_seriesid= [int(item) for item in this_user.favorites[1:-1].split(',')]
        dict_series = {}
        for el in favorite_seriesid : 
            this_serie = Serie.objects.get(id = el)
            dict_series[el] = this_serie.display_favorites()
        dict_soon = {} 
        dict_now = {}       

        for item in favorite_seriesid:
            this_serie = Serie.objects.get(id = item)
            if this_serie.alert < 4 and this_serie.alert > 1:
                dict_soon[item] = this_serie
            elif this_serie.alert < 2:
                dict_now[item] = this_serie

        nb_soon = len(dict_soon)
        nb_now = len(dict_now)
        nb_total = nb_soon + nb_now

        # favorite_seriesid= [int(item) for item in this_user.favorites[1:-1].split(',')]
        # dict_series = search_class._get_attributes_for_serie(favorite_seriesid)    
    return render(request, 'webapp/favorites.html',locals())

def genre(request, genre_id, genre_name, page_number=1):

    name = genre_name
    page = page_number
    previous_page = page_number - 1 
    next_page = page_number + 1

    number_pageT=SearchThread(Search.get_genre_total_page, genre_id)
    dict_seriesT = SearchThread(Search.get_tv_by_genre, genre_id, page)
    number_pageT.start()
    dict_seriesT.start()
    number_pageT.join()
    dict_seriesT.join()
    number_page=number_pageT.result()
    dict_series=dict_seriesT.result()

    this_user = request.user.profil
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

        nb_soon = len(dict_soon)
        nb_now = len(dict_now)
        nb_total = nb_soon + nb_now

    return render(request,'webapp/genre.html',locals())


def serieinfo(request, serie_id):

    serie_infoT=SearchThread(Search.get_attributes_for_serie, serie_id)
    similar_seriesT=SearchThread(Search.get_similar_series, serie_id)
    serie_infoT.start()
    similar_seriesT.start()
    serie_infoT.join()
    similar_seriesT.join()
    serie_info=serie_infoT.result()
    similar_series = similar_seriesT.result()



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

        nb_soon = len(dict_soon)
        nb_now = len(dict_now)
        nb_total = nb_soon + nb_now
    return render(request, 'webapp/serieinfo.html',locals())

def seasoninfo(request, serie_id, season_number):

    season_infoT=SearchThread(Search.get_attributes_for_season, serie_id, season_number)
    season_infoT.start()
    season_infoT.join()
    season_info=season_infoT.result()

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

        nb_soon = len(dict_soon)
        nb_now = len(dict_now)
        nb_total = nb_soon + nb_now
    return render(request, 'webapp/seasoninfo.html',locals())

def trending(request, number_page=1):
    page = number_page
    previous_page = page - 1
    next_page = page + 1

    number_pagesT=SearchThread(Search.get_number_of_trending_page, page)
    dict_seriesT=SearchThread(Search.get_series_trending, page)
    number_pagesT.start()
    dict_seriesT.start()
    number_pagesT.join()
    dict_seriesT.join()
    number_pages = number_pagesT.result()
    dict_series=dict_seriesT.result()

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

        nb_soon = len(dict_soon)
        nb_now = len(dict_now)
        nb_total = nb_soon + nb_now
    return render(request, 'webapp/trending.html',locals())
