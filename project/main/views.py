from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .forms import Query
from .models import SearchResult, EachUserQueryHistory, UserQuery
import uuid
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_protect
import json
from Retrieval import Retrieval
from django.urls import reverse
from django.shortcuts import redirect
# from django.http import HttpResponse

# Create your views here.

@csrf_protect
def index(request):
    # return HttpResponse("Hello world. You are currently at the main's index.")

    query_submitted = False
    query_results = []
    stem_keywords = []
    
    retrieval = Retrieval("main.db")
    stem_keywords = [word for word in retrieval.get_all_keywords() if word is not '']

    if request.method == 'GET':
        cookie_id = request.COOKIES.get('user_cookie_id')

        # when this is the very first time the user use the browser to view the search engine we interface
        if not cookie_id:
            cookie_id = uuid.uuid4()

            # make sure each user has a unique query history
            new_query_history, created = EachUserQueryHistory.objects.get_or_create(cookie_id = str(cookie_id))

            response = render(request, 'index.html', {
                "message": "Since this is the first time you use our search engine, we will help you to set up a new cookie.",
                "query_submitted": query_submitted,
                "stem_keywords": stem_keywords
            })
            # set the max_age to be 2 years, or 63072000 seconds
            response.set_cookie('user_cookie_id', str(cookie_id), max_age=63072000)

            return response
        
        # when this is not the very first time the user user our search engine, then the user already has a cookie
        else:
            query_history = EachUserQueryHistory.objects.get(cookie_id = cookie_id)
            queries = UserQuery.objects.filter(history = query_history).order_by('-timestamp')[:50]

            return render(request, 'index.html', {
                "queries": queries,
                "query_submitted": query_submitted,
                "stem_keywords": stem_keywords
            })
        
    elif request.method == 'POST':
        cookie_id = request.COOKIES.get('user_cookie_id')

        if cookie_id:
            query_submitted = True
            query_history = EachUserQueryHistory.objects.get(cookie_id = cookie_id)

            if query_history.request:
                query_submitted = True
                query_strings = query_history.request_query

                retrieval = Retrieval("main.db")
                query_results = retrieval.retrieve(query_strings)

                query_exist = UserQuery.objects.filter(history = query_history, query = query_strings).exists()

                if not query_exist and bool(query_strings.strip()):
                    new_query = UserQuery(history = query_history, query = query_strings)
                    new_query.save()

                    # Note that we only give the latest 10 query history for users
                    if UserQuery.objects.filter(history = query_history).count() > 10:
                        UserQuery.objects.filter(pk__in=UserQuery.objects.filter(history = query_history).order_by('-timestamp').values_list('pk', flat = True)[10:]).delete()
                
                queries = UserQuery.objects.filter(history = query_history).order_by('-timestamp')[:50]

                query_history.request = False
                query_history.request_query = ""
                query_history.save()

                return render(request,"index.html", {
                    "query_results": query_results,
                    "queries": queries,
                    "query_submitted": query_submitted,
                    "stem_keywords": stem_keywords
                })
            
            query_strings = request.POST.get('query', '')

            retrieval = Retrieval("main.db")
            query_results = retrieval.retrieve(query_strings)

            query_exist = UserQuery.objects.filter(history = query_history, query = query_strings).exists()

            if not query_exist and bool(query_strings.strip()):
                new_query = UserQuery(history = query_history, query = query_strings)
                new_query.save()

                # Note that we only give the latest 10 query history for users
                if UserQuery.objects.filter(history = query_history).count() > 10:
                    UserQuery.objects.filter(pk__in=UserQuery.objects.filter(history = query_history).order_by('-timestamp').values_list('pk', flat = True)[10:]).delete()

            queries = UserQuery.objects.filter(history = query_history).order_by('-timestamp')[:50]

            return render(request, "index.html", {
                "query_results": query_results,
                "queries": queries,
                "query_submitted": query_submitted,
                "stem_keywords": stem_keywords
            })
        
        else:
            return HttpResponse("Sorry, we cannot find your cookie. Please enable your cookie.", status = 400)