from django.shortcuts import render,redirect
from django.contrib.auth import login, authenticate
from webapp.forms import SignUpForm, SearchForm
from webapp.models import Search
from pandas import DataFrame as df

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
            
            