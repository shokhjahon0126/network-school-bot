from django.db import models


class User(models.Model):
    chat_id = models.BigIntegerField(unique=True)
    username = models.CharField(unique=True)
    full_name = models.CharField()

    class Meta:
        unique_together = ["chat_id","username"]