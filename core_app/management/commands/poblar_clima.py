import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from core_app.models import ClimaActual

class Command(BaseCommand):
    help = 'Simula datos meteorológicos en tiempo real para Medellín'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando extracción de datos climáticos de Medellín...'))

        # Comunas de Medellín con riesgo pluvial diferente
        comunas_medellin = [
            {"departamento": "ANT", "municipio": "Medellín"},
            {"departamento": "ANT", "municipio": "Bello"},
            {"departamento": "ANT", "municipio": "Itagüí"},
            {"departamento": "ANT", "municipio": "Envigado"},
            {"departamento": "ANT", "municipio": "Sabaneta"},
            {"departamento": "ANT", "municipio": "Caldas"},
        ]

        for item in comunas_medellin:
            # Simular lluvia realista (mayor en zonas altas)
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
                self.stdout.write(f"[NUEVO] {item['municipio']}: {intensidad} mm/h.")
            else:
                self.stdout.write(f"[ACTUALIZADO] {item['municipio']}: {intensidad} mm/h.")

        self.stdout.write(self.style.SUCCESS('¡Clima de Medellín actualizado!'))