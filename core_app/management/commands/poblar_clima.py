from django.core.management.base import BaseCommand
from django.utils import timezone
import random
from core_app.models import ClimaActual, FlujoTiempoReal, HistoricoAccidentes, PrediccionesTrafico, SectoresCriticos
from datetime import timedelta

class Command(BaseCommand):
    help = 'Puebla datos simulados Medellín'

    def handle(self, *args, **kwargs):
        # Clima
        for mun in ["Medellín", "Bello", "Itagüí"]:
            ClimaActual.objects.get_or_create(municipio=mun, defaults={
                "departamento": "ANT", "intensidad_lluvia": random.uniform(0, 30), "alerta_inundacion_activa": random.choice([True, False])
            })
        # Flujo
        sectores = list(SectoresCriticos.objects.filter(municipio='Medellín'))
        for s in sectores:
            FlujoTiempoReal.objects.create(sector=s, fecha_hora_registro=timezone.now(), 
                velocidad_promedio=random.uniform(10, 50), volumen_vehicular=random.randint(500, 1500),
                nivel_congestion=random.choice(['Fluido', 'Moderado', 'Crítico']))
        # Accidentes
        for s in sectores:
            for _ in range(5):
                HistoricoAccidentes.objects.create(sector=s, fecha_hora=timezone.now()-timedelta(days=random.randint(1,30)),
                    gravedad=random.choice(['Solo Daños', 'Con Heridos', 'Con Muertos']),
                    tipo_vehiculo=random.choice(['Moto', 'Auto']), condicion_climatica='Lluvia ligera')
        # Predicciones
        for s in sectores:
            for h in [2, 3]:
                PrediccionesTrafico.objects.create(sector=s, fecha_hora_ejecucion=timezone.now(),
                    fecha_hora_predicha=timezone.now()+timedelta(hours=h), probabilidad_congestion=round(random.uniform(0.1, 0.8), 2))
        self.stdout.write("Datos poblados")