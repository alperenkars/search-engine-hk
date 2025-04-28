from django.db import models

# Create your models here.

class EachUserQueryHistory(models.Model):
    cookie_id = models.CharField(max_length=500, unique=True, primary_key=True)
    request = models.BooleanField(default=False) # true if user request reload, so that user can get results in GET from views.py
    request_query = models.CharField(max_length=500) # the request query for the reload 

class UserQuery(models.Model):
    history = models.ForeignKey(
        EachUserQueryHistory, 
        on_delete=models.CASCADE, 
        related_name="queries"
    )
    query = models.CharField(max_length=500, default='')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.query

class SearchResult(models.Model):
    title = models.CharField(max_length=500)
    url = models.URLField()
    lastModificationDate = models.CharField(max_length=500)
    pageSize = models.IntegerField()
    keywords = models.CharField(max_length=500)