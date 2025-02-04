# Generated by Django 4.1.6 on 2023-07-25 14:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0005_valeurcommerciale'),
    ]

    operations = [
        migrations.CreateModel(
            name='EngagementClient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='engagement_client', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
