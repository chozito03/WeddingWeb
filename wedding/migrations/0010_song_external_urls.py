# Generated by Django 4.1.5 on 2023-02-17 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wedding', '0009_remove_song_user_id_song_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='external_urls',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
