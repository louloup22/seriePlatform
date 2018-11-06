from django.db import models
from django.contrib.auth.models import User
import webapp.config as config
import json
import requests
from pandas import DataFrame as df
from datetime import date
import re
from django.db.models.signals import post_save
from django.dispatch import receiver
#import tkinter
#import tkMessageBox


class Search(models.Model):
    API_KEY = models.CharField(default=config.API_KEY, null = False, max_length=500)
    query = models.CharField(null = True, verbose_name = "Search", max_length=400)
    
    def _get_serie_by_name_with_space(self,query,page=1):
        #20 results by page
        query=query.replace(" ","+")
        url="https://api.themoviedb.org/3/search/tv?query="+query+"&api_key="+self.API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        results=resp["results"]
        #print(resp)
        return results       
        
    def _get_number_of_result(self,query,page=1):
        url="https://api.themoviedb.org/3/search/tv?query="+query+"&api_key="+self.API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        print(resp['total_results'])
        return resp['total_results']
    
    def _get_number_of_pages(self,query,page=1):
        url="https://api.themoviedb.org/3/search/tv?query="+query+"&api_key="+self.API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        print(resp['total_pages'])
        return resp['total_pages']
    
    
    def _get_info_from_result(self, query,page=1):
        dict_series={}
        obj=self._get_serie_by_name_with_space(query,page)
        for i in obj["results"]:
            dico={}
