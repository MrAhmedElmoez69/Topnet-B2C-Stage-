# Generated by Django 4.1.6 on 2023-07-29 12:48

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0018_engagementtopnet_delai_traitement'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scoreparameters',
            name='anciennete',
        ),
        migrations.RemoveField(
            model_name='scoreparameters',
            name='categorie_client',
        ),
        migrations.RemoveField(
            model_name='scoreparameters',
            name='client',
        ),
        migrations.RemoveField(
            model_name='scoreparameters',
            name='criteres',
        ),
        migrations.RemoveField(
            model_name='scoreparameters',
            name='debit',
        ),
        migrations.RemoveField(
            model_name='scoreparameters',
            name='engagement_contractuel',
        ),
        migrations.RemoveField(
            model_name='scoreparameters',
            name='objectif',
        ),
        migrations.RemoveField(
            model_name='scoreparameters',
            name='offre',
        ),
        migrations.RemoveField(
            model_name='scoreparameters',
            name='poids',
        ),
        migrations.AddField(
            model_name='scoreparameters',
            name='comportement_client_weight',
            field=models.PositiveIntegerField(default=25, help_text='Weight for Comportement Client axis (0 to 100).', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='scoreparameters',
            name='engagement_client_weight',
            field=models.PositiveIntegerField(default=25, help_text='Weight for Engagement Client axis (0 to 100).', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='scoreparameters',
            name='engagement_topnet_weight',
            field=models.PositiveIntegerField(default=25, help_text='Weight for Engagement TOPNET axis (0 to 100).', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='scoreparameters',
            name='valeur_commerciale_weight',
            field=models.PositiveIntegerField(default=25, help_text='Weight for Valeur Commerciale axis (0 to 100).', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
    ]