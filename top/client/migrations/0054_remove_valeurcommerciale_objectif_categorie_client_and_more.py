# Generated by Django 4.1.6 on 2023-08-02 14:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0053_valeurcommerciale_objectif_categorie_client_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='valeurcommerciale',
            name='objectif_categorie_client',
        ),
        migrations.RemoveField(
            model_name='valeurcommerciale',
            name='objectif_debit',
        ),
        migrations.RemoveField(
            model_name='valeurcommerciale',
            name='objectif_engagement_contractuel',
        ),
        migrations.RemoveField(
            model_name='valeurcommerciale',
            name='objectif_offre',
        ),
    ]