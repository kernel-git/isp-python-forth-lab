# Generated by Django 3.2.3 on 2021-05-19 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MediaContent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('displayed_name', models.CharField(max_length=60)),
            ],
        ),
    ]
