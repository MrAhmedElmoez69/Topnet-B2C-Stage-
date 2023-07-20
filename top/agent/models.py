from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class Agent(AbstractUser):
    # Your fields for the Agent model go here

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='agent_set'  # Change 'agent_set' to a unique related_name
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='agent_set'  # Change 'agent_set' to a unique related_name
    )

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