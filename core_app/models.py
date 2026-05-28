from django.db import models

# =========================================================================
# TABLA 1: EJE GEOGRÁFICO (Sectores viales críticos de Colombia)
# =========================================================================
class SectoresCriticos(models.Model):
    DEPARTAMENTO_CHOICES = [
        ('ANT', 'Antioquia'),
        ('BGT', 'Bogotá D.C.'),
        ('VAC', 'Valle del Cauca'),
        ('SUC', 'SUCRE'),
        ('COR', 'Córdoba'),
        ('ATL', 'Atlántico'),
        ('BOL', 'Bolívar'),
        ('CAL', 'Caldas'),
        ('CAQ', 'Caquetá'),
        ('CAS', 'Casanare'),
        ('CUN', 'Cundinamarca'),
        ('HUA', 'Huila'),
        ('MAG', 'Magdalena'),
        ('NAR', 'Nariño'),
        ('QUE', 'Quindío'),
        ('RIS', 'Risaralda'),
    ]
    
    nombre_sector = models.CharField(max_length=150, help_text="Ej: Deprimido de la 80")
    departamento = models.CharField(max_length=3, choices=DEPARTAMENTO_CHOICES, db_index=True, help_text="Departamento", default='ANT')
    municipio = models.CharField(max_length=100, db_index=True, help_text="Ej: Medellín, Bogotá, Bello", default='Medellín')
    barrio = models.CharField(max_length=100, blank=True, null=True)
    latitud = models.DecimalField(max_length=10, decimal_places=8, max_digits=10)
    longitud = models.DecimalField(max_length=11, decimal_places=8, max_digits=11)
    es_inundable = models.BooleanField(default=False, help_text="Sufre inundaciones relámpago")
    capacidad_vehicular_max = models.IntegerField(help_text="Umbral de carros permitidos antes de colapso")

    class Meta:
        db_table = 'sectores_criticos'
        verbose_name_plural = "Sectores Críticos"

    def __str__(self):
        return f"{self.nombre_sector} ({self.municipio}, {self.departamento})"


# =========================================================================
# TABLA 2: MÓDULO 1 (Histórico de Accidentes, Víctimas y Fotomultas)
# =========================================================================
class HistoricoAccidentes(models.Model):
    GRAVEDAD_CHOICES = [
        ('Solo Daños', 'Solo Daños'),
        ('Con Heridos', 'Con Heridos'),
        ('Con Muertos', 'Con Muertos'),
    ]
    
    sector = models.ForeignKey(SectoresCriticos, on_delete=models.CASCADE, db_column='sector_id')
    fecha_hora = models.DateTimeField()
    gravedad = models.CharField(max_length=20, choices=GRAVEDAD_CHOICES)
    tipo_vehiculo = models.CharField(max_length=50, help_text="Moto, Auto, Peatón, Bicicleta")
    condicion_climatica = models.CharField(max_length=50, default='Seco')

    class Meta:
        db_table = 'historico_accidentes'
        verbose_name_plural = "Historial de Accidentes"


# =========================================================================
# TABLA 3: MÓDULO 2 (Monitoreo de Tránsito en Tiempo Real - Flujo cada 5 min)
# =========================================================================
class FlujoTiempoReal(models.Model):
    CONGESTION_CHOICES = [
        ('Fluido', 'Fluido'),
        ('Moderado', 'Moderado'),
        ('Crítico', 'Crítico'),
    ]

    sector = models.ForeignKey(SectoresCriticos, on_delete=models.CASCADE, db_column='sector_id')
    fecha_hora_registro = models.DateTimeField(db_index=True)
    velocidad_promedio = models.FloatField(help_text="Velocidad actual en km/h")
    volumen_vehicular = models.IntegerField(help_text="Cantidad de vehículos detectados")
    nivel_congestion = models.CharField(max_length=20, choices=CONGESTION_CHOICES)

    class Meta:
        db_table = 'flujo_tiempo_real'
        verbose_name_plural = "Flujo en Tiempo Real"


# =========================================================================
# TABLA 4: MÓDULO 3 (Predicciones de Congestión Urbana - Modelos de IA)
# =========================================================================
class PrediccionesTrafico(models.Model):
    sector = models.ForeignKey(SectoresCriticos, on_delete=models.CASCADE, db_column='sector_id')
    fecha_hora_ejecucion = models.DateTimeField(help_text="Cuándo calculó la IA la predicción")
    fecha_hora_predicha = models.DateTimeField(db_index=True, help_text="Hora futura anticipada")
    probabilidad_congestion = models.DecimalField(max_digits=3, decimal_places=2, help_text="Riesgo entre 0.00 y 1.00")

    class Meta:
        db_table = 'predicciones_trafico'
        verbose_name_plural = "Predicciones de Tráfico"


# =========================================================================
# TABLA 5: MÓDULO 4 (Estado del Clima Actual por Municipio)
# =========================================================================
class ClimaActual(models.Model):
    departamento = models.CharField(max_length=3, help_text="Código departamento", default='ANT')
    municipio = models.CharField(max_length=100, help_text="Ej: Medellín, Bogotá", default='Medellín')
    intensidad_lluvia = models.FloatField(default=0.0, help_text="Medido en mm/h")
    alerta_inundacion_activa = models.BooleanField(default=False)
    ultima_actualizacion = models.DateTimeField()

    class Meta:
        db_table = 'clima_actual'
        verbose_name_plural = "Clima Actual"
        unique_together = ['departamento', 'municipio']

    def __str__(self):
        return f"{self.municipio} - Alerta: {self.alerta_inundacion_activa}"
