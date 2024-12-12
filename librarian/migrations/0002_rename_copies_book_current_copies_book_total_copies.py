# Generated by Django 5.1.4 on 2024-12-11 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('librarian', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='book',
            old_name='copies',
            new_name='current_copies',
        ),
        migrations.AddField(
            model_name='book',
            name='total_copies',
            field=models.IntegerField(default=1),
        ),
    ]