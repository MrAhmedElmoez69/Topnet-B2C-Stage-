# Generated by Django 4.1.6 on 2023-08-03 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contrat', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contrat',
            name='montant_en_cours',
        ),
        migrations.AddField(
            model_name='contrat',
            name='nombre_facture_impayee',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