#            print(i)

            dico['id']=i['id']
            if i["poster_path"]!=None:
                    dico["poster_path"]="https://image.tmdb.org/t/p/w500"+i["poster_path"]
            else:
                dico["poster_path"]="https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"
            dico['name']=i['name']
            dict_series[dico['id']]=dico
        #print(len(dict_series))
        return dict_series
    
    def _get_id_from_result(self, query,page=1):
        liste_id=[]
        obj=self._get_serie_by_name_with_space(query,page)
        for i in obj["results"]:
            #print(type(i['id']))
            liste_id.append(i['id'])
        print(len(liste_id))
        return liste_id
    
    def _get_attributes_for_serie(self,tv_id):
        number_ids=len(tv_id)
        print(number_ids)
        #il y a 20 ids par pages
        number_page=number_ids//20
        if number_ids%20!=0:
            number_page+=1
        print(number_page)
        
        dict_series = {}
        
        page=1
        if number_page==1:
            print("il n'y a qu'une page")
            for i in range(number_ids):
                dico={}
                url="https://api.themoviedb.org/3/tv/"+str(tv_id[i])+"?api_key="+self.API_KEY+"&language=en-US"
                req =requests.get(url)
                resp=json.loads(req.content)
                try:
                    dico["genres"]=resp["genres"]
                except:
                    continue
                dico["genres"]=resp["genres"]
                if resp['in_production']==False:
                    #question pour next air date pas forcément donné par l'API
                    dico["next_episode_date"]=None
                else: 
                    if resp['next_episode_to_air']==None:
                        dico["next_episode_date"]=None
                        dico["next_episode"]=None
                    else:
                        next_air=resp["next_episode_to_air"]["air_date"]
                        liste=list(map(int,re.findall(r'\d+',next_air)))
                        if len(liste)==3:
                            dico["next_episode_date"]=date(liste[0],liste[1],liste[2])
                        season=resp["next_episode_to_air"]["season_number"]
                        episode=resp["next_episode_to_air"]["episode_number"]
                        dico["next_episode"]="{}x{}".format(season,episode)
                        
                
                today= date.today()
                if  dico["next_episode_date"]!=None:
                    dico["alert"]=dico["next_episode_date"]-today
                else:
                    dico['alert']=None
                
                
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
                if resp["poster_path"]!=None:
                    dico["poster_path"]="https://image.tmdb.org/t/p/w500"+resp["poster_path"]
                else:
                    dico["poster_path"]="https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"
                dico['id']=tv_id[i]
                dict_series[dico['id']]=dico
        
        #plus de 20 résultats pour la recherche
        else:
            print("il y a plus d'une page")
            while page <number_page:
                if page==2:
                    print("j'en suis à la 2eme page")
                for i in range((page-1)*20,page*20):
    #        for i in range(len(tv_id)):
                    dico={}
                    url="https://api.themoviedb.org/3/tv/"+str(tv_id[i])+"?api_key="+self.API_KEY+"&language=en-US&page="+str(page)
                    req =requests.get(url)
                    resp=json.loads(req.content)
                    try:
                        dico["genres"]=resp["genres"]
                    except:
                        continue
        #            print(resp)
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
                    if resp["poster_path"]!=None:
                        dico["poster_path"]="https://image.tmdb.org/t/p/w500"+resp["poster_path"]
                    else:
                        dico["poster_path"]="https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"
                    dico['id']=tv_id[i]
                    dict_series[dico['id']]=dico
                    
                page+=1
                
            for i in range((page-1)*20,number_ids):
                dico={}
                url="https://api.themoviedb.org/3/tv/"+str(tv_id[i])+"?api_key="+self.API_KEY+"&language=en-US&page="+str(page)
                req =requests.get(url)
                resp=json.loads(req.content)
                try:
                    dico["genres"]=resp["genres"]
                except:
                    continue
    #            print(resp)
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
                if resp["poster_path"]!=None:
                    dico["poster_path"]="https://image.tmdb.org/t/p/w500"+resp["poster_path"]
                else:
                    dico["poster_path"]="https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"
                dico['id']=tv_id[i]
                dict_series[dico['id']]=dico
        return dict_series
    
    
    
    def _get_attributes_for_serie_in_list(self,tv_id):
        dict_series = []
        for i in range(len(tv_id)):
            dico={}
            url="https://api.themoviedb.org/3/tv/"+str(tv_id[i])+"?api_key="+self.API_KEY+"&language=en-US"
            url_video="https://api.themoviedb.org/3/tv/"+str(tv_id[i])+"/videos?api_key="+self.API_KEY+"&language=en-US"
            req =requests.get(url)
            resp=json.loads(req.content)
            reqvideo=requests.get(url_video)
            video_resp=json.loads(reqvideo.content)
            check_video_result=True
            try:
                dico["genres"]=resp["genres"]
            except:
                continue
            try:
                video_resp=video_resp['results']
            except:
                check_video_result=False
            
            #print(resp)
            if video_resp!=[] and check_video_result==True:
                print("video en vue")
                #on prend la première video de la liste par défaut
                video_resp=video_resp[0]
                print(video_resp['site'])
                if video_resp['site']=="YouTube":
                    dico['video']="https://www.youtube.com/embed/"+video_resp['key']+"?autoplay=1"
                    dico['video_title']=video_resp['name']
                    print(dico['video'])
                else:
                    print("pas youtube")
                    dico['video']=None
                    dico['video_title']=None
            else:
                print("pas de video")
                dico['video']=None
                dico['video_title']=None
                
                
            dico["genres"]=resp["genres"]
            if resp['in_production']==False:
                #question pour next air date pas forcément donné par l'API
                dico["next_episode_date"]=None
            else: 
                if resp['next_episode_to_air']==None:
                    dico["next_episode_date"]=None
                    dico["next_episode"]=None
                else:
                    next_air=resp["next_episode_to_air"]["air_date"]
                    liste=list(map(int,re.findall(r'\d+',next_air)))
                    if len(liste)==3:
                        dico["next_episode_date"]=date(liste[0],liste[1],liste[2])
                    season=resp["next_episode_to_air"]["season_number"]
                    episode=resp["next_episode_to_air"]["episode_number"]
                    dico["next_episode"]="{}x{}".format(season,episode)
                    
            
            today= date.today()
            if  dico["next_episode_date"]!=None:
                dico["alert"]=(dico["next_episode_date"]-today).days
            else:
                dico['alert']=None
            
            
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
            dico["seasons"]=resp["seasons"]
            if resp["poster_path"]!=None:
                dico["poster_path"]="https://image.tmdb.org/t/p/w500"+resp["poster_path"]
            else:
                dico["poster_path"]="/static/img/no_image_available.png"
            dico['id']=tv_id[i]
            dict_series.append(dico)
        return dict_series

    def _get_attributes_for_season(self,tv_id,season_number):
        dico={}
        url="https://api.themoviedb.org/3/tv/"+str(tv_id)+"/season/"+str(season_number)+"?api_key="+self.API_KEY+"&language=en-US"
        req =requests.get(url)
        resp=json.loads(req.content)
        dico["name"]=resp["name"] #nom de la saison
        dico["overview"]=resp["overview"]
        dico["air_date"]=resp["air_date"]
        dico["episodes"]=resp["episodes"]
        return dico
    
 
    def _get_tv_by_genre(self,genre_id,page=1):
        url="https://api.themoviedb.org/3/discover/tv?api_key="+self.API_KEY+"&language=en-US&with_genres="+str(genre_id)+"&air_date.gte=2012-01-01&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        results=resp["results"]
        dict_series={}
        for i in results:
            dico={}
            try:
                dico['id']=i['id']
            except:
                continue
            dico['id']=i['id']
            if i["poster_path"]!=None:
                    dico["poster_path"]="https://image.tmdb.org/t/p/w500"+i["poster_path"]
            else:
                dico["poster_path"]="/static/img/no_image_available.png"
            dico['name']=i['name']
            dict_series[dico['id']]=dico
        return dict_series
    
    def _get_genre_total_page(self,genre_id):
        url="https://api.themoviedb.org/3/discover/tv?api_key="+self.API_KEY+"&language=en-US&with_genres="+str(genre_id)+"&air_date.gte=2012-01-01"
        req =requests.get(url)
        resp=json.loads(req.content)
        total_pages =resp['total_pages']
        return total_pages
        
        
        
    def _get_tv_airing_today(self,page=1):
        url="https://api.themoviedb.org/3/tv/airing_today?api_key="+self.API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        results=resp["results"]
