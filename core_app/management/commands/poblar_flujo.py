import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from core_app.models import FlujoTiempoReal, SectoresCriticos

class Command(BaseCommand):
    help = 'Simula flujo de tráfico en tiempo real de Medellín'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Simulando datos de tráfico de Medellín...'))
        
        sectores = list(SectoresCriticos.objects.filter(municipio='Medellín'))
        
        for sector in sectores:
            for i in range(3):
                FlujoTiempoReal.objects.create(
                    sector=sector,
                    fecha_hora_registro=timezone.now() - timezone.timedelta(minutes=i*5),
                    velocidad_promedio=round(random.uniform(5, 60), 1),
                    volumen_vehicular=random.randint(100, 2000),
                    nivel_congestion=random.choice(['Fluido', 'Moderado', 'Crítico'])
                )
                self.stdout.write(f"[FLUJO] {sector.nombre_sector}: {random.randint(100, 2000)} veh")
        
        self.stdout.write(self.style.SUCCESS('Datos de tráfico de Medellín generados!'))