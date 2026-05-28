import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from core_app.models import ClimaActual

class Command(BaseCommand):
    help = 'Simula datos meteorológicos en tiempo real para municipios de Colombia'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando extracción de datos climáticos...'))

        municipios_colombia = [
            {"departamento": "ANT", "municipio": "Medellín"},
            {"departamento": "ANT", "municipio": "Bello"},
            {"departamento": "ANT", "municipio": "Itagüí"},
            {"departamento": "BGT", "municipio": "Bogotá"},
            {"departamento": "VAC", "municipio": "Cali"},
            {"departamento": "BOL", "municipio": "Barranquilla"},
            {"departamento": "SAC", "municipio": "Bucaramanga"},
            {"departamento": "COR", "municipio": "Montería"},
            {"departamento": "QUC", "municipio": "Quito"},
            {"departamento": "HUA", "municipio": "Neiva"},
            {"departamento": "MAG", "municipio": "Santa Marta"},
            {"departamento": "CAS", "municipio": "Valledupar"},
            {"departamento": "ATL", "municipio": "Soledad"},
            {"departamento": "RIS", "municipio": "Pereira"},
            {"departamento": "CAQ", "municipio": "Florencia"},
        ]

        for item in municipios_colombia:
            intensidad = round(random.uniform(0.0, 45.0), 2)
            alerta = intensidad > 25.0

            clima, created = ClimaActual.objects.update_or_create(
                departamento=item["departamento"],
                municipio=item["municipio"],
                defaults={
                    'intensidad_lluvia': intensidad,
                    'alerta_inundacion_activa': alerta,
                    'ultima_actualizacion': timezone.now()
                }
            )

            if created:
                self.stdout.write(f"[NUEVO] {item['municipio']} ({item['departamento']}): {intensidad} mm/h.")
            else:
                self.stdout.write(f"[ACTUALIZADO] {item['municipio']}: {intensidad} mm/h.")

        self.stdout.write(self.style.SUCCESS('¡Clima de Colombia actualizado con éxito!'))