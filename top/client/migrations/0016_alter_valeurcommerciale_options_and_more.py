# Generated by Django 4.2.3 on 2023-07-26 13:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0015_alter_valeurcommerciale_debit'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='valeurcommerciale',
            options={'verbose_name_plural': 'Valeurs Commerciales'},
        ),
        migrations.RemoveField(
            model_name='valeurcommerciale',
            name='debit',
        ),
    ]
