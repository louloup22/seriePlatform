from django.db import models
from django.contrib.auth.models import User
import webapp.config as config
import json
import requests
from pandas import DataFrame as df
import datetime
import re
import urllib.request

class Search(models.Model):
    API_KEY = models.CharField(default=config.API_KEY, null = False, max_length=500)
    query = models.CharField(null = True, verbose_name = "Search", max_length=400)
    
    def _get_serie_by_name_with_space(self,query):
        query=query.replace(" ","+")
        url="https://api.themoviedb.org/3/search/tv?query="+query+"&api_key="+self.API_KEY+"&language=en-US"
        req =requests.get(url)
        resp=json.loads(req.content)
        #print(resp)
        return resp       
        
    def _get_number_of_result(self,query):
        obj=self._get_serie_by_name_with_space(query)
        print(obj['total_results'])
        return obj['total_results']
    
    def _get_id_from_result(self, query):
        liste_id=[]
        obj=self._get_serie_by_name_with_space(query)
        for i in obj["results"]:
            #print(type(i['id']))
            liste_id.append(i['id'])
        return liste_id
    
    def _get_attributes_for_serie(self,tv_id):
        dict_series = {}
        for i in range(len(tv_id)):
            url="https://api.themoviedb.org/3/tv/"+str(tv_id[i])+"?api_key="+self.API_KEY+"&language=en-US"
            req =requests.get(url)
            resp=json.loads(req.content)
            print(resp)
            serie=Serie(resp)
            dict_series[serie.id]=serie
        return dict_series
    
    def _get_attributes_for_serie_by_list(self,tv_id):
        dict_series = []
        for i in range(len(tv_id)):
            url="https://api.themoviedb.org/3/tv/"+str(tv_id[i])+"?api_key="+self.API_KEY+"&language=en-US"
            req =requests.get(url)
            resp=json.loads(req.content)
            print(resp)
            serie=Serie(resp)
            dict_series.append(serie)
        return dict_series
    
    def _get_attributes_for_season(self,tv_id,season_number):
        url="https://api.themoviedb.org/3/tv/"+str(tv_id)+"/season/"+str(season_number)+"?api_key="+self.API_KEY+"&language=en-US"
        req =requests.get(url)
        resp=json.loads(req.content)
        season_info=Season(resp)
        return season_info
    
    def _get_series_trending(self):
        url="https://api.themoviedb.org/3/tv/popular?api_key="+self.API_KEY+"&language=en-US&page=1"
        req =requests.get(url)
        resp=json.loads(req.content)
        results=resp["results"]
        return results
    
    def _get_similar_series(self,tv_id):
        url="https://api.themoviedb.org/3/tv/"+str(tv_id)+"/recommendations?api_key="+self.API_KEY+"&language=en-US&page=1"
        req =requests.get(url)
        resp=json.loads(req.content)
        results=resp["results"]
        return results
        
    def _get_recent_and_incoming_episodes_by_list(self,tv_id):
        dict_recent_episodes = []
        dict_incoming_episodes = []
        for i in range(len(tv_id)):
            url="https://api.themoviedb.org/3/tv/"+str(tv_id[i])+"?api_key="+self.API_KEY+"&language=en-US"
            req =requests.get(url)
            resp=json.loads(req.content)
            for j in range(len(resp["seasons"])):
                url2="https://api.themoviedb.org/3/tv/"+str(resp["id"])+"/season/"+str(resp["seasons"][j]["season_number"])+"?api_key="+self.API_KEY+"&language=en-US"
                req2 =requests.get(url2)
                resp2=json.loads(req2.content)
                dico_recent_episodes={}
                dico_incoming_episodes={}
                liste_recent_episode=[]
                liste_incoming_episode=[]
                dico_recent_episodes["serie_id"]=resp["id"]
                dico_recent_episodes["serie_name"]=resp["name"]
                dico_recent_episodes["serie_overview"]=resp["overview"]
                dico_recent_episodes["serie_poster_path"]="https://image.tmdb.org/t/p/w500"+resp["poster_path"]
                dico_recent_episodes["serie_nb_episodes"]=resp["number_of_episodes"]
                dico_recent_episodes["serie_nb_seasons"]=resp["number_of_seasons"]
                dico_recent_episodes["season_name"]=resp["seasons"][j]["name"]
                dico_recent_episodes["season_number"]=resp["seasons"][j]["season_number"]
                dico_incoming_episodes["serie_id"]=resp["id"]
                dico_incoming_episodes["serie_name"]=resp["name"]
                dico_incoming_episodes["serie_overview"]=resp["overview"]
                dico_incoming_episodes["serie_poster_path"]="https://image.tmdb.org/t/p/w500"+resp["poster_path"]
                dico_incoming_episodes["serie_nb_episodes"]=resp["number_of_episodes"]
                dico_incoming_episodes["serie_nb_seasons"]=resp["number_of_seasons"]
                dico_incoming_episodes["season_name"]=resp["seasons"][j]["name"]
                dico_incoming_episodes["season_number"]=resp["seasons"][j]["season_number"]
                
                for k in range(len(resp2["episodes"])):
                    dico_recent_episode={}
                    dico_incoming_episode={}
                    if resp2["episodes"][k]["air_date"]==None:
                        diff_jours=100
                    else:
                        diff_jours=(datetime.date(int(resp2["episodes"][k]["air_date"][0:4]),int(resp2["episodes"][k]["air_date"][5:7]),int(resp2["episodes"][k]["air_date"][8:10]))-datetime.date.today()).days
                    if diff_jours>=0 and diff_jours<30:
                        dico_incoming_episode["episode_air_date"]=resp2["episodes"][k]["air_date"]
                        dico_incoming_episode["episode_name"]=resp2["episodes"][k]["name"]
                        dico_incoming_episode["episode_overview"]=resp2["episodes"][k]["overview"]
                        dico_incoming_episode["episode_number"]=resp2["episodes"][k]["episode_number"]
                        liste_incoming_episode.append(dico_incoming_episode)
                    if diff_jours<0 and diff_jours>-30:
                        dico_recent_episode["episode_air_date"]=resp2["episodes"][k]["air_date"]
                        dico_recent_episode["episode_name"]=resp2["episodes"][k]["name"]
                        dico_recent_episode["episode_overview"]=resp2["episodes"][k]["overview"]
                        dico_recent_episode["episode_number"]=resp2["episodes"][k]["episode_number"]
                        liste_recent_episode.append(dico_recent_episode)
                dico_recent_episodes["episodes"]=liste_recent_episode            
                dico_incoming_episodes["episodes"]=liste_incoming_episode
                dict_recent_episodes.append(dico_recent_episodes)
                dict_incoming_episodes.append(dico_incoming_episodes)
            M=[]
            for i in range(len(dict_recent_episodes)):
                if dict_recent_episodes[i]["episodes"]==[]:
                    M=[i]+M
            for j in range(len(M)):
                dict_recent_episodes.pop(M[j])
            N=[]
            for i in range(len(dict_incoming_episodes)):
                if dict_incoming_episodes[i]["episodes"]==[]:
                    N=[i]+N
            for j in range(len(N)):
                dict_incoming_episodes.pop(N[j])
        return dict_recent_episodes,dict_incoming_episodes



