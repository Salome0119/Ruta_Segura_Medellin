from django.core.management.base import BaseCommand
from core_app.models import SectoresCriticos

class Command(BaseCommand):
    help = 'Puebla sectores viales de Medellín'

    def handle(self, *args, **kwargs):
        puntos = [
            {"nombre": "Deprimido de los Músicos", "barrio": "San Joaquín", "lat": 6.2464, "lon": -75.5881, "inundable": True, "cap": 1200},
            {"nombre": "Deprimido 80 con San Juan", "barrio": "La América", "lat": 6.2519, "lon": -75.5975, "inundable": True, "cap": 1800},
            {"nombre": "Soterrado Parques del Río", "barrio": "Guayaquil", "lat": 6.2442, "lon": -75.5786, "inundable": False, "cap": 3500},
            {"nombre": "Intercambiador Punto Cero", "barrio": "El Volador", "lat": 6.2625, "lon": -75.5772, "inundable": False, "cap": 4000},
            {"nombre": "Deprimido Feria Ganado", "barrio": "Castilla", "lat": 6.2891, "lon": -75.5714, "inundable": True, "cap": 1500},
        ]
        for p in puntos:
            SectoresCriticos.objects.get_or_create(nombre_sector=p["nombre"], defaults={
                "departamento": "ANT", "municipio": "Medellín", "barrio": p["barrio"],
                "latitud": p["lat"], "longitud": p["lon"], "es_inundable": p["inundable"], "capacidad_vehicular_max": p["cap"]
            })
        self.stdout.write("Sectores poblados")