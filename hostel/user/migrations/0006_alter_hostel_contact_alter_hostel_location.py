# Generated by Django 4.1.7 on 2023-04-06 02:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_rename_images1_hostel_images_remove_hostel_images2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hostel',
            name='contact',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='hostel',
            name='location',
            field=models.CharField(choices=[('Kathmandu', 'Kathmandu'), ('Lalitpur', 'Lalitpur'), ('Bhaktapur', 'Bhaktapur')], default='Kathmandu', max_length=100),
        ),
    ]
