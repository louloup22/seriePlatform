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
from threading import Thread


#On importe en premier lieu la clé de l'API qu'on a préalablement enregistrée dans le fichier config.py
API_KEY = config.API_KEY
#On définit le format des demandes autorisées
query = models.CharField(null = True, verbose_name = "Search", max_length=400)

#La classe SearchThread va nous permettre de faire tourner des threads dès que nous allons réaliser une demande à l'API,
#optimisant ainsi le temps d'exécution puisque nous pourrons faire tourner plusieurs threads en même temps selon des méthodes différentes.

class SearchThread(Thread):

#Chaque thread a pour argument en entrée une méthode (le plus souvent de la classe Search) et une liste d'arguments non prédéfinis (d'où l'utilisation de *args)
    def __init__(self, method, *args):
        Thread.__init__(self)
        self.method = method
        self.args=args
        self.results = None

#La fonction run du thread enregistre le résultat de la méthode employée dans self.results.        
    def run(self):
        self.results = self.method(*self.args)
        #self.results.type = self.method(*args).type

#La fonction result nous permet de récupérer le résultat du thread et ainsi de le réutiliser dans le code.
    def result(self):
        return self.results

#La classe Search va regrouper les différentes méthodes, notamment d'appel à l'API, qui nous permettent d'obtenir les informations sur les séries
# et ceci selon différents arguments d'entrée. C'est une classe statique et publique dont les méthodes seront utilisées dans les Threads.


class Search(models.Model):
    #API_KEY = models.CharField(default=config.API_KEY, null = False, max_length=500)
    #query = models.CharField(null = True, verbose_name = "Search", max_length=400)
    
    def get_serie_by_name_with_space(query,page=1):
        #20 results by page
        query=query.replace(" ","+")
        url="https://api.themoviedb.org/3/search/tv?query="+query+"&api_key="+API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        results=resp["results"]
        #print(resp)
        return results       
        
    def get_number_of_result(query,page=1):
        url="https://api.themoviedb.org/3/search/tv?query="+query+"&api_key="+API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        print(resp['total_results'])
        return resp['total_results']
    
    def get_number_of_pages(query,page=1):
        url="https://api.themoviedb.org/3/search/tv?query="+query+"&api_key="+API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        print(resp['total_pages'])
        return resp['total_pages']
    
    
    def get_info_from_result(query,page=1):
        dict_series={}
        obj=get_serie_by_name_with_space(query,page)
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
    
    def get_id_from_result(query,page=1):
        liste_id=[]
        obj=get_serie_by_name_with_space(query,page)
        for i in obj["results"]:
            #print(type(i['id']))
            liste_id.append(i['id'])
        print(len(liste_id))
        return liste_id
    
    
    
    def get_attributes_for_serie(tv_id):
        # dict_series = []
        # for i in range(len(tv_id)):
        dico={}
        url="https://api.themoviedb.org/3/tv/"+str(tv_id)+"?api_key="+API_KEY+"&language=en-US"
        url_video="https://api.themoviedb.org/3/tv/"+str(tv_id)+"/videos?api_key="+API_KEY+"&language=en-US"
        req =requests.get(url)
        resp=json.loads(req.content)
        reqvideo=requests.get(url_video)
        video_resp=json.loads(reqvideo.content)
        video_resp=video_resp['results']
        #print(resp)
        if video_resp!=[]:
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
            dico["next_episode"]=None
        else: 
            #print("This is next episode to air : {}".format(resp['next_episode_to_air']))
            if resp['next_episode_to_air']==None:
                dico["next_episode_date"]=None
                dico["next_episode"]=None
            elif resp['next_episode_to_air']=="null":
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
            dico['alert']=999999
        
        
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
        dico['id']=tv_id
        # dict_series.append(dico)
        return dico

    def get_attributes_for_season(tv_id,season_number):
        dico={}
        url="https://api.themoviedb.org/3/tv/"+str(tv_id)+"/season/"+str(season_number)+"?api_key="+API_KEY+"&language=en-US"
        req =requests.get(url)
        resp=json.loads(req.content)
        dico["name"]=resp["name"] #nom de la saison
        dico["overview"]=resp["overview"]
        dico["air_date"]=resp["air_date"]
        dico["episodes"]=resp["episodes"]
        if resp["poster_path"]!=None:
                dico["poster_path"]="https://image.tmdb.org/t/p/w500"+resp["poster_path"]
        else:
            dico["poster_path"]="/static/img/no_image_available.png"
        return dico
    
 
    
    """Obtenir une liste de série d'un genre en particulier
    Pour obtenir une liste assez significative sans avoir trop de résultats nous ne montrerons
    que des séries ayant eu un épisode au moins depuis le 1er janvier 2012
    """
    def get_tv_by_genre(genre_id,page=1):
        url="https://api.themoviedb.org/3/discover/tv?api_key="+API_KEY+"&language=en-US&with_genres="+str(genre_id)+"&air_date.gte=2012-01-01&page="+str(page)
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
        return results
    
    def get_genre_total_page(genre_id):
        url="https://api.themoviedb.org/3/discover/tv?api_key="+API_KEY+"&language=en-US&with_genres="+str(genre_id)+"&air_date.gte=2012-01-01"
        req =requests.get(url)
        resp=json.loads(req.content)
        total_pages =resp['total_pages']
        return total_pages
        
    def get_tv_airing_today(page=1):
        url="https://api.themoviedb.org/3/tv/airing_today?api_key="+API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        results=resp["results"]
        return results
    
    def get_tv_airing_week(page=1):
        url=" https://api.themoviedb.org/3/tv/on_the_air?api_key="+API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        results=resp["results"]
        return results

    def get_number_of_trending_page(page=1):
        url="https://api.themoviedb.org/3/tv/popular?api_key="+API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp =json.loads(req.content)
        number= resp['total_pages']
        return number

    
    def get_series_trending(page=1):
        url="https://api.themoviedb.org/3/tv/popular?api_key="+API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        results=resp["results"]
        return results


