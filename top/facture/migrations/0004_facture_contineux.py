# Generated by Django 4.2.3 on 2023-07-26 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facture', '0003_facture_statut_paiement_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='facture',
            name='contineux',
            field=models.BooleanField(default=False),
        ),
    ]
