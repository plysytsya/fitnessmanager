# Generated by Django 4.2 on 2023-05-25 19:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitnessmanager_api', '0004_alter_message_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='sent_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
