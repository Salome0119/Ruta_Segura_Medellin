from django.contrib import admin
from .models import SectoresCriticos, ClimaActual, FlujoTiempoReal, HistoricoAccidentes, PrediccionesTrafico

admin.site.register(SectoresCriticos)
admin.site.register(ClimaActual)
admin.site.register(FlujoTiempoReal)
admin.site.register(HistoricoAccidentes)
admin.site.register(PrediccionesTrafico)