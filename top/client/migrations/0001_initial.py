# Generated by Django 4.1.6 on 2023-07-23 15:29

import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScoreParameters',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('anciennete', models.IntegerField(blank=True, choices=[(1, '< 1 an'), (2, '1 an < ancienneté < 2 ans'), (3, '2 ans et plus')], default=None, null=True)),
                ('criteres', models.CharField(choices=[('valeur_commerciale', 'Valeur Commerciale'), ('engagement_client', 'Engagement Client'), ('engagement_topnet', 'Engagement Topnet'), ('comportement_client', 'Comportement Client')], max_length=100)),
                ('poids', models.DecimalField(decimal_places=2, max_digits=5)),
                ('objectif', models.DecimalField(decimal_places=2, max_digits=5)),
                ('categorie_client', models.IntegerField(blank=True, choices=[(None, 'Unspecified'), (0, 'Standard'), (1, 'VIP')], default=None, null=True)),
                ('engagement_contractuel', models.IntegerField(blank=True, choices=[(None, 'Unspecified'), (0, 'Engagé'), (1, 'Non Engagé')], default=None, null=True)),
                ('offre', models.DecimalField(blank=True, choices=[(None, 'Unspecified'), (0.5, 'XDSL'), (1, 'HD')], decimal_places=1, default=None, max_digits=3, null=True)),
                ('debit', models.PositiveIntegerField(blank=True, choices=[(None, 'Unspecified'), (100, 1), (50, 0.9), (30, 0.8), (20, 0.7), (12, 0.6), (10, 0.4), (8, 0.2), (4, 0)], default=None, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('phone_number', models.CharField(max_length=17, validators=[django.core.validators.RegexValidator(message='Le numéro de téléphone doit être au format +216 00 000 000.', regex='^\\+216 \\d{2} \\d{3} \\d{3}$')])),
                ('CIN', models.CharField(max_length=250, validators=[django.core.validators.RegexValidator(message='Numbers Only!', regex='^[0-9]{8}$')], verbose_name='CIN')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('score_parameters', models.ManyToManyField(to='client.scoreparameters')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
