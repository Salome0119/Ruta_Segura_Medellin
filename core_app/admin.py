from django.contrib import admin
from .models import (
    SectoresCriticos,
    HistoricoAccidentes,
    FlujoTiempoReal,
    PrediccionesTrafico,
    ClimaActual
)

@admin.register(SectoresCriticos)
class SectoresCriticosAdmin(admin.ModelAdmin):
    list_display = ('nombre_sector', 'departamento', 'municipio', 'barrio', 'es_inundable', 'capacidad_vehicular_max')
    search_fields = ('nombre_sector', 'municipio', 'barrio', 'departamento')
    list_filter = ('departamento', 'municipio', 'es_inundable')
    list_editable = ('es_inundable',)

@admin.register(HistoricoAccidentes)
class HistoricoAccidentesAdmin(admin.ModelAdmin):
    list_display = ('sector', 'fecha_hora', 'gravedad', 'tipo_vehiculo', 'condicion_climatica')
    list_filter = ('gravedad', 'condicion_climatica', 'fecha_hora')
    search_fields = ('sector__nombre_sector', 'tipo_vehiculo')

@admin.register(FlujoTiempoReal)
class FlujoTiempoRealAdmin(admin.ModelAdmin):
    list_display = ('sector', 'fecha_hora_registro', 'velocidad_promedio', 'volumen_vehicular', 'nivel_congestion')
    list_filter = ('nivel_congestion', 'fecha_hora_registro')
    search_fields = ('sector__nombre_sector',)

@admin.register(PrediccionesTrafico)
class PrediccionesTraficoAdmin(admin.ModelAdmin):
    list_display = ('sector', 'fecha_hora_predicha', 'probabilidad_congestion', 'fecha_hora_ejecucion')
    list_filter = ('fecha_hora_predicha',)
    search_fields = ('sector__nombre_sector',)

@admin.register(ClimaActual)
class ClimaActualAdmin(admin.ModelAdmin):
    list_display = ('departamento', 'municipio', 'intensidad_lluvia', 'alerta_inundacion_activa', 'ultima_actualizacion')
    list_filter = ('alerta_inundacion_activa', 'departamento')
    search_fields = ('municipio', 'departamento')