import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Avg, Count
from core_app.models import PrediccionesTrafico, SectoresCriticos, FlujoTiempoReal, HistoricoAccidentes

class Command(BaseCommand):
    help = 'Genera predicciones de congestión con IA para Medellín (modelo estadístico)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Generando predicciones IA para Medellín...'))
        
        sectores = list(SectoresCriticos.objects.filter(municipio='Medellín'))
        total_predicciones = 0
        
        for sector in sectores:
            # Obtener datos históricos para este sector
            flujos_historicos = FlujoTiempoReal.objects.filter(sector=sector).order_by('-fecha_hora_registro')[:20]
            accidentes_sector = HistoricoAccidentes.objects.filter(sector=sector).count()
            
            # Calcular promedio de velocidad del sector
            avg_vel = list(flujos_historicos.values_list('velocidad_promedio', flat=True))
            avg_vol = list(flujos_historicos.values_list('volumen_vehicular', flat=True))
            
            vel_prom = sum(avg_vel) / len(avg_vel) if avg_vel else 35.0
            vol_prom = sum(avg_vol) / len(avg_vol) if avg_vol else 1000
            
            # Modelo simple de IA: factores que influyen en congestión
            score = 0.3
            
            # Factor velocidad
            if vel_prom < 15:
                score += 0.4
            elif vel_prom < 30:
                score += 0.25
            elif vel_prom < 45:
                score += 0.15
            else:
                score += 0.1
                
            # Factor volumen
            if vol_prom > 1500:
                score += 0.25
            elif vol_prom > 800:
                score += 0.15
            else:
                score += 0.05
                
            # Factor historial accidentes
            if accidentes_sector > 20:
                score += 0.2
            elif accidentes_sector > 10:
                score += 0.1
            else:
                score += 0.05
                
            # Factor zona inundable
            if sector.es_inundable:
                score += 0.15
            
            for hora in [2, 3, 4]:
                prob = min(0.95, max(0.1, score + random.uniform(-0.1, 0.15)))
                
                PrediccionesTrafico.objects.create(
                    sector=sector,
                    fecha_hora_ejecucion=timezone.now(),
                    fecha_hora_predicha=timezone.now() + timedelta(hours=hora),
                    probabilidad_congestion=round(prob, 2)
                )
                total_predicciones += 1
                
            self.stdout.write(f"[IA] {sector.nombre_sector}: {score:.2f} -> predicción generada")
        
        self.stdout.write(self.style.SUCCESS(f'¡Predicciones IA generadas! Total: {total_predicciones} predicciones'))