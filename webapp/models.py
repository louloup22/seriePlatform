from django.db import models
from django.contrib.auth.models import User
import webapp.config as config
import json
import requests
from pandas import DataFrame as df
from datetime import date
import re


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
            dico={}
            url="https://api.themoviedb.org/3/tv/"+str(tv_id[i])+"?api_key="+self.API_KEY+"&language=en-US"
            req =requests.get(url)
            resp=json.loads(req.content)
            print(resp)
            dico["genres"]=resp["genres"]
            if resp['in_production']==False:
                #question pour next air date pas forcément donné par l'API
                dico["next_episode_date"]=None
            else: 
                if resp['next_episode_to_air']==None:
                    dico["next_episode_date"]="Not known"
                    dico["next_episode"]="Not known"
                else:
                    next_air=resp["next_episode_to_air"]["air_date"]
                    liste=list(map(int,re.findall(r'\d+',next_air)))
                    if len(liste)==3:
                        dico["next_episode_date"]=date(liste[0],liste[1],liste[2])
                    season=resp["next_episode_to_air"]["season_number"]
                    episode=resp["next_episode_to_air"]["episode_number"]
                    dico["next_episode"]="{}x{}".format(season,episode)
                    
            
            if resp["last_air_date"]!=None:        
                last_air=resp["last_air_date"]
                liste=list(map(int,re.findall(r'\d+',last_air)))
                if len(liste)==3:
                    dico["last_episode_date"]=date(liste[0],liste[1],liste[2])
                else:
                    dico["last_episode_date"]="Error"
            else:
                dico["last_episode_date"]=None
            
            #last episode
            if dico["last_episode_date"]==None:
                dico["last_episode"]=None
            elif resp["last_episode_to_air"]!=None:
                #should we add id ?
                season=resp["last_episode_to_air"]["season_number"]
                episode=resp["last_episode_to_air"]["episode_number"]
                dico["last_episode"]="{}x{}".format(season,episode)
            else:
                dico["last_episode"]=None
                
        
                
            #name
            dico["name"]=resp["name"]
            
            dico["overview"]=resp["overview"]
            
            dico["nb_episodes"]=resp["number_of_episodes"]
            dico["nb_seasons"]=resp["number_of_seasons"]
            dico['id']=tv_id[i]
            dict_series[dico['id']]=dico
        return dict_series
    
    def _get_attributes_in_dataframe_html(self,tv_id):
        dict_series = {}
        for i in range(len(tv_id)):
            dico={}
            url="https://api.themoviedb.org/3/tv/"+str(tv_id[i])+"?api_key="+self.API_KEY+"&language=en-US"
            req =requests.get(url)
            resp=json.loads(req.content)
            print(resp)
            #name
            dico["name"]=resp["name"]
            dico["overview"]=resp["overview"]
            dico["nb_seasons"]=resp["number_of_seasons"]
            dico["genres"]=resp["genres"]
            
            if resp['in_production']==False:
                #question pour next air date pas forcément donné par l'API
                dico["next_episode_date"]=None
            else: 
                if resp['next_episode_to_air']==None:
                    dico["next_episode_date"]="Not known"
                    dico["next_episode"]="Not known"
                else:
                    next_air=resp["next_episode_to_air"]["air_date"]
                    liste=list(map(int,re.findall(r'\d+',next_air)))
                    if len(liste)==3:
                        dico["next_episode_date"]=date(liste[0],liste[1],liste[2])
                    season=resp["next_episode_to_air"]["season_number"]
                    episode=resp["next_episode_to_air"]["episode_number"]
                    dico["next_episode"]="{}x{}".format(season,episode)
                    
            
            if resp["last_air_date"]!=None:        
                last_air=resp["last_air_date"]
                liste=list(map(int,re.findall(r'\d+',last_air)))
                if len(liste)==3:
                    dico["last_episode_date"]=date(liste[0],liste[1],liste[2])
                else:
                    dico["last_episode_date"]="Error"
            else:
                dico["last_episode_date"]=None
            
            #last episode
            if dico["last_episode_date"]==None:
                dico["last_episode"]=None
            elif resp["last_episode_to_air"]!=None:
                #should we add id ?
                season=resp["last_episode_to_air"]["season_number"]
                episode=resp["last_episode_to_air"]["episode_number"]
                dico["last_episode"]="{}x{}".format(season,episode)
            else:
                dico["last_episode"]=None
            
            #dico['id']=tv_id[i]
            dict_series[tv_id[i]]=dico
            
        dataframe = df.from_dict(dict_series,orient='index')
            #for index,row in dataframe.iterrows():
                #row['name']
            
        #html = dataframe.to_html()
        return dataframe
    
    
    
    
    def _get_attributes_for_serie_in_list(self,tv_id):
        dict_series = []
        for i in range(len(tv_id)):
            dico={}
            url="https://api.themoviedb.org/3/tv/"+str(tv_id[i])+"?api_key="+self.API_KEY+"&language=en-US"
            req =requests.get(url)
            resp=json.loads(req.content)
            print(resp)
            dico["genres"]=resp["genres"]
            if resp['in_production']==False:
                #question pour next air date pas forcément donné par l'API
                dico["next_episode_date"]=None
            else: 
                if resp['next_episode_to_air']==None:
                    dico["next_episode_date"]="Not known"
                    dico["next_episode"]="Not known"
                else:
                    next_air=resp["next_episode_to_air"]["air_date"]
                    liste=list(map(int,re.findall(r'\d+',next_air)))
                    if len(liste)==3:
                        dico["next_episode_date"]=date(liste[0],liste[1],liste[2])
                    season=resp["next_episode_to_air"]["season_number"]
                    episode=resp["next_episode_to_air"]["episode_number"]
                    dico["next_episode"]="{}x{}".format(season,episode)
                    
            
            if resp["last_air_date"]!=None:        
                last_air=resp["last_air_date"]
                liste=list(map(int,re.findall(r'\d+',last_air)))
                if len(liste)==3:
                    dico["last_episode_date"]=date(liste[0],liste[1],liste[2])
                else:
                    dico["last_episode_date"]="Error"
            else:
                dico["last_episode_date"]=None
            
            #last episode
            if dico["last_episode_date"]==None:
                dico["last_episode"]=None
            elif resp["last_episode_to_air"]!=None:
                #should we add id ?
                season=resp["last_episode_to_air"]["season_number"]
                episode=resp["last_episode_to_air"]["episode_number"]
                dico["last_episode"]="{}x{}".format(season,episode)
            else:
                dico["last_episode"]=None
                
        
                
            #name
            dico["name"]=resp["name"]
            
            dico["overview"]=resp["overview"]
            
            dico["nb_episodes"]=resp["number_of_episodes"]
            dico["nb_seasons"]=resp["number_of_seasons"]
            dico['id']=tv_id[i]
            dict_series.append(dico)
        return dict_series
    
    
    



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
    
    class Meta:
        verbose_name = "Série"
        verbose_name_plural= "Séries"
    
    def __str__(self):
        return self.name

    def _get_info_episode_uptodate(self):
        if date.now()>self.next_episode_date:
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
        
    

                





