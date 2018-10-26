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
    return render(request, 'base.html')


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
            #dict_series = search_class._get_attributes_for_serie(ids)
            #dataframe = df.from_dict(dict_series,orient='index')
            #for index,row in dataframe.iterrows():
                #row['name']
            #html = dataframe.to_html()
            
            dict_series = search_class._get_attributes_for_serie(ids)

            dataframe = df.from_dict(dict_series,orient='index')
            
#            context = {
#                    "profil_list": Profil.objects.all(),
#                    "title": "Profil_List"
#                    }

            html = dataframe.to_html()
            
            #dataframe = search_class._get_attributes_in_dataframe_html(ids)
            #taille=len(dataframe['name'])
            #top=Tkinter.Tk()
            #Tkinter.Button(top,text="Add to Favourites",command=tkMessageBox.showinfo( "Hello Python", "Hello World"))
            #dataframe['button']=pd.Series(np.zeros(taille),index=dataframe.index)
            #html=dataframe.to_html()

            
            #liste=[]
            #for tv_id in ids:
            #    attributes = search_class._get_attributes_for_serie(tv_id)
            #    liste.append(attributes)
            #return redirect('/search')
            envoi = True
        else:
            form = SearchForm()

    return render(request,'webapp/search_result.html',locals())

def add_favorite(request, id, user_id):
    print("this is the id: {0}".format(id))
    print("this is the user_id: {0}".format(user_id))
    to_edit=Profil.objects.get(user_id=user_id)
    if to_edit.favorites=='[]':
        to_edit.favorites= '[{}]'.format(id)
        to_edit.save()
    else:
        to_edit.favorites = [int(item) for item in to_edit.favorites[1:-1].split(',')]
        print(to_edit)
        if int(id) in to_edit.favorites:
            pass
        else:
            to_edit.favorites.append(id)
            to_edit.save()
    
    
    return JsonResponse({'status':'OK'})
#    user = 
#    id = user.get_id
    
def remove_favorite(request, id, user_id):
    print("this is the id: {0}".format(id))
    print("this is the user_id: {0}".format(user_id))
    to_edit=Profil.objects.get(user_id=user_id)
    to_edit.favorites = [int(item) for item in to_edit.favorites[1:-1].split(',')]
    to_edit.favorites.remove(id)
    to_edit.save()
    return JsonResponse({'status':'OK'})


def display_favorites(request):
    this_user=request.user.profil
    favorite_seriesid= [int(item) for item in this_user.favorites[1:-1].split(',')]
    search_class = Search('hello')
    dict_series = search_class._get_attributes_for_serie(favorite_seriesid)

    
    dataframe = search_class._get_attributes_in_dataframe_html(favorite_seriesid)
    html = dataframe.to_html()
#    liste_dico_serie=[]
#    for id in favorite_seriesid:
#        search_class = Search('')
#        dict_series = search_class._get_attributes_for_serie(id)
#        liste_dico_serie.append(dict_series)
    return render(request, 'webapp/favorites.html',locals())

def serieinfo(request,serie_id):
    search_class = Search('')
    serie_info = search_class._get_attributes_for_serie_in_list([serie_id])[0]
    similar_series = search_class._get_similar_series(serie_id)
    return render(request, 'webapp/serieinfo.html',locals())

def seasoninfo(request,serie_id,season_number):
    search_class = Search('')
    season_info = search_class._get_attributes_for_season(serie_id,season_number)
    return render(request, 'webapp/seasoninfo.html',locals())

def trending(request):
    search_class = Search('')
    ids = search_class._get_series_trending_id()
    dict_series = search_class._get_attributes_for_serie(ids)
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


        
            
            
