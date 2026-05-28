from django.core.management.base import BaseCommand
from core_app.models import SectoresCriticos

class Command(BaseCommand):
    help = 'Puebla sectores viales críticos de Medellín con coordenadas reales'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Registrando infraestructura vial crítica de Medellín...'))

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
                "nombre": "Avenida 10 con Calle 70",
                "departamento": "ANT",
                "municipio": "Medellín",
                "barrio": " Laureles",
                "lat": 6.2125, "lon": -75.5650,
                "inundable": False, "capacidad": 2800
            },
            {
                "nombre": "Carrera 60 con Avenida 80",
                "departamento": "ANT",
                "municipio": "Medellín",
                "barrio": "Belen",
                "lat": 6.2950, "lon": -75.6000,
                "inundable": False, "capacidad": 3200
            },
            {
                "nombre": "Avenida 30 de Agosto",
                "departamento": "ANT",
                "municipio": "Medellín",
                "barrio": "Manrique",
                "lat": 6.2687, "lon": -75.5475,
                "inundable": True, "capacidad": 1800
            },
            {
                "nombre": "Avenida Bolivariana",
                "departamento": "ANT",
                "municipio": "Medellín",
                "barrio": "Itagüí",
                "lat": 6.1889, "lon": -75.6014,
                "inundable": False, "capacidad": 4500
            },
            {
                "nombre": "Autopista Medellín - Bello",
                "departamento": "ANT",
                "municipio": "Medellín",
                "barrio": "Bello",
                "lat": 6.3369, "lon": -75.5639,
                "inundable": False, "capacidad": 5000
            },
            {
                "nombre": "Tramo Alto - Guayabal",
                "departamento": "ANT",
                "municipio": "Medellín",
                "barrio": "Guayabal",
                "lat": 6.2442, "lon": -75.5500,
                "inundable": True, "capacidad": 1500
            },
            {
                "nombre": "Avenida Las Vegas",
                "departamento": "ANT",
                "municipio": "Medellín",
                "barrio": "Robledo",
                "lat": 6.2750, "lon": -75.5800,
                "inundable": False, "capacidad": 2500
            },
            {
                "nombre": "Avenida Caldas",
                "departamento": "ANT",
                "municipio": "Medellín",
                "barrio": "Poblado",
                "lat": 6.2100, "lon": -75.5650,
                "inundable": False, "capacidad": 3500
            },
            {
                "nombre": "Carrera 43A con Avenida 135",
                "departamento": "ANT",
                "municipio": "Medellín",
                "barrio": "Envigado",
                "lat": 6.1767, "lon": -75.5933,
                "inundable": True, "capacidad": 1200
            },
            {
                "nombre": "Avenida Poblado",
                "departamento": "ANT",
                "municipio": "Medellín",
                "barrio": "Poblado",
                "lat": 6.2089, "lon": -75.5675,
                "inundable": False, "capacidad": 4000
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

        self.stdout.write(self.style.SUCCESS('Infraestructura vial de Medellín inicializada con éxito!'))