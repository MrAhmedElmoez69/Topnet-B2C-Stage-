# Generated by Django 4.1.6 on 2023-07-29 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0030_alter_engagementtopnet_delai_traitement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='engagementtopnet',
            name='nombre_reclamations',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=3),
        ),
    ]
