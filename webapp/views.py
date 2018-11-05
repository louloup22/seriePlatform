from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate
from webapp.forms import SignUpForm, SearchForm
from webapp.models import Search, Serie, Profil,SearchThread
from pandas import DataFrame as df
import pandas as pd
from django.http import JsonResponse
from django.template.context import RequestContext
import numpy as np


"""
This is a list of different views
""" 

# class Views(Search, Profil, Serie):
#     def __init__(self):
#         Profil.__init__(self, id, user_id, favorites)
#         Search.__init__(self, API_KEY, query="")
#         Serie.__init__(self, id, name, nb_episodes, nb_seasons, genres, overview, last_episode_date, last_episode, next_episode_date, next_episode, alert, poster_path, seasons, video, video_title, favorites_user)

#     def home(request): 


def home(request):
    # search_class = Search('')
    # dict_series1 = search_class._get_tv_airing_today()
    # dict_series2 = search_class._get_tv_airing_week()
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
        # search_class = Search('hello')
        if this_user.favorites == '[]':
            dict_series = Search.get_attributes_for_serie([])
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

            # compter le nombre d'élement dans dict



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


    this_user = request.user.profil
    # search_class = Search('hello')
    if this_user.favorites == '[]':
        dict_series = Search.get_attributes_for_serie([])
    else:
        dict_soon = {} 
        dict_now = {}   

#METTRE DES THREADS !!

        # favorite_seriesid= [int(item) for item in this_user.favorites[1:-1].split(',')]
        # dict_seriesT = SearchThread(Search.get_attributes_for_serie, favorite_seriesid)
        # dict_seriesT.start()
        # dict_seriesT.join()
        # dict_series = dict_seriesT.result()

        for item in this_user.favorites[1:-1].split(','): 
            item = int(item)
            this_serie = Serie.objects.get(id = item)
            update_serie = Search.get_attributes_for_serie_in_list([item])[0]
            # print(update_serie[item])
            this_serie.alert = update_serie['alert']
            this_serie.save()
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
    
    # search_class = Search(query)
    
    # resp = search_class.get_serie_by_name_with_space(query,page=page_number)
    # number_results = search_class.get_number_of_result(query,page=page_number)
    # number_pages = search_class.get_number_of_pages(query,page=page_number)

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
    # search_class = Search('hello')
    if this_user.favorites == '[]':
        dict_series = Search.get_attributes_for_serie([])
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
2 possibilités:
- récupérer les IDs des séries favories dans la table webapp_profil puis chercher les lignes de ces ids dans la table webapp_serie
- dans la table webapp_serie chercher les lignes qui contient le user_id dans la colonne favorites_user
"""

def display_favorites(request):
    this_user = request.user.profil
    # search_class = Search('hello')


    if this_user.favorites == '[]':
        dict_seriesT = SearchThread(Search.get_attributes_for_serie, [])
        dict_seriesT.start()
        dict_seriesT.join()
        dict_series = dict_seriesT.result()
        # dict_series = search_class._get_attributes_for_serie([])
    else:
        favorite_seriesid= [int(item) for item in this_user.favorites[1:-1].split(',')]
        dict_seriesT = SearchThread(Search.get_attributes_for_serie, favorite_seriesid)
        dict_seriesT.start()
        dict_seriesT.join()
        dict_series = dict_seriesT.result()


        # dict_series={}        
        # for item in this_user.favorites[1:-1].split(','): 
        #     item = int(item)
        #     this_serie = Serie.objects.get(id=item)
        #     dict_series[item]=this_serie

    # this_user = request.user.profil
    # search_class = Search('hello')
    # if this_user.favorites == '[]':
    #     dict_series = search_class._get_attributes_for_serie([])
    # else:
        dict_soon = {} 
        dict_now = {}       
        # for item in this_user.favorites[1:-1].split(','): 
        #     item = int(item)
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
    # search_class = Search('')
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


    # number_page = search_class._get_genre_total_page(genre_id)
    # dict_series = search_class._get_tv_by_genre(genre_id,page = page_number)

    this_user = request.user.profil
    # search_class = Search('hello')
    if this_user.favorites == '[]':
        dict_series = Search.get_attributes_for_serie([])
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
    # search_class = Search('')
    # serie_info = search_class._get_attributes_for_serie_in_list([serie_id])[0]
    # similar_series = search_class._get_similar_series(serie_id)

    serie_infoT=SearchThread(Search.get_attributes_for_serie_in_list, [serie_id])
    similar_seriesT=SearchThread(Search.get_similar_series, serie_id)
    serie_infoT.start()
    similar_seriesT.start()
    serie_infoT.join()
    similar_seriesT.join()
    serie_info=serie_infoT.result()[0]
    similar_series = similar_seriesT.result()



    this_user = request.user.profil
    search_class = Search('hello')
    if this_user.favorites == '[]':
        dict_series = search_class.get_attributes_for_serie([])
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
    # search_class = Search('')
    # season_info = search_class._get_attributes_for_season(serie_id,season_number)

    season_infoT=SearchThread(Search.get_attributes_for_season, serie_id, season_number)
    season_infoT.start()
    season_infoT.join()
    season_info=season_infoT.result()

    this_user = request.user.profil
    search_class = Search('hello')
    if this_user.favorites == '[]':
        dict_series = search_class.get_attributes_for_serie([])
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

    # search_class = Search('')
    # number_pages = search_class._get_number_of_trending_page(page = 1)
    # dict_series = search_class._get_series_trending(page = number_page)

    this_user = request.user.profil
    search_class = Search('hello')
    if this_user.favorites == '[]':
        dict_series = search_class.get_attributes_for_serie([])
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