#        dict_series={}
#        for i in results:
#            dico={}
#            dico['id']=i['id']
#            if i["poster_path"]!=None:
#                    dico["poster_path"]="https://image.tmdb.org/t/p/w500"+i["poster_path"]
#            else:
#                dico["poster_path"]="/static/img/no_image_available.png"
#            dico['name']=i['name']
#            dict_series[dico['id']]=dico
#        #print(len(dict_series))
#        return dict_series
        return results
    
    def _get_tv_airing_week(self,page=1):
        url=" https://api.themoviedb.org/3/tv/on_the_air?api_key="+self.API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        results=resp["results"]
#        dict_series={}
#        for i in results:
#            dico={}
##            print(i)
#
#            dico['id']=i['id']
#            if i["poster_path"]!=None:
#                    dico["poster_path"]="https://image.tmdb.org/t/p/w500"+i["poster_path"]
#            else:
#                dico["poster_path"]="/static/img/no_image_available.png"
#            dico['name']=i['name']
#            dict_series[dico['id']]=dico
#        #print(len(dict_series))
#        return dict_series
        return results

    def _get_number_of_trending_page(self,page=1):
        url="https://api.themoviedb.org/3/tv/popular?api_key="+self.API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp =json.loads(req.content)
        number= resp['total_pages']
        return number

    
    def _get_series_trending(self,page=1):
        url="https://api.themoviedb.org/3/tv/popular?api_key="+self.API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        results=resp["results"]
