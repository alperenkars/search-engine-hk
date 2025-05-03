from django.contrib import admin
from .models import EachUserQueryHistory, UserQuery, SearchResult

# Register your models here.

admin.site.register(EachUserQueryHistory)
admin.site.register(UserQuery)
admin.site.register(SearchResult)