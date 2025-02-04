# Generated by Django 4.1.6 on 2023-07-29 15:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0028_alter_engagementtopnet_delai_traitement_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='engagementtopnet',
            name='client',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='engagement_topnet', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='engagementtopnet',
            name='delai_traitement',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='engagementtopnet',
            name='nombre_reclamations',
            field=models.FloatField(default=0),
        ),
    ]
