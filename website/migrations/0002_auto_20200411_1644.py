# Generated by Django 2.2.12 on 2020-04-11 11:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Fruits',
            new_name='Fruit',
        ),
        migrations.AlterModelOptions(
            name='fruit',
            options={'ordering': ['-id'], 'verbose_name': 'Fruit', 'verbose_name_plural': 'Fruits'},
        ),
    ]