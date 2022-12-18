from django.db import models

class Post(models.Model):
    title = models.CharField()
    text = models.CharField()
    date = models.DateTimeField(auto_now_add=True)
    tags = models.CharField()
    category = models.CharField()
    views = models.IntegerField()

