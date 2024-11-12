# Generated by Django 5.1.2 on 2024-11-12 12:56

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountActivation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=17)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=64)),
                ('salt', models.CharField(max_length=64)),
                ('verifier', models.CharField(max_length=128)),
                ('recruiter_id', models.IntegerField(blank=True, null=True)),
                ('hash', models.CharField(max_length=32, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.RemoveField(
            model_name='recruitreward',
            name='claimed_by',
        ),
        migrations.AddField(
            model_name='claimedreward',
            name='ip_address',
            field=models.CharField(default='127.0.0.1', max_length=45),
        ),
    ]
