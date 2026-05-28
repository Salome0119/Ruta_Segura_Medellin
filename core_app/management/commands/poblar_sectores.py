from django.core.management.base import BaseCommand
from core_app.models import SectoresCriticos

class Command(BaseCommand):
    help = 'Puebla sectores viales críticos de Colombia con coordenadas reales'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Registrando infraestructura vial crítica de Colombia...'))

        puntos_criticos = [
            {
                "nombre": "Deprimido de los Músicos",
                "departamento": "ANT",
                "municipio": "Medellín",
                "barrio": "San Joaquín",
                "lat": 6.2464, "lon": -75.5881,
                "inundable": True, "capacidad": 1200
            },
            {
                "nombre": "Deprimido de la 80 con San Juan",
                "departamento": "ANT",
                "municipio": "Medellín",
                "barrio": "La América",
                "lat": 6.2519, "lon": -75.5975,
                "inundable": True, "capacidad": 1800
            },
            {
                "nombre": "Soterrado de Parques del Río",
                "departamento": "ANT",
                "municipio": "Medellín",
                "barrio": "Guayaquil",
                "lat": 6.2442, "lon": -75.5786,
                "inundable": False, "capacidad": 3500
            },
            {
                "nombre": "Intercambiador Vial Punto Cero",
                "departamento": "ANT",
                "municipio": "Medellín",
                "barrio": "El Volador",
                "lat": 6.2625, "lon": -75.5772,
                "inundable": False, "capacidad": 4000
            },
            {
                "nombre": "Deprimido de la Feria de Ganado",
                "departamento": "ANT",
                "municipio": "Medellín",
                "barrio": "Castilla",
                "lat": 6.2891, "lon": -75.5714,
                "inundable": True, "capacidad": 1500
            },
            {
                "nombre": "Avenida Boyacá (Calle 7) - Subalcantarada",
                "departamento": "BGT",
                "municipio": "Bogotá",
                "barrio": "Suba",
                "lat": 4.7105, "lon": -74.0695,
                "inundable": False, "capacidad": 5000
            },
            {
                "nombre": "Autopista Sur - Zona de accidentes frecuente",
                "departamento": "BGT",
                "municipio": "Bogotá",
                "barrio": "Usaquén",
                "lat": 4.7599, "lon": -74.0399,
                "inundable": False, "capacidad": 4500
            },
            {
                "nombre": "Vía de Cali - Zona centro",
                "departamento": "VAC",
                "municipio": "Cali",
                "barrio": "San Antonio",
                "lat": 3.4517, "lon": -76.5329,
                "inundable": False, "capacidad": 3000
            },
            {
                "nombre": "Deprimido frente a Barranquilla",
                "departamento": "BOL",
                "municipio": "Barranquilla",
                "barrio": "Centro",
                "lat": 10.9685, "lon": -74.8039,
                "inundable": True, "capacidad": 2000
            },
            {
                "nombre": "Zona Rosa - Bucaramanga",
                "departamento": "SAC",
                "municipio": "Bucaramanga",
                "barrio": "Zona Rosa",
                "lat": 7.1179, "lon": -73.1169,
                "inundable": False, "capacidad": 2500
            },
        ]

        for punto in puntos_criticos:
            sector, created = SectoresCriticos.objects.update_or_create(
                nombre_sector=punto["nombre"],
                defaults={
                    "departamento": punto["departamento"],
                    "municipio": punto["municipio"],
                    "barrio": punto["barrio"],
                    "latitud": punto["lat"],
                    "longitud": punto["lon"],
                    "es_inundable": punto["inundable"],
                    "capacidad_vehicular_max": punto["capacidad"]
                }
            )
            if created:
                self.stdout.write(f"[SECTOR CREADO] {punto['nombre']} - {punto['municipio']}")
            else:
                self.stdout.write(f"[SECTOR ACTUALIZADO] {punto['nombre']}")

        self.stdout.write(self.style.SUCCESS('Infraestructura vial de Colombia inicializada con éxito!'))