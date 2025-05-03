from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from .forms import UserQuery
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