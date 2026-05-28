from django.http import JsonResponse
from django.shortcuts import render
from .models import SectoresCriticos, ClimaActual, FlujoTiempoReal, HistoricoAccidentes, PrediccionesTrafico
from django.utils import timezone
from datetime import timedelta
from django.db import models

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
    municipios_con_alerta = ClimaActual.objects.filter(municipio='Medellín', alerta_inundacion_activa=True)
    data = []
    for clima in municipios_con_alerta:
        data.append({
            'departamento': clima.departamento,
            'municipio': clima.municipio,
            'intensidad_lluvia_mm_h': clima.intensidad_lluvia,
            'alerta_inundacion_activa': clima.alerta_inundacion_activa,
            'ultima_actualizacion': clima.ultima_actualizacion.strftime('%Y-%m-%d %H:%M:%S')
        })
    return JsonResponse({'status': 'success', 'alertas_activas': len(data), 'municipios': data})

def indice(request):
    return render(request, 'core_app/index.html')

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
        municipio__in=municipios_con_alerta,
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
        respuesta = "¿Qué información necesitas? Puedo ayudarte con zonas críticas, tráfico en tiempo real, predicciones de congestión y rutas seguras de Medellín."
    elif any(x in pregunta for x in ['zonas críticas', 'críticas', 'sector crítico', 'sectores críticos', 'zonas peligrosas', 'inundables', 'inundable']):
        sectores = SectoresCriticos.objects.filter(municipio='Medellín')
        total = sectores.count()
        inundables = sectores.filter(es_inundable=True).count()
        sin_inundables = total - inundables
        porc_inundables = round((inundables / total * 100) if total > 0 else 0, 1)
        
        top_sectores = list(sectores.filter(es_inundable=True).values('nombre_sector', 'municipio', 'barrio')[:10])
        
        respuesta = f"🔴 **Zonas Críticas de Seguridad Vial - Medellín**\n\n"
        respuesta += f"• Total sectores monitoreados: {total}\n"
        respuesta += f"• Zonas inundables: {inundables} ({porc_inundables}%)\n"
        respuesta += f"• Vías estables: {sin_inundables}\n\n"
        if top_sectores:
            respuesta += "**Principales zonas inundables:**\n"
            for s in top_sectores:
                respuesta += f"  • {s['nombre_sector']} ({s['barrio']})\n"
        respuesta += "\n⚠️ Las zonas inundables tienen alto riesgo de accidentes por condiciones climáticas adversas. Evítalas en temporada lluvia."
    elif any(x in pregunta for x in ['tráfico', 'trafico', 'tiempo real', 'flujo', 'vehicular', 'vehículos', 'velocidad', 'congestión', 'congestion']):
        flujos = FlujoTiempoReal.objects.filter(
            fecha_hora_registro__gte=timezone.now() - timedelta(hours=1),
            sector__municipio='Medellín'
        )
        fluido = flujos.filter(nivel_congestion='Fluido').count()
        moderado = flujos.filter(nivel_congestion='Moderado').count()
        critico = flujos.filter(nivel_congestion='Crítico').count()
        total_flujo = flujos.count()
        
        critico_sectores = list(flujos.filter(nivel_congestion='Crítico').select_related('sector').values('sector__nombre_sector', 'sector__municipio', 'velocidad_promedio')[:5])
        
        velocidad_prom = flujos.aggregate(models.Avg('velocidad_promedio'))['velocidad_promedio__avg'] or 0
        
        respuesta = f"🟢 **Monitoreo de Tráfico en Tiempo Real - Medellín**\n\n"
        respuesta += f"• Tráfico fluido: {fluido} sectores\n"
        respuesta += f"• Tráfico moderado: {moderado} sectores\n"
        respuesta += f"• Tráfico crítico: {critico} sectores\n"
        respuesta += f"• Velocidad promedio: {float(velocidad_prom):.1f} km/h\n\n"
        if critico_sectores:
            respuesta += "**Zonas con tráfico crítico AHORA:**\n"
            for s in critico_sectores:
                respuesta += f"  • {s['sector__nombre_sector']} - {s['velocidad_promedio']} km/h\n"
        residuos = flujos.values('sector__nombre_sector').annotate(models.Avg('volumen_vehicular'))[:3]
        respuesta += "\n🔄 Los datos se actualizan cada 5 minutos desde el Sistema Inteligente de Movilidad (SIM)."
    elif any(x in pregunta for x in ['predicción', 'prediccion', 'congestion', 'congestión', 'ia', 'modelo', 'riesgo futuro', 'futuro', 'mañana', 'hoy']):
        predicciones = PrediccionesTrafico.objects.filter(
            fecha_hora_predicha__gte=timezone.now(),
            sector__municipio='Medellín'
        ).select_related('sector')
        alta = predicciones.filter(probabilidad_congestion__gte=0.7).count()
        media = predicciones.filter(probabilidad_congestion__gte=0.4, probabilidad_congestion__lt=0.7).count()
        baja = predicciones.filter(probabilidad_congestion__lt=0.4).count()
        total_pred = predicciones.count()
        
        alta_sectores = list(predicciones.filter(probabilidad_congestion__gte=0.7).values('sector__nombre_sector', 'probabilidad_congestion', 'fecha_hora_predicha', 'sector__barrio')[:5])
        
        respuesta = f"🔮 **Predicción de Congestión - Medellín**\n\n"
        respuesta += f"• Alto riesgo (≥70%): {alta} sectores\n"
        respuesta += f"• Riesgo medio (40-69%): {media} sectores\n"
        respuesta += f"• Bajo riesgo (<40%): {baja} sectores\n\n"
        if alta_sectores:
            respuesta += "**Sectores con alto riesgo de congestión:**\n"
            for s in alta_sectores:
                hora = s['fecha_hora_predicha'].strftime('%H:%M') if hasattr(s['fecha_hora_predicha'], 'strftime') else str(s['fecha_hora_predicha'])
                respuesta += f"  • {s['sector__nombre_sector']} ({s['sector__barrio']}) - {float(s['probabilidad_congestion'])*100:.0f}% a las {hora}\n"
        respuesta += "\n📊 Predicciones basadas en modelos de IA usando datos históricos y condiciones actuales del SIM."
    elif any(x in pregunta for x in ['rutas seguras', 'ruta segura', 'lluvia', 'inundación', 'inundaciones', 'segura', 'alternativa', 'evitar', 'seguro', 'seguro', 'temporada lluvia']):
        clima_alertas = ClimaActual.objects.filter(municipio='Medellín', alerta_inundacion_activa=True)
        alertas_count = clima_alertas.count()
        
        sectores_inundables = SectoresCriticos.objects.filter(municipio='Medellín', es_inundable=True)
        
        rutas_segreguras = PrediccionesTrafico.objects.filter(
            sector__municipio='Medellín',
            fecha_hora_predicha__gte=timezone.now(),
            probabilidad_congestion__lt=0.3
        ).select_related('sector').values('sector__nombre_sector', 'sector__municipio', 'probabilidad_congestion', 'sector__barrio')[:5]
        
        respuesta = f"🌊 **Rutas Seguras - Medellín (Temporada Lluvia)**\n\n"
        respuesta += f"• Alertas activas: {alertas_count} zonas\n"
        respuesta += f"• Zonas inundables: {sectores_inundables.count()}\n\n"
        if rutas_segreguras:
            respuesta += "**Rutas recomendadas (bajo riesgo hoy):**\n"
            for r in rutas_segreguras:
                respuesta += f"  • {r['sector__nombre_sector']} ({r['sector__barrio']})\n"
        respuesta += "\n✅ Verifica siempre el estado del clima antes de viajar. Puedes filtrar por barrio en la pestaña."
    elif any(x in pregunta for x in ['hola', 'hello', 'buenas', 'hi', 'hey', 'saludos']):
        respuesta = "🤖 ¡Hola! Soy tu asistente de **Ruta Segura Medellín**.\n\nPregúntame sobre:\n• Zonas críticas e inundables\n• Tráfico en tiempo real\n• Predicciones de congestión\n• Rutas seguras en lluvia\n\n💡 Tip: Usa los filtros para buscar por barrio o área específica."
    elif any(x in pregunta for x in ['gracias', 'gracias', 'thank', 'ok', 'vale', 'genial']):
        respuesta = "¡Con gusto! Si necesitas más información sobre movilidad en Medellín, aquí estoy. 🚗💨"
    elif any(x in pregunta for x in ['dónde', 'donde', 'ubicación', 'ubicacion', 'direccion', 'dirección', 'cómo llegar', 'como llegar']):
        respuesta = "🗺️ **Navegación en Medellín**\n\nEl mapa muestra en tiempo real las zonas con mayor riesgo. Haz clic en los marcadores para ver detalles.\n\nPara rutas específicas, usa Google Maps integrado con traffic layer activado."
    else:
        respuesta = "❓ No entiendo tu pregunta. Intenta con:\n• '¿Qué zonas críticas hay en Medellín?'\n• '¿Cómo está el tráfico ahora?'\n• '¿Qué predicciones hay para hoy?'\n• '¿Qué rutas son seguras en lluvia?'\n• '¿Dónde están las zonas inundables?'"

    return JsonResponse({'status': 'success', 'respuesta': respuesta})