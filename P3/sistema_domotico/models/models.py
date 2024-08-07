from django.db import models
# Create your models here.


class DispositivoIot(models.Model):
    nombre = models.CharField(max_length=50)

    class Meta:
        abstract = True


class Switch(DispositivoIot):
    state = models.CharField(
        max_length=3,
        choices=(('ON', 'On'), ('OFF', 'Off')),
        default='OFF',
    )

    def toggle(self):
        self.state = 'OFF' if self.state == 'ON' else 'ON'
        self.save()
        return self.state


class Sensor(DispositivoIot):
    valor = models.FloatField(default=0.0)
    unidad_de_medida = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id}: {self.valor} {self.unidad_de_medida}"


class Reloj(DispositivoIot):
    tiempo = models.TimeField(default='00:00:00')

    def __str__(self):
        return f"{self.nombre}: {self.tiempo}"


class Regla(models.Model):
    nombre = models.CharField(max_length=100)
    condicion = models.CharField(max_length=100)
    sensor_asociado = models.ForeignKey(
        Sensor, on_delete=models.CASCADE, related_name='reglas_sensor', null=True, blank=True)
    accion = models.CharField(max_length=100)
    switch_asociado = models.ForeignKey(
        Switch, on_delete=models.CASCADE, related_name='reglas_switch', null=True, blank=True)

    def __str__(self):
        return f"{self.nombre}: Si {self.condicion}, entonces {self.switch_asociado.__str__()} {self.accion}"


class Evento(models.Model):
    marca_de_tiempo = models.DateTimeField(auto_now_add=True)
    sensor = models.ForeignKey(
        Sensor, on_delete=models.CASCADE, related_name='evento_sensor', null=True, blank=True, default=None)
    valor = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.marca_de_tiempo}"