#id will be automatically generated by the model
class Serie(models.Model):
    
    
    name = models.CharField(max_length=300, null = False)
    nb_episodes = models.IntegerField(verbose_name = "Total number of episodes")
    nb_seasons = models.IntegerField(verbose_name = "Total number of seasons")
    genres = models.TextField()
    overview = models.TextField(null=True)
    last_episode_date = models.DateTimeField(verbose_name =  "Date of last episode", null = True)
    last_episode = models.CharField(max_length=10, verbose_name = "Last episode", null = True)
    next_episode_date = models.DateTimeField(verbose_name =  "Date of next episode", null = True)
    next_episode = models.CharField(max_length=10, verbose_name = "Next episode", null = True)

    def __init__(self,resp):
        self.id=resp["id"]
        self.name=resp["name"]
        self.genres=resp["genres"]
        if resp['next_episode_to_air']==None:
            self.next_episode_date="Not known"
            self.next_episode="Not known"
        else:
            next_air=resp["next_episode_to_air"]["air_date"]
            liste=list(map(int,re.findall(r'\d+',next_air)))
            if len(liste)==3:
                self.next_episode_date=datetime.date(liste[0],liste[1],liste[2])
                season=resp["next_episode_to_air"]["season_number"]
                episode=resp["next_episode_to_air"]["episode_number"]
                self.next_episode="{}x{}".format(season,episode)
            else:
                self.next_episode_date="Error"
                self.next_episode="Error"
        if resp["last_air_date"]!=None:        
            last_air=resp["last_air_date"]
            liste=list(map(int,re.findall(r'\d+',last_air)))
            if len(liste)==3:
                self.last_episode_date=datetime.date(liste[0],liste[1],liste[2])
            else:
                self.last_episode_date="Error"
        else:
            self.last_episode_date=None
        if resp["last_episode_to_air"]!=None:
            #should we add id ?
            season=resp["last_episode_to_air"]["season_number"]
            episode=resp["last_episode_to_air"]["episode_number"]
            self.last_episode="{}x{}".format(season,episode)
        else:
            self.last_episode=None
        self.overview=resp["overview"]
        self.nb_episodes=resp["number_of_episodes"]
        self.nb_seasons=resp["number_of_seasons"]
        self.seasons=resp["seasons"]
        self.poster_path="https://image.tmdb.org/t/p/w500"+resp["poster_path"]

    class Meta:
        verbose_name = "Série"
        verbose_name_plural= "Séries"
    
    def __str__(self):
        return self.name

    def _get_info_episode_uptodate(self):
        if datetime.date.now()>self.next_episode_date:
            obj_serie=Search._get_serie_by_name_with_space(self.name)
            if len(obj_serie["results"])==1:
                id_serie=obj_serie["results"]["id"]
                dico=Search._get_attributes_for_serie(id_serie)
                self.nb_episodes=dico["nb_episodes"]
                self.nb_seasons=dico["nb_seasons"]
                self.last_episode=dico["last_episode"]
                self.last_episode_date=dico["last_episode_date"]
                self.next_episode=dico["next_episode"]
                self.next_episode_date=dico["next_episode_date"]


class Season(models.Model):
    
    def __init__(self,resp):
        self.name=resp["name"]
        self.overview=resp["overview"]
        self.air_date=resp["air_date"]
        self.episodes=resp["episodes"]


class Profil(models.Model):
    user =  models.OneToOneField(User,on_delete=models.CASCADE) #liaison vers modèle User
    favorites = models.TextField(null=True)
    
    #faire un bouton add favorites qui permet d'appeler cette méthode
    #attention à la forme
    def _add_favorites(self,x):
        self.favorites = json.dumps(x)
    
    
    def _convert_favorites(self):
        liste_favorites = []
        string = json.loads(self.favorites)
        for el in string:
            liste_favorites.append(el)
        #liste
        return liste_favorites
    
    
    def _get_favorites(self):
        # return favorites
        return self._convert_favorites()
    #return json.loads(self.favorites)
    
    #voir methode pour retirer directement dans le json
    def _remove_favorites(self,x):
        new_list = self._convert_favorites().pop(x)
        self.favorites = json.dumps(new_list)
        
        



                





