# Generated by Django 5.1.2 on 2024-11-12 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_alter_accountactivation_salt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountactivation',
            name='salt',
            field=models.BinaryField(max_length=32),
        ),
        migrations.AlterField(
            model_name='accountactivation',
            name='verifier',
            field=models.BinaryField(max_length=32),
        ),
    ]
