# Generated by Django 4.2.3 on 2023-07-20 20:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ScoreParameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criteres', models.CharField(max_length=100)),
                ('poids', models.DecimalField(decimal_places=2, max_digits=5)),
                ('objectif', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score_parameters', models.ManyToManyField(to='client.scoreparameters')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='client', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]