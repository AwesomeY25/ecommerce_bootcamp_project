# Generated by Django 5.1.3 on 2024-12-05 03:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerce_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='tags',
            field=models.CharField(default='exit', help_text='Enter tags separated by commas', max_length=100),
            preserve_default=False,
        ),
    ]
