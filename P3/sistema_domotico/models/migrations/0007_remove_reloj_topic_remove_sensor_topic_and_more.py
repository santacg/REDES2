# Generated by Django 5.0.6 on 2024-06-28 07:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0006_remove_evento_descripcion_remove_reloj_device_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reloj',
            name='topic',
        ),
        migrations.RemoveField(
            model_name='sensor',
            name='topic',
        ),
        migrations.RemoveField(
            model_name='switch',
            name='topic',
        ),
    ]
