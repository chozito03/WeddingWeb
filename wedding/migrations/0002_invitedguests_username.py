# Generated by Django 4.1.5 on 2023-02-14 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wedding', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='invitedguests',
            name='username',
            field=models.CharField(max_length=64, null=True, unique=True),
        ),
    ]