#        dict_series={}
#        for i in results:
#            dico={}
##            print(i)
#
#            dico['id']=i['id']
#            if i["poster_path"]!=None:
#                    dico["poster_path"]="https://image.tmdb.org/t/p/w500"+i["poster_path"]
#            else:
#                dico["poster_path"]="/static/img/no_image_available.png"
#            dico['name']=i['name']
#            dict_series[dico['id']]=dico
#        #print(len(dict_series))
#        return dict_series
        return results


##TODO: display more recommandation by chaning page
    def _get_similar_series(self,tv_id):
        url="https://api.themoviedb.org/3/tv/"+str(tv_id)+"/recommendations?api_key="+self.API_KEY+"&language=en-US&page=1"
        req =requests.get(url)
        resp=json.loads(req.content)
        results=resp["results"]
#        liste_id=[]
#        for show in results:
#            liste_id.append(show['id'])
        
        return results
      
    def _get_episodes_by_list(self,tv_id):
        dict_series = []
        for i in range(len(tv_id)):
            url="https://api.themoviedb.org/3/tv/"+str(tv_id[i])+"?api_key="+self.API_KEY+"&language=en-US"
            req =requests.get(url)
            resp=json.loads(req.content)
            for j in range(len(resp["seasons"])):
                url2="https://api.themoviedb.org/3/tv/"+str(resp["id"])+"/season/"+str(resp["seasons"][j]["season_number"])+"?api_key="+self.API_KEY+"&language=en-US"
                req2 =requests.get(url2)
                resp2=json.loads(req2.content)
                for k in range(len(resp2["episodes"])):
                    dico={}
                    dico["serie_id"]=resp["id"]
                    dico["serie_name"]=resp["name"]
                    dico["serie_overview"]=resp["overview"]
                    dico["serie_poster_path"]="https://image.tmdb.org/t/p/w500"+resp["poster_path"]
                    dico["serie_nb_episodes"]=resp["number_of_episodes"]
                    dico["serie_nb_seasons"]=resp["number_of_seasons"]
                    dico["season_name"]=resp["seasons"][j]["name"]
                    dico["season_number"]=resp["seasons"][j]["season_number"]
                    dico["episode_air_date"]=resp2["episodes"][k]["air_date"]
                    dico["episode_name"]=resp2["episodes"][k]["name"]
                    dico["episode_overview"]=resp2["episodes"][k]["overview"]
                    dico["episode_number"]=resp2["episodes"][k]["episode_number"]
                    dict_series.append(dico)
        return dict_series 
    

#id will be automatically generated by the model
class Serie(models.Model): 
    serie_id = models.IntegerField(verbose_name = "Serie id",default=999999999)
    name = models.CharField(max_length=300, null = False)
    nb_episodes = models.IntegerField(verbose_name = "Total number of episodes")
    nb_seasons = models.IntegerField(verbose_name = "Total number of seasons")
    genres = models.TextField(null=True)
    overview = models.TextField(null=True)
    last_episode_date = models.DateTimeField(verbose_name =  "Date of last episode", null = True)
    last_episode = models.CharField(max_length=10, verbose_name = "Last episode", null = True)
    next_episode_date = models.DateTimeField(verbose_name =  "Date of next episode", null = True)
    next_episode = models.CharField(max_length=10, verbose_name = "Next episode", null = True)
    video = models.CharField(max_length=200, verbose_name = "Video path", null = True)
    video_title = models.CharField(max_length=200, verbose_name = "Video title", null = True)
    poster_path = models.CharField(max_length=200, verbose_name = "Poster path", null = True)
    alert = models.IntegerField(verbose_name = "Days before next episode",default=None)
    seasons = models.TextField(null=True, verbose_name = "Seasons and episodes info")
    favorites_user = models.TextField(default='[]', null=True,blank=True)
    
    
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
    favorites = models.TextField(default='[]', null=True,blank=True)
    alerts_seen = models.NullBooleanField(default=False, null=True,blank=True)
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
        
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(user=instance)
    instance.profil.save()
       