##TODO: display more recommandation by changing page
    def get_similar_series(tv_id):
        url="https://api.themoviedb.org/3/tv/"+str(tv_id)+"/recommendations?api_key="+API_KEY+"&language=en-US&page=1"
        req =requests.get(url)
        resp=json.loads(req.content)
        results=resp["results"]        
        return results
      
    def get_episodes_by_list(tv_id):
        dict_series = []
        for i in range(len(tv_id)):
            url="https://api.themoviedb.org/3/tv/"+str(tv_id[i])+"?api_key="+API_KEY+"&language=en-US"
            req =requests.get(url)
            resp=json.loads(req.content)
            for j in range(len(resp["seasons"])):
                url2="https://api.themoviedb.org/3/tv/"+str(resp["id"])+"/season/"+str(resp["seasons"][j]["season_number"])+"?api_key="+API_KEY+"&language=en-US"
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
    seasons = models.TextField(null=True, verbose_name = "Seasons and episodes info")
    nb_fav_users = models.IntegerField(default=0, null=True,blank=True)
    alert = models.IntegerField(verbose_name = "Days before next episode",default=999999, null=True,blank=True)
    
    
    class Meta:
        verbose_name = "Série"
        verbose_name_plural= "Séries"
    
    # def __str__(self):
    #     return self.name

    def update_serie(self, nb_episodes, nb_seasons, last_episode_date,last_episode, next_episode_date, next_episode,seasons,video,alert):
        self.nb_episodes = nb_episodes
        self.nb_seasons = nb_seasons
        self.last_episode_date = last_episode_date
        self.last_episode = last_episode
        self.next_episode_date = next_episode_date
        self.next_episode = next_episode
        self.seasons = seasons
        self.video = video
        self.alert = alert
        return self

    def display_favorites(self):
        dict = {}
        dict['id'] = self.id
        dict['name'] = self.name
        dict['poster_path'] = self.poster_path
        return dict




class Profil(models.Model):
    user =  models.OneToOneField(User,on_delete=models.CASCADE) #liaison vers modèle User
    favorites = models.TextField(default='[]', null=True,blank=True)
    
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
    def remove_favorite(self,id):
        self.favorites=[int(item) for item in self.favorites[1:-1].split(',')]
        self.favorites.remove(id)
        self.save()

        
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(user=instance)
    instance.profil.save()


        
    

                





