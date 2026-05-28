import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from core_app.models import PrediccionesTrafico, SectoresCriticos

class Command(BaseCommand):
    help = 'Simula predicciones de congestión con IA'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Simulando predicciones de IA...'))
        
        sectores = list(SectoresCriticos.objects.all())
        
        for sector in sectores:
            for hora in [2, 3, 4]:
                PrediccionesTrafico.objects.create(
                    sector=sector,
                    fecha_hora_ejecucion=timezone.now(),
                    fecha_hora_predicha=timezone.now() + timezone.timedelta(hours=hora),
                    probabilidad_congestion=round(random.uniform(0.1, 0.95), 2)
                )
                self.stdout.write(f"[PREDICCIÓN] {sector.nombre_sector}: +{hora}h - {random.uniform(0.1, 0.95):.2f}")
        
        self.stdout.write(self.style.SUCCESS('Predicciones generadas!'))