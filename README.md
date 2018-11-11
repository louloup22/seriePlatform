# seriePlatform

This project is aimed to create a search platform for series. It uses the API of https://www.themoviedb.org/ and the website uses django framework.

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
