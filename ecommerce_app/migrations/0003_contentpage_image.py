# Generated by Django 5.1.3 on 2024-12-06 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_app', '0002_contentpage'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentpage',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='content_images/'),
        ),
    ]