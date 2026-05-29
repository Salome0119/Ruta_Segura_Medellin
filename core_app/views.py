from django.db import models
import urllib.request
import json
from django.http import JsonResponse
from django.shortcuts import render
from .models import SectoresCriticos, ClimaActual, FlujoTiempoReal, HistoricoAccidentes, PrediccionesTrafico
from django.utils import timezone
from datetime import timedelta

def indice(request):
    return render(request, 'core_app/index.html')

def lista_sectores_criticos(request):
    filtro = request.GET.get('filtro', None)
    campo = request.GET.get('campo', 'barrio')
    sectores = SectoresCriticos.objects.filter(municipio='Medellín')
    
    if filtro and campo in ['departamento', 'municipio', 'barrio']:
        sectores = sectores.filter(**{f"{campo}__icontains": filtro})
        
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
    return JsonResponse({'status': 'success', 'total': len(data), 'sectores': data})

def alertas_clima_comunas(request):
    alertas = ClimaActual.objects.filter(municipio='Medellín', alerta_inundacion_activa=True)
    data = []
    for clima in alertas:
        data.append({
            'departamento': clima.departamento,
            'municipio': clima.municipio,
            'intensidad_lluvia_mm_h': clima.intensidad_lluvia,
            'alerta_inundacion_activa': clima.alerta_inundacion_activa,
            'ultima_actualizacion': clima.ultima_actualizacion.strftime('%Y-%m-%d %H:%M:%S')
        })
    return JsonResponse({'status': 'success', 'alertas_activas': len(data), 'municipios': data})

def api_flujo_tiempo_real(request):
    filtro = request.GET.get('filtro', None)
    campo = request.GET.get('campo', 'barrio')
    
    flujos = FlujoTiempoReal.objects.filter(
        fecha_hora_registro__gte=timezone.now() - timedelta(hours=1),
        sector__municipio='Medellín'
    )
    
    if filtro and campo in ['departamento', 'municipio', 'barrio']:
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
    return JsonResponse({'status': 'success', 'flujos': data})

def api_historico_accidentes(request):
    filtro = request.GET.get('filtro', None)
    campo = request.GET.get('campo', 'barrio')
    
    accidentes = HistoricoAccidentes.objects.select_related('sector').filter(sector__municipio='Medellín')
    
    if filtro and campo in ['departamento', 'municipio', 'barrio']:
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
    return JsonResponse({'status': 'success', 'total': len(data), 'accidentes': data})

def api_predicciones_trafico(request):
    filtro = request.GET.get('filtro', None)
    campo = request.GET.get('campo', 'barrio')
    
    predicciones = PrediccionesTrafico.objects.filter(
        fecha_hora_predicha__gte=timezone.now(),
        sector__municipio='Medellín'
    ).select_related('sector')
    
    if filtro and campo in ['departamento', 'municipio', 'barrio']:
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
    return JsonResponse({'status': 'success', 'predicciones': data})

def api_clima_actual(request):
    filtro = request.GET.get('filtro', None)
    campo = request.GET.get('campo', None)
    
    clima = ClimaActual.objects.filter(municipio='Medellín')
    
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
    return JsonResponse({'status': 'success', 'clima': data})

def api_rutas_seguras(request):
    filtro = request.GET.get('filtro', None)
    campo = request.GET.get('campo', None)
    
    clima_data = ClimaActual.objects.filter(municipio='Medellín', alerta_inundacion_activa=True)
    if filtro and campo in ['departamento', 'municipio']:
        clima_data = clima_data.filter(**{f"{campo}__icontains": filtro})
    
    municipios_con_alerta = clima_data.values_list('municipio', flat=True)
    sector_ids = SectoresCriticos.objects.filter(
        municipio__in=['Medellín'],
        municipio='Medellín'
    ).values_list('id', flat=True)
    
    predicciones = PrediccionesTrafico.objects.filter(
        sector_id__in=sector_ids,
        fecha_hora_predicha__gte=timezone.now(),
        sector__municipio='Medellín'
    ).select_related('sector').order_by('-probabilidad_congestion')[:50]
    
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
    return JsonResponse({'status': 'success', 'rutas_peligrosas': data})

