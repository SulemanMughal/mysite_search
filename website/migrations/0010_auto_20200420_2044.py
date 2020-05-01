# Generated by Django 2.2.12 on 2020-04-20 15:44

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_configresultsdatabase'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configresultsdatabase',
            name='results_store_DB_1_timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Timestamp for DB 1'),
        ),
        migrations.AlterField(
            model_name='configresultsdatabase',
            name='results_store_DB_2_timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Timestamp for DB 2'),
        ),
        migrations.AlterField(
            model_name='configresultsdatabase',
            name='updated_timtstamp',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Results Updated Time'),
        ),
    ]
