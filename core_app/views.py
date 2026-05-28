from django.http import JsonResponse
from django.shortcuts import render
from .models import SectoresCriticos, ClimaActual, FlujoTiempoReal, HistoricoAccidentes, PrediccionesTrafico
from django.utils import timezone
from datetime import datetime, timedelta

def lista_sectores_criticos(request):
    filtro = request.GET.get('filtro', None)
    campo = request.GET.get('campo', 'municipio')
    if filtro and campo in ['departamento', 'municipio']:
        sectores = SectoresCriticos.objects.filter(**{f"{campo}__icontains": filtro})
    else:
        sectores = SectoresCriticos.objects.all()
        
    data = []
    for sector in sectores:
        data.append({
            'id': sector.id,
            'nombre_sector': sector.nombre_sector,
            'departamento': sector.departamento,
            'municipio': sector.municipio,
            'barrio': sector.barrio,
            'coordenadas': {
                'latitud': float(sector.latitud),
                'longitud': float(sector.longitud),
            },
            'es_inundable': sector.es_inundable,
            'capacidad_vehicular_max': sector.capacidad_vehicular_max
        })
    return JsonResponse({'status': 'success', 'total': len(data), 'sectores': data}, safe=False)

def alertas_clima_comunas(request):
    municipios_con_alerta = ClimaActual.objects.filter(alerta_inundacion_activa=True)
    data = []
    for clima in municipios_con_alerta:
        data.append({
            'departamento': clima.departamento,
            'municipio': clima.municipio,
            'intensidad_lluvia_mm_h': clima.intensidad_lluvia,
            'alerta_inundacion_activa': clima.alerta_inundacion_activa,
            'ultima_actualizacion': clima.ultima_actualizacion.strftime('%Y-%m-%d %H:%M:%S')
        })
    return JsonResponse({'status': 'success', 'alertas_activas': len(data), 'municipios': data}, safe=False)

def indice(request):
    return render(request, 'core_app/index.html')

def api_flujo_tiempo_real(request):
    filtro = request.GET.get('filtro', None)
    campo = request.GET.get('campo', None)
    
    flujos = FlujoTiempoReal.objects.filter(fecha_hora_registro__gte=timezone.now() - timedelta(hours=1))
    
    if filtro and campo in ['departamento', 'municipio']:
        flujos = flujos.filter(**{f"sector__{campo}__icontains": filtro})
    
    data = []
    for flujo in flujos.select_related('sector'):
        data.append({
            'id': flujo.id,
            'sector_id': flujo.sector.id,
            'sector_nombre': flujo.sector.nombre_sector,
            'departamento': flujo.sector.departamento,
            'municipio': flujo.sector.municipio,
            'coordenadas': {
                'latitud': float(flujo.sector.latitud),
                'longitud': float(flujo.sector.longitud),
            },
            'fecha_hora_registro': flujo.fecha_hora_registro.strftime('%Y-%m-%d %H:%M:%S'),
            'velocidad_promedio': flujo.velocidad_promedio,
            'volumen_vehicular': flujo.volumen_vehicular,
            'nivel_congestion': flujo.nivel_congestion
        })
    return JsonResponse({'status': 'success', 'flujos': data}, safe=False)

def api_historico_accidentes(request):
    filtro = request.GET.get('filtro', None)
    campo = request.GET.get('campo', None)
    
    accidentes = HistoricoAccidentes.objects.select_related('sector').all()
    
    if filtro and campo in ['departamento', 'municipio']:
        accidentes = accidentes.filter(**{f"sector__{campo}__icontains": filtro})
    
    accidentes = accidentes[:100]
    
    data = []
    for accidente in accidentes:
        data.append({
            'id': accidente.id,
            'sector_id': accidente.sector.id if accidente.sector else None,
            'sector_nombre': accidente.sector.nombre_sector if accidente.sector else 'Desconocido',
            'municipio': accidente.sector.municipio if accidente.sector else 'Desconocido',
            'departamento': accidente.sector.departamento if accidente.sector else 'Desconocido',
            'coordenadas': {
                'latitud': float(accidente.sector.latitud) if accidente.sector else None,
                'longitud': float(accidente.sector.longitud) if accidente.sector else None,
            },
            'fecha_hora': accidente.fecha_hora.strftime('%Y-%m-%d %H:%M:%S'),
            'gravedad': accidente.gravedad,
            'tipo_vehiculo': accidente.tipo_vehiculo,
            'condicion_climatica': accidente.condicion_climatica
        })
    return JsonResponse({'status': 'success', 'total': len(data), 'accidentes': data}, safe=False)

