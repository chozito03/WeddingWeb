# Generated by Django 4.1.5 on 2023-02-16 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wedding', '0002_invitedguests_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('artist', models.CharField(max_length=200)),
                ('album', models.CharField(max_length=200)),
                ('spotify_id', models.CharField(max_length=200)),
                ('preview_url', models.CharField(blank=True, max_length=256, null=True)),
                ('image_url', models.CharField(blank=True, max_length=256, null=True)),
            ],
        ),
    ]
