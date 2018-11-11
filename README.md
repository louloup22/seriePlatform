# seriePlatform

This project is aimed to create a search platform for series. It uses the API of https://www.themoviedb.org/ and the website uses django framework. You can search, add series to favorites and be notified of the episodes of your favorite series that will be released in the next days. To be able to have the updated notification you need to click on search for the moment to make the changes.

## Technical set-up precaution

First, this project is working with python 3.7.0.

To be able to use the project, you will need to have django installed on your local machine in your python packages :

```python
python -m pip install Django==2.0
```

In the webapp folder you must create a config.py file where you store the API_KEY from the movie database.

In config.py file write :

```python
API_KEY = "Your API key"
```

You will find your API_KEY by creating an account in https://www.themoviedb.org/.
The documentation for the use of the API is available here : https://developers.themoviedb.org/3/

To run the server, type on the command line in the project folder:

```python
python manage.py runserver
```

If you modify global variable in the different classes of models.py you need to update the database. To do so just run on the command line these 2 commands:

```python
python manage.py makemigrations
python manage.py migrate
```

### Python packages :

Other python packages that need to be installed on your local machine (use pip install to do so) :
```python
#requests : HTTP library for python
python -m pip install requests==2.20.0
#(pandas) --> imported but not used
```

The web application has also been deployed on previous version. You can access the website here : https://ancient-journey-48339.herokuapp.com


## General overview

You need to sign up or login to access the website. Then the website will redirect you to the home page where you can look at the TV shows airing today or in the week.

If you prefer, you can also search TV shows by keywords or look at trending series.
At any time you when you see the picture of a TV show you can see more information (click on the name that appears when you hover on the picture) or add it to your favorites list. Then you can also look at all your favorite series and you will be notified of new episodes that will be aired in the next 4 days in your favorites list. If you want to remove a TV show from your favorite list, just browse your favorite list and click on the button "Remove from favorites" in the poster of the desired TV show. 

If you want more information about a TV show, you will be redirected to the TV show information page where you will see its genre (click on it to see other TV shows of the same genre), a trailer from youtube, episodes and seasons informations. You can click on the name of a season to have more information about this season and its episodes and browse the different seasons of the TV shows.
