# Generated by Django 4.1.6 on 2023-08-21 17:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0060_axesweight_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='criteriaweight',
            name='active_axes_weight',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='active_criteria_weight', to='client.axesweight'),
        ),
    ]
