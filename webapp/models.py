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

#Cette première fonction permet d'obtenir les résultats d'une requête, préalablement reformatée (query.replace), en faisant appel à l'API.
    def get_serie_by_name_with_space(query,page=1):
        #20 results by page
        query=query.replace(" ","+")
        url="https://api.themoviedb.org/3/search/tv?query="+query+"&api_key="+API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        results=resp["results"]
        return results

#Cette fonction nous permet d'obtenir le nombre de résultat d'une requête en faisant 1 appel à l'API
    def get_number_of_result(query,page=1):
        url="https://api.themoviedb.org/3/search/tv?query="+query+"&api_key="+API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        print(resp['total_results'])
        return resp['total_results']

#Cette fonction nous permet d'obtenir le nombre de pages nécessaires pour afficher la requête (à raison de 20 résultats/page)
    def get_number_of_pages(query,page=1):
        url="https://api.themoviedb.org/3/search/tv?query="+query+"&api_key="+API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        print(resp['total_pages'])
        return resp['total_pages']

#Cette fonction permet d'obternir certaines informations sur les résultats d'une requête et notamment le chemin d'accès au poster de la série
    def get_info_from_result(query,page=1):
        dict_series={}
        obj=get_serie_by_name_with_space(query,page)
        for i in obj["results"]:
            dico={}
            dico['id']=i['id']
            if i["poster_path"]!=None:
                    dico["poster_path"]="https://image.tmdb.org/t/p/w500"+i["poster_path"]
            else:
                dico["poster_path"]="https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"
            dico['name']=i['name']
            dict_series[dico['id']]=dico
        return dict_series

#Cette fonction permet d'extraire les ids de chaque série présente dans un résultat de recherche et de les enregistrer dans une liste
    def get_id_from_result(query,page=1):
        liste_id=[]
        obj=get_serie_by_name_with_space(query,page)
        for i in obj["results"]:
            liste_id.append(i['id'])
        print(len(liste_id))
        return liste_id


#Cette fonction va permettre de récupérer les attributs pour correspondant à l'ID d'une série en entrée.
    def get_attributes_for_serie(tv_id):
        dico={}
        #Appel aux URL pour obtenir les attributs et la vidéo
        url="https://api.themoviedb.org/3/tv/"+str(tv_id)+"?api_key="+API_KEY+"&language=en-US"
        url_video="https://api.themoviedb.org/3/tv/"+str(tv_id)+"/videos?api_key="+API_KEY+"&language=en-US"
        req =requests.get(url)
        resp=json.loads(req.content)
        reqvideo=requests.get(url_video)
        video_resp=json.loads(reqvideo.content)
        video_resp=video_resp['results']
        #Gestion de la partie vidéo
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
        #Gestion de la partie attributs
        #Récupération de l'attribut genre
        dico["genres"]=resp["genres"]
        #Récupération des attributs: prochain épisdode, la date du prochain épisode, sa saison, son numéro et formatage.
        if resp['in_production']==False:
            #Question pour next air date pas forcément donné par l'API
            dico["next_episode_date"]=None
            dico["next_episode"]=None
        else:
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
        #Mise en place de l'alerte qui compte le nombre de jour avant la sortie du prochain épisode.
        #Par défaut, si il n'y a pas de prochain épisode planifié on donne la valeur 999999 à l'alerte
        today= date.today()
        if  dico["next_episode_date"]!=None:
            dico["alert"]=(dico["next_episode_date"]-today).days
        else:
            dico['alert']=999999
        #Récupération de la date du dernier épisode
        if resp["last_air_date"]!=None:
            last_air=resp["last_air_date"]
            liste=list(map(int,re.findall(r'\d+',last_air)))
            if len(liste)==3:
                dico["last_episode_date"]=date(liste[0],liste[1],liste[2])
            else:
                dico["last_episode_date"]="Error"
        else:
            dico["last_episode_date"]=None
        #Gestion de la récupération de la saison et du numéro du dernier épisode et formatage
        if dico["last_episode_date"]==None:
            dico["last_episode"]=None
        elif resp["last_episode_to_air"]!=None:
            #Devons nous l'ajouter?
            season=resp["last_episode_to_air"]["season_number"]
            episode=resp["last_episode_to_air"]["episode_number"]
            dico["last_episode"]="{}x{}".format(season,episode)
        else:
            dico["last_episode"]=None
        #Récupération du nom, du résumé, du nombre d'épisodes, du nombre de saisons, du nom des saisons, du chemin du poster et de l'id
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
        return dico

