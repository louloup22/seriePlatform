from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate
from webapp.forms import SignUpForm, SearchForm
from webapp.models import Search, Serie
from pandas import DataFrame as df
import datetime

def home(request):
    return render(request, 'base.html')



def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username = username, password = password)
            login(request,user)
            return redirect('/search')
        else:
            form = SignUpForm()
    
    return render(request,'webapp/signup.html',locals())

def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data.get('query')
            search_class = Search(query)
            resp = search_class._get_serie_by_name_with_space(query)
            number_results = search_class._get_number_of_result(query)
            #liste des ids
            ids = search_class._get_id_from_result(query)
            
            #verif que ca peut marcher
            dict_series = search_class._get_attributes_for_serie(ids)
            dataframe = df.from_dict(dict_series,orient='index')
            html = dataframe.to_html()
            
            
            #liste=[]
            #for tv_id in ids:
            #    attributes = search_class._get_attributes_for_serie(tv_id)
            #    liste.append(attributes)
            #return redirect('/search')
            envoi = True
        else:
            form = SearchForm()

    return render(request,'webapp/search_result.html',locals())


def favorites(request):
    favorite_seriesid=[71446,66732]
    search_class = Search('')
    dict_series = search_class._get_attributes_for_serie_by_list(favorite_seriesid)
    return render(request, 'webapp/favorites.html',locals())

def serieinfo(request,serie_id):
    search_class = Search('')
    serie_info = search_class._get_attributes_for_serie_by_list([serie_id])[0]
    similar_series = search_class._get_similar_series(serie_id)
    return render(request, 'webapp/serieinfo.html',locals())

def seasoninfo(request,serie_id,season_number):
    search_class = Search('')
    season_info = search_class._get_attributes_for_season(serie_id,season_number)
    return render(request, 'webapp/seasoninfo.html',locals())

def trending(request):
    search_class = Search('')
    results = search_class._get_series_trending()
    return render(request, 'webapp/trending.html',locals())
        
def profile(request):
    search_class = Search('')
    favorite_seriesid=[71446,66732,61056]
    results = search_class._get_recent_and_incoming_episodes_by_list(favorite_seriesid)
    results_trending = search_class._get_series_trending()
    incoming_episodes=results[1]
    recent_episodes=results[0]
    return render(request, 'webapp/profile.html',locals())
            