def api_chatbot(request):
    pregunta = request.GET.get('pregunta', '').lower().strip()
    
    if not pregunta:
        respuesta = "🔍 ¿Qué necesitas?\n\n• **Zonas críticas**: sectores inundables y accidentes\n• **Tráfico RT**: estado actual vial (SIM Medellín)\n• **Predicción IA**: riesgo 2-4 horas\n• **Rutas seguras**: alternativas lluvia\n\nEjemplo: 'tráfico ahora'"
    elif any(x in pregunta for x in ['tráfico', 'trafico', 'tiempo real', 'flujo', 'camaras', 'cámaras']):
        respuesta = api_sim_trafico_real()
    elif any(x in pregunta for x in ['zonas críticas', 'críticas', 'sector crítico', 'sectores críticos', 'zonas peligrosas', 'inundables', 'inundable']):
        sectores = SectoresCriticos.objects.filter(municipio='Medellín')
        total = sectores.count()
        inundables = sectores.filter(es_inundable=True).count()
        
        top_sectores = list(sectores.filter(es_inundable=True).values('nombre_sector', 'barrio', 'capacidad_vehicular_max')[:5])
        
        respuesta = f"🔴 **Zonas Críticas - Medellín**\n\n"
        respuesta += f"**Total sectores**: {total}\n"
        respuesta += f"**Zonas inundables**: {inundables} ({round(inundables/total*100 if total > 0 else 0)}%)\n\n"
        if top_sectores:
            respuesta += "**Más críticas**:\n" + "\n".join([f"• {s['nombre_sector']} ({s['barrio']})" for s in top_sectores])
    elif any(x in pregunta for x in ['predicción', 'prediccion', 'ia', 'inteligencia artificial']):
        predicciones = PrediccionesTrafico.objects.filter(fecha_hora_predicha__gte=timezone.now(), sector__municipio='Medellín')
        alta = sum(1 for p in predicciones if p.probabilidad_congestion >= 0.7)
        media = sum(1 for p in predicciones if p.probabilidad_congestion >= 0.4) - alta
        baja = predicciones.count() - alta - media
        
        respuesta = f"🔮 **Predicción IA - Congestión**\n\n"
        respuesta += f"• **Alto riesgo (≥70%)**: {alta}\n"
        respuesta += f"• **Riesgo medio (40-69%)**: {media}\n"
        respuesta += f"• **Bajo riesgo (<40%)**: {baja}\n"
    elif any(x in pregunta for x in ['ruta', 'lluvia', 'inundación']):
        alertas = ClimaActual.objects.filter(municipio='Medellín', alerta_inundacion_activa=True).count()
        respuesta = f"🌊 **Rutas Seguras - Lluvia**\n\n**Alertas activas**: {alertas} zonas\nEvita: Deprimido Músicos, Feria Ganado"
    else:
        respuesta = "❓ No entendí. Prueba: '¿Tráfico ahora?', '¿Zonas inundables?'"
    
    return JsonResponse({'status': 'success', 'respuesta': respuesta})

def api_sim_trafico_real():
    """Obtiene tráfico en tiempo real del SIM Medellín - GeoServer WFS"""
    try:
        url = "https://geomedellin.medellin.gov.co/geoserver/wfs?service=wfs&version=2.0.0&request=GetFeature&typeName=movilidad:camaras_cctv_simm&outputFormat=application/json"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read())
        
        total = len(data.get('features', []))
        respuesta = f"🟢 **Tráfico Tiempo Real - SIM Medellín**\n\n"
        respuesta += f"**Cámaras activas**: {total}\n"
        if total > 0:
            respuesta += "\nDatos en tiempo real del Sistema Inteligente de Movilidad"
        return respuesta
    except Exception as e:
        return "🟢 **Tráfico SIM Medellín**\n\nServicio temporalmente no disponible. Usando datos simulados."

def api_traffic_sim_wfs(request):
    """Endpoint para obtener datos GeoJSON crudos del SIM"""
    try:
        url = "https://geomedellin.medellin.gov.co/geoserver/wfs?service=wfs&version=2.0.0&request=GetFeature&typeName=movilidad:camaras_cctv_simm&outputFormat=application/json"
        with urllib.request.urlopen(url, timeout=5) as response:
            return JsonResponse(json.loads(response.read()), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)