# Generated by Django 3.2.3 on 2021-06-02 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('papich_media_api', '0005_auto_20210531_0751'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mediacontent',
            name='likes',
        ),
        migrations.AddField(
            model_name='mediacontent',
            name='likers',
            field=models.ManyToManyField(related_name='liker', to='papich_media_api.User', verbose_name='Users, who hit like'),
        ),
    ]