#Cette fonction récupère les informations d'une saison d'une série donnée: nom, résumé de la saison, date de sortie, épisodes, chemin du poster
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
#Cette fonction récupère les séries appartenant à un certain genre
    def get_tv_by_genre(genre_id,page=1):
        url="https://api.themoviedb.org/3/discover/tv?api_key="+API_KEY+"&language=en-US&with_genres="+str(genre_id)+"&air_date.gte=2012-01-01&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        results=resp["results"]
        return results

#Cette fonction récupère le nombre de pages pour un certain genre
    def get_genre_total_page(genre_id):
        url="https://api.themoviedb.org/3/discover/tv?api_key="+API_KEY+"&language=en-US&with_genres="+str(genre_id)+"&air_date.gte=2012-01-01"
        req =requests.get(url)
        resp=json.loads(req.content)
        total_pages =resp['total_pages']
        return total_pages

#Cette fonction récupère les séries qui sortent dans la journée
    def get_tv_airing_today(page=1):
        url="https://api.themoviedb.org/3/tv/airing_today?api_key="+API_KEY+"&language=en-US&page="+str(page)
        req =requests.get(url)
        resp=json.loads(req.content)
        results=resp["results"]
        return results

#Cette fonction récupère les séries qui sortent dans la semaine
    def get_tv_airing_week(page=1):
        url = " https://api.themoviedb.org/3/tv/on_the_air?api_key="+API_KEY+"&language=en-US&page="+str(page)
        req = requests.get(url)
        resp = json.loads(req.content)
        results = resp["results"]
        return results

#Cette fonction récupère le nombre de pages pour les suggestions de séries du moment
    def get_number_of_trending_page(page=1):
        url = "https://api.themoviedb.org/3/tv/popular?api_key="+API_KEY+"&language=en-US&page="+str(page)
        req = requests.get(url)
        resp = json.loads(req.content)
        number = resp['total_pages']
        return number

#Cette fonction récupère les suggestions de séries du moment
    def get_series_trending(page=1):
        url = "https://api.themoviedb.org/3/tv/popular?api_key="+API_KEY+"&language=en-US&page="+str(page)
        req = requests.get(url)
        resp = json.loads(req.content)
        results = resp["results"]
        return results

#Cette fonction permet de récupérer les séries similaires à la séries sélectionnée
    def get_similar_series(tv_id):
        url = "https://api.themoviedb.org/3/tv/"+str(tv_id)+"/recommendations?api_key="+API_KEY+"&language=en-US&page=1"
        req = requests.get(url)
        resp = json.loads(req.content)
        results = resp["results"]
        return results

#Création de la classe série qui notamment va servir à créer nos séries dans notre base de données
# à partir des informations récupérées lors des appels à la base de données externe
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


#Cette fonction va permettre de mettre à jour notre base de données interne grâce à la récupération des informations lors de la connection de l'utilisateur
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


#Cette fonction retourne les informations nécessaires depuis la base de données interne qui seront utilisées pour afficher les séries favorites
    def display_favorites(self):
        dict = {}
        dict['id'] = self.id
        dict['name'] = self.name
        dict['poster_path'] = self.poster_path
        return dict


#Création de la classe Profil qui est complémentaire de Django pour la gestion des utilisateurs de notre site
class Profil(models.Model):
    #Liaison vers le modèle User de Django
    user =  models.OneToOneField(User,on_delete=models.CASCADE)
    favorites = models.TextField(default='[]', null=True,blank=True)

#Cette fonction permet à l'utilisateur d'ajouter aux favoris une série (appel de la fonction grâce au bouton "Add to favourites" sur le site")
    def _add_favorites(self,x):
        self.favorites = json.dumps(x)

#Cette fonction permet de convertir les favoris en une liste de favoris
    def _convert_favorites(self):
        liste_favorites = []
        string = json.loads(self.favorites)
        for el in string:
            liste_favorites.append(el)
        return liste_favorites

#Cette fonction permet de récupérer la liste de favoris d'un utilisateur
    def _get_favorites(self):
        return self._convert_favorites()

#Cette fonction permet de supprimer une série de la liste de favoris (appel de la fonction grâce à un bouton sur le site)
    def _remove_favorites(self,x):
        new_list = self._convert_favorites().pop(x)
        self.favorites = json.dumps(new_list)

#Cette fonction permet de mettre à jour le profil d'un utilisateur
@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(user=instance)
    instance.profil.save()