def api_predicciones_trafico(request):
    filtro = request.GET.get('filtro', None)
    campo = request.GET.get('campo', None)
    
    predicciones = PrediccionesTrafico.objects.filter(fecha_hora_predicha__gte=timezone.now()).select_related('sector')
    
    if filtro and campo in ['departamento', 'municipio']:
        predicciones = predicciones.filter(**{f"sector__{campo}__icontains": filtro})
    
    predicciones = predicciones[:100]
    
    data = []
    for pred in predicciones:
        data.append({
            'id': pred.id,
            'sector_id': pred.sector.id,
            'sector_nombre': pred.sector.nombre_sector,
            'departamento': pred.sector.departamento,
            'municipio': pred.sector.municipio,
            'coordenadas': {
                'latitud': float(pred.sector.latitud),
                'longitud': float(pred.sector.longitud),
            },
            'fecha_hora_ejecucion': pred.fecha_hora_ejecucion.strftime('%Y-%m-%d %H:%M:%S'),
            'fecha_hora_predicha': pred.fecha_hora_predicha.strftime('%Y-%m-%d %H:%M:%S'),
            'probabilidad_congestion': float(pred.probabilidad_congestion)
        })
    return JsonResponse({'status': 'success', 'predicciones': data}, safe=False)

def api_clima_actual(request):
    filtro = request.GET.get('filtro', None)
    campo = request.GET.get('campo', None)
    
    clima = ClimaActual.objects.all()
    
    if filtro and campo in ['departamento', 'municipio']:
        clima = clima.filter(**{f"{campo}__icontains": filtro})
    
    data = []
    for c in clima:
        data.append({
            'departamento': c.departamento,
            'municipio': c.municipio,
            'intensidad_lluvia_mm_h': c.intensidad_lluvia,
            'alerta_inundacion_activa': c.alerta_inundacion_activa,
            'ultima_actualizacion': c.ultima_actualizacion.strftime('%Y-%m-%d %H:%M:%S')
        })
    return JsonResponse({'status': 'success', 'clima': data}, safe=False)

def api_rutas_seguras(request):
    filtro = request.GET.get('filtro', None)
    campo = request.GET.get('campo', None)
    
    clima_data = ClimaActual.objects.filter(alerta_inundacion_activa=True)
    if filtro and campo in ['departamento', 'municipio']:
        clima_data = clima_data.filter(**{f"{campo}__icontains": filtro})
    
    municipios_con_alerta = clima_data.values_list('municipio', flat=True)
    sector_ids = SectoresCriticos.objects.filter(municipio__in=municipios_con_alerta).values_list('id', flat=True)
    
    predicciones = PrediccionesTrafico.objects.filter(sector_id__in=sector_ids, fecha_hora_predicha__gte=timezone.now()).select_related('sector').order_by('-probabilidad_congestion')[:50]
    
    data = []
    for pred in predicciones:
        data.append({
            'sector_id': pred.sector.id,
            'sector_nombre': pred.sector.nombre_sector,
            'departamento': pred.sector.departamento,
            'municipio': pred.sector.municipio,
            'coordenadas': {
                'latitud': float(pred.sector.latitud),
                'longitud': float(pred.sector.longitud),
            },
            'riesgo_congestion': float(pred.probabilidad_congestion),
            'es_inundable': pred.sector.es_inundable
        })
    return JsonResponse({'status': 'success', 'rutas_peligrosas': data}, safe=False)