#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 11:38:03 2018

@author: LouiseP
"""

import config
import json
import requests
from pandas import DataFrame as df
from datetime import date
import re

#Inventaire de toutes les séries
class Inventaire_serie:
    def __init__(self):
        self._dict_series={}
    
    def _add_series(self,dico):
        self._dict_series[dico["id"]]=dico
        
    def _return_dataframe_inventaire(self):
        dataframe=df.from_dict(self._dict_series,orient='index')
        return dataframe
                
                
        
class Serie(Inventaire_serie):
    _compteur=0
    def __init__(self,name,nb_episodes,nb_seasons,genres,overview,last_episode_date,next_episode_date,last_episode,next_episode):
        self.id=Serie._compteur
        self.name=name
        self.nb_episodes=nb_episodes
        self.nb_seasons=nb_seasons
        self.genres=genres
        self.overview=overview
        self.last_episode_date=last_episode_date
        self.next_episode_date=next_episode_date
        self.last_episode=last_episode
        self.next_episode=next_episode
        Serie._compteur+=1
        
    
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
    
    def _get_attributes(self):
        print(self.next_episode_date)
            
            
            

class Search:
    #API_KEY="e403e0e25456da8a7d4727d3139f0d88"
    def __init__(self,API_KEY):
        self.API_KEY=API_KEY
    
    def _get_serie_by_name_with_space(self,query):
        query=query.replace(" ","+")
        url="https://api.themoviedb.org/3/search/tv?query="+query+"&api_key="+self.API_KEY+"&language=en-US"
        req =requests.get(url)
        resp=json.loads(req.content)
        #print(resp)
        return resp
    
    """def _get_series_by_actor(self,query):
        query=query.replace(" ","+")
        url="https://api.themoviedb.org/3/search/person?query="+query+"&api_key="+self.API_KEY+"&language=en-US&page=1&media_type=tv"
        req =requests.get(url)
        resp=json.loads(req.content)
        print(resp)"""        
        
    def _get_number_of_result(self,query):
        obj=self._get_serie_by_name_with_space(query)
        print(obj['total_results'])
        return obj['total_results']
    
    def _get_id_from_result(self,query):
        liste_id=[]
        obj=self._get_serie_by_name_with_space(query)
        for i in obj["results"]:
            #print(type(i['id']))
            liste_id.append(i['id'])
        return liste_id
    
    def _get_attributes_for_serie(self,tv_id):
        dico={}
        url="https://api.themoviedb.org/3/tv/"+str(tv_id)+"?api_key="+self.API_KEY+"&language=en-US"
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
        dico['id']=tv_id
        return dico
        #return resp
        
    

##Attention not up to date !!    

Serie_class=Search(config.API_KEY)
inventaire=Inventaire_serie()


Serie_class._get_number_of_result("Desperate")
liste=Serie_class._get_id_from_result("Desperate")
print(liste)
for el in liste:
    attributes=Serie_class._get_attributes_for_serie(el)
    inventaire._add_series(attributes)

print(inventaire._dict_series)
inventaire._return_dataframe_inventaire().to_csv('CSV/test.csv',sep='\t')


#Ajout=Serie(attributes["name"],attributes["nb_episodes"],attributes["nb_seasons"],attributes["genres"],attributes["overview"],attributes["last_episode_date"],attributes["next_episode_date"],attributes["last_episode"],attributes["next_episode"])
#Ajout._get_attributes()