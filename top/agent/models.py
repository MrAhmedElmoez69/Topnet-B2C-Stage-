from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import RegexValidator,MaxLengthValidator

class Agent(AbstractUser):
    groups = models.ManyToManyField(Group, verbose_name='groups', blank=True, related_name='agents')
    user_permissions = models.ManyToManyField(Permission, verbose_name='user permissions', blank=True, related_name='agents')



class ScoreRule(models.Model):
    name = models.CharField(max_length=100)
    weight = models.FloatField()

class ScoreParameter(models.Model):
    rule = models.ForeignKey(ScoreRule, on_delete=models.CASCADE)
    parameter_name = models.CharField(max_length=100)
    weight = models.FloatField()

class Score(models.Model):
    client = models.ForeignKey('client.Client', on_delete=models.CASCADE)
    rule = models.ForeignKey(ScoreRule, on_delete=models.CASCADE)
    score = models.FloatField()

    