# Generated by Django 4.1.6 on 2023-07-29 12:58

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0019_remove_scoreparameters_anciennete_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='scoreparameters',
            options={'verbose_name_plural': 'Calculate Score Axes'},
        ),
        migrations.AddField(
            model_name='client',
            name='score_parameters',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='client_score_parameters', to='client.scoreparameters'),
        ),
        migrations.AlterField(
            model_name='scoreparameters',
            name='comportement_client_weight',
            field=models.PositiveIntegerField(default=25, help_text='Weight for Comportement Client in percentage.', validators=[django.core.validators.MinValueValidator(0, message='Weight should be at least 0.'), django.core.validators.MaxValueValidator(100, message='Weight cannot exceed 100.')]),
        ),
        migrations.AlterField(
            model_name='scoreparameters',
            name='engagement_client_weight',
            field=models.PositiveIntegerField(default=25, help_text='Weight for Engagement Client in percentage.', validators=[django.core.validators.MinValueValidator(0, message='Weight should be at least 0.'), django.core.validators.MaxValueValidator(100, message='Weight cannot exceed 100.')]),
        ),
        migrations.AlterField(
            model_name='scoreparameters',
            name='engagement_topnet_weight',
            field=models.PositiveIntegerField(default=25, help_text='Weight for Engagement Topnet in percentage.', validators=[django.core.validators.MinValueValidator(0, message='Weight should be at least 0.'), django.core.validators.MaxValueValidator(100, message='Weight cannot exceed 100.')]),
        ),
        migrations.AlterField(
            model_name='scoreparameters',
            name='valeur_commerciale_weight',
            field=models.PositiveIntegerField(default=25, help_text='Weight for Valeur Commerciale in percentage.', validators=[django.core.validators.MinValueValidator(0, message='Weight should be at least 0.'), django.core.validators.MaxValueValidator(100, message='Weight cannot exceed 100.')]),
        ),
    ]
