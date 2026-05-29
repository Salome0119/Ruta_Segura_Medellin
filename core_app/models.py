from django.db import models

class SectoresCriticos(models.Model):
    nombre_sector = models.CharField(max_length=100)
    departamento = models.CharField(max_length=50)
    municipio = models.CharField(max_length=50)
    barrio = models.CharField(max_length=50, blank=True, null=True)
    latitud = models.FloatField()
    longitud = models.FloatField()
    es_inundable = models.BooleanField(default=False)
    capacidad_vehicular_max = models.IntegerField(default=1000)

    def __str__(self):
        return self.nombre_sector


class ClimaActual(models.Model):
    departamento = models.CharField(max_length=50)
    municipio = models.CharField(max_length=50)
    intensidad_lluvia = models.FloatField()
    alerta_inundacion_activa = models.BooleanField(default=False)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.municipio} - {self.intensidad_lluvia}mm/h"


class FlujoTiempoReal(models.Model):
    sector = models.ForeignKey(SectoresCriticos, on_delete=models.CASCADE)
    fecha_hora_registro = models.DateTimeField()
    velocidad_promedio = models.FloatField()
    volumen_vehicular = models.IntegerField()
    nivel_congestion = models.CharField(max_length=20, choices=[
        ('Fluido', 'Fluido'),
        ('Moderado', 'Moderado'),
        ('Crítico', 'Crítico')
    ])

    def __str__(self):
        return f"{self.sector.nombre_sector} - {self.nivel_congestion}"


class HistoricoAccidentes(models.Model):
    sector = models.ForeignKey(SectoresCriticos, on_delete=models.CASCADE, null=True, blank=True)
    fecha_hora = models.DateTimeField()
    gravedad = models.CharField(max_length=20, choices=[
        ('Solo Daños', 'Solo Daños'),
        ('Con Heridos', 'Con Heridos'),
        ('Con Muertos', 'Con Muertos')
    ])
    tipo_vehiculo = models.CharField(max_length=20)
    condicion_climatica = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.fecha_hora} - {self.gravedad}"


class PrediccionesTrafico(models.Model):
    sector = models.ForeignKey(SectoresCriticos, on_delete=models.CASCADE)
    fecha_hora_ejecucion = models.DateTimeField()
    fecha_hora_predicha = models.DateTimeField()
    probabilidad_congestion = models.FloatField()

    def __str__(self):
        return f"{self.sector.nombre_sector} - {self.probabilidad_congestion}"