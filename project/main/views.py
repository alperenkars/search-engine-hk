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

def get_stemmed_keywords():
    """Get all stemmed keywords from the database."""
    retrieval = Retrieval("main.db")
    return [word for word in retrieval.get_all_keywords() if word != '']

def get_user_query_history(cookie_id):
    """Get query history for a specific user."""
    try:
        query_history = EachUserQueryHistory.objects.get(cookie_id=cookie_id)
        return UserQuery.objects.filter(history=query_history).order_by('-timestamp')[:50]
    except EachUserQueryHistory.DoesNotExist:
        return []

def save_query_to_history(query_history, query_string):
    """Save a new query to the user's history."""
    if bool(query_string.strip()):
        new_query = UserQuery(history=query_history, query=query_string)
        new_query.save()

        # Keep only the latest 10 queries
        if UserQuery.objects.filter(history=query_history).count() > 10:
            UserQuery.objects.filter(
                pk__in=UserQuery.objects.filter(history=query_history)
                .order_by('-timestamp')
                .values_list('pk', flat=True)[10:]
            ).delete()

@csrf_protect
def index(request):
    query_submitted = False
    query_results = []
    stem_keywords = get_stemmed_keywords()

    if request.method == 'GET':
        cookie_id = request.COOKIES.get('user_cookie_id')

        # First time user
        if not cookie_id:
            cookie_id = uuid.uuid4()
            new_query_history, created = EachUserQueryHistory.objects.get_or_create(cookie_id=str(cookie_id))

            response = render(request, 'index.html', {
                "message": "Since this is the first time you use our search engine, we will help you to set up a new cookie.",
                "query_submitted": query_submitted,
                "stem_keywords": stem_keywords
            })
            response.set_cookie('user_cookie_id', str(cookie_id), max_age=63072000)
            return response
        
        # Returning user
        queries = get_user_query_history(cookie_id)
        return render(request, 'index.html', {
            "queries": queries,
            "query_submitted": query_submitted,
            "stem_keywords": stem_keywords
        })
        
    elif request.method == 'POST':
        cookie_id = request.COOKIES.get('user_cookie_id')

        if not cookie_id:
            return HttpResponse("Sorry, we cannot find your cookie. Please enable your cookie.", status=400)

        query_submitted = True
        query_history = EachUserQueryHistory.objects.get(cookie_id=cookie_id)

        # Handle stored query request
        if query_history.request:
            query_strings = query_history.request_query
            retrieval = Retrieval("main.db")
            query_results = retrieval.retrieve(query_strings)

            save_query_to_history(query_history, query_strings)
            queries = get_user_query_history(cookie_id)

            query_history.request = False
            query_history.request_query = ""
            query_history.save()

            return render(request, "index.html", {
                "query_results": query_results,
                "queries": queries,
                "query_submitted": query_submitted,
                "stem_keywords": stem_keywords
            })
        
        # Handle new query request
        query_strings = request.POST.get('query', '')
        retrieval = Retrieval("main.db")
        query_results = retrieval.retrieve(query_strings)

        save_query_to_history(query_history, query_strings)
        queries = get_user_query_history(cookie_id)

        return render(request, "index.html", {
            "query_results": query_results,
            "queries": queries,
            "query_submitted": query_submitted,
            "stem_keywords": stem_keywords
        })

@csrf_protect
def clear_history(request):
    if request.method == 'POST':
        cookie_id = request.COOKIES.get('user_cookie_id')
        if cookie_id:
            try:
                query_history = EachUserQueryHistory.objects.get(cookie_id=cookie_id)
                UserQuery.objects.filter(history=query_history).delete()
                return redirect('index')
            except EachUserQueryHistory.DoesNotExist:
                return HttpResponse("Query history not found.", status=404)
        else:
            return HttpResponse("Cookie not found.", status=400)
    return HttpResponse("Method not allowed.", status=405)