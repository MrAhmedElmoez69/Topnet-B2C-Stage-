# Generated by Django 4.1.6 on 2023-08-01 09:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0046_alter_axes_client_alter_axes_comportement_client_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='axes',
            name='comportement_client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='client.comportementclient'),
        ),
        migrations.AlterField(
            model_name='axes',
            name='engagement_client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='client.engagementclient'),
        ),
        migrations.AlterField(
            model_name='axes',
            name='engagement_topnet',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='client.engagementtopnet'),
        ),
        migrations.AlterField(
            model_name='axes',
            name='valeur_commerciale',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='client.valeurcommerciale'),
        ),
    ]
