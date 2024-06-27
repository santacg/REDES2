# Generated by Django 5.0.6 on 2024-06-27 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('models', '0003_remove_regla_interruptor_asociado_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reloj',
            name='formato_tiempo',
        ),
        migrations.RemoveField(
            model_name='reloj',
            name='status',
        ),
        migrations.RemoveField(
            model_name='sensor',
            name='status',
        ),
        migrations.RemoveField(
            model_name='switch',
            name='status',
        ),
        migrations.AlterField(
            model_name='reloj',
            name='device_type',
            field=models.CharField(choices=[('switch', 'Switch'), ('sensor', 'Sensor'), ('reloj', 'Reloj')], default=None, max_length=10),
        ),
        migrations.AlterField(
            model_name='sensor',
            name='device_type',
            field=models.CharField(choices=[('switch', 'Switch'), ('sensor', 'Sensor'), ('reloj', 'Reloj')], default=None, max_length=10),
        ),
        migrations.AlterField(
            model_name='switch',
            name='device_type',
            field=models.CharField(choices=[('switch', 'Switch'), ('sensor', 'Sensor'), ('reloj', 'Reloj')], default=None, max_length=10),
        ),
    ]
