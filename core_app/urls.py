from django.urls import path
from . import views

urlpatterns = [
    path('', views.indice, name='indice'),
    path('sectores/', views.lista_sectores_criticos, name='lista_sectores'),
    path('alertas-clima/', views.alertas_clima_comunas, name='alertas_clima'),
    path('api/flujo-tiempo-real/', views.api_flujo_tiempo_real, name='api_flujo_tiempo_real'),
    path('api/historico-accidentes/', views.api_historico_accidentes, name='api_historico_accidentes'),
    path('api/predicciones-trafico/', views.api_predicciones_trafico, name='api_predicciones_trafico'),
    path('api/clima-actual/', views.api_clima_actual, name='api_clima_actual'),
    path('api/rutas-seguras/', views.api_rutas_seguras, name='api_rutas_seguras'),
    path('api/chatbot/', views.api_chatbot, name='api_chatbot'),
    path('api/traffic-sim/', views.api_traffic_sim_wfs, name='api_traffic_sim_wfs'),
]