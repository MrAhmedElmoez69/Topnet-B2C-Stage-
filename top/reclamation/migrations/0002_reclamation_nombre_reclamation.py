# Generated by Django 4.2.3 on 2023-07-25 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reclamation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reclamation',
            name='nombre_reclamation',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
