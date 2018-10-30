from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate
from webapp.forms import SignUpForm, SearchForm
from webapp.models import Search, Serie, Profil
from pandas import DataFrame as df
import pandas as pd
from django.http import JsonResponse
from django.template.context import RequestContext
import numpy as np




def home(request):
    search_class = Search('')
    #number_pages=search_class._get_number_of_trending_page(page=1)
    dict_series1 = search_class._get_tv_airing_today()
    dict_series2 = search_class._get_tv_airing_week()
    return render(request, 'webapp/home.html',locals())



def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user=form.save()
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
            print('/search/'+query)
            envoi = True
            return redirect('/search/'+query+'/1')
    else:
        form = SearchForm()
            
    return render(request,'webapp/search_result.html',locals())
        

def search_query(request,query,page_number=1):
    form = SearchForm()
    page=page_number
    previous_page=page-1
    next_page=page+1
    envoi = True
    
    search_class = Search(query)
    
    #on s'occupe de la page 1
    #page=1
    resp = search_class._get_serie_by_name_with_space(query,page=page_number)
    number_results = search_class._get_number_of_result(query,page=page_number)
    number_pages = search_class._get_number_of_pages(query,page=page_number)
#    dict_series = search_class._get_info_from_result(query,page=page_number)
#    while page<number_pages:
#            page+=1
#            resp = search_class._get_serie_by_name_with_space(query,page=page)
#            dict_series = {**dict_series,**search_class._get_info_from_result(query,page=page)}
#    if request.method == 'POST':
#        form = SearchForm(request.POST)

    return render(request,'webapp/search_result.html',locals())






def display_favorites(request):
    this_user=request.user.profil
    search_class = Search('hello')
    if this_user.favorites=='[]':
        dict_series = search_class._get_attributes_for_serie([])
    else:        
        favorite_seriesid= [int(item) for item in this_user.favorites[1:-1].split(',')]
        dict_series = search_class._get_attributes_for_serie(favorite_seriesid)    
    return render(request, 'webapp/favorites.html',locals())

def genre(request,genre_id,genre_name,page_number=1):
    search_class = Search('')
    name=genre_name
    page=page_number
    previous_page=page_number-1
    next_page=page_number+1
    number_page=search_class._get_genre_total_page(genre_id)
    dict_series = search_class._get_tv_by_genre(genre_id,page=page_number)
    return render(request,'webapp/genre.html',locals())


def serieinfo(request,serie_id):
    search_class = Search('')
    serie_info = search_class._get_attributes_for_serie_in_list([serie_id])[0]
    similar_series = search_class._get_similar_series(serie_id)
#    similar_series= search_class._get_attributes_for_serie(ids)
    return render(request, 'webapp/serieinfo.html',locals())

def seasoninfo(request,serie_id,season_number):
    search_class = Search('')
    season_info = search_class._get_attributes_for_season(serie_id,season_number)
    return render(request, 'webapp/seasoninfo.html',locals())

def trending(request,number_page=1):
    page=number_page
    previous_page=page-1
    next_page=page+1
    search_class = Search('')
    number_pages=search_class._get_number_of_trending_page(page=1)
    dict_series = search_class._get_series_trending(page=number_page)
    return render(request, 'webapp/trending.html',locals())

def profile(request):
    search_class = Search('')
    favorite_seriesid=[71446,66732]
    results = search_class._get_episodes_in_list(favorite_seriesid)
    #results = search_class._get_attributes_for_serie(favorite_seriesid)
    incoming_episodes=[]
    recent_episodes=[]
    #for i in range(len(results)):
    #    if datetime.date(int(results[i]["episode_air_date"][0:4]),int(results[i]["episode_air_date"][5:7]),int(results[i]["episode_air_date"][8:10])-datetime.date.today():
            
    return render(request, 'webapp/trending.html',locals())


        
            
            
