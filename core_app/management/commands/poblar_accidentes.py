import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from core_app.models import HistoricoAccidentes, SectoresCriticos

class Command(BaseCommand):
    help = 'Simula histórico de accidentes de Medellín'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Simulando histórico de accidentes de Medellín...'))
        
        sectores = list(SectoresCriticos.objects.filter(municipio='Medellín'))
        gravedades = ['Solo Daños', 'Con Heridos', 'Con Muertos']
        vehiculos = ['Moto', 'Auto', 'Peatón', 'Bicicleta']
        climas = ['Seco', 'Lluvia ligera', 'Lluvia intensa']
        
        for sector in sectores:
            for i in range(10):
                HistoricoAccidentes.objects.create(
                    sector=sector,
                    fecha_hora=timezone.now() - timezone.timedelta(days=random.randint(1, 30)),
                    gravedad=random.choice(gravedades),
                    tipo_vehiculo=random.choice(vehiculos),
                    condicion_climatica=random.choice(climas)
                )
                self.stdout.write(f"[ACCIDENTE] {sector.nombre_sector}")
        
        self.stdout.write(self.style.SUCCESS('Histórico de accidentes de Medellín generado!'))