# Generated by Django 4.2.6 on 2024-01-05 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='additional_duty_time',
            name='unique_add_duty',
        ),
        migrations.RemoveConstraint(
            model_name='main_duty_time',
            name='unique_main_duty_time_per_date',
        ),
        migrations.AddConstraint(
            model_name='additional_duty_time',
            constraint=models.UniqueConstraint(fields=('trooper', 'time_of_day', 'add_duty', 'commander'), name='unique_add_duty'),
        ),
        migrations.AddConstraint(
            model_name='main_duty_time',
            constraint=models.UniqueConstraint(fields=('start_time', 'end_time', 'main_duty', 'duty_date', 'commander'), name='unique_main_duty_time_per_date'),
        ),
    ]
