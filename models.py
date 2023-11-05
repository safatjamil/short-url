from django.db import models

class Org(models.Model):
    org_email = models.CharField(max_length=50)
    org_alias = models.CharField(max_length=4)
    password = models.BinaryField(max_length=255)
class Cookie(models.Model):
    org_id = models.CharField(max_length=30)
    sec_key = models.CharField(max_length=20)
class RedirectMap(models.Model):
    org_id = models.CharField(max_length=20)
    org_alias = models.CharField(max_length=4)
    redirect_name = models.CharField(max_length=60)
    randcode = models.CharField(max_length=6)
    redirect_to = models.CharField(max_length=400)
