# Generated by Django 4.1.6 on 2023-08-02 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0049_engagementclient_poids_anciennete_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comportementclient',
            name='poids_contentieux',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='comportementclient',
            name='poids_delai_moyen_paiement',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
        migrations.AddField(
            model_name='comportementclient',
            name='poids_incident_de_paiement',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]
