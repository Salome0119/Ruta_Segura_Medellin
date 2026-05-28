const rutasSegurasApp = {
    map: null,
    markers: {},
    currentTab: 'zonas-criticas',
    refreshInterval: null,

    init() {
        this.initMap();
        this.bindEvents();
        this.loadSectoresCriticos();
        this.startAutoRefresh();
    },

    initMap() {
        this.map = L.map('map').setView([4.5708, -74.2973], 6);
        
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        this.updateLegend();
    },

    bindEvents() {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        document.getElementById('apply-filter').addEventListener('click', () => {
            this.applyCurrentFilter();
        });

        document.getElementById('filter-valor').addEventListener('keyup', (e) => {
            if (e.key === 'Enter') this.applyCurrentFilter();
        });
    },

    getFilterParams() {
        const filtro = document.getElementById('filter-valor').value;
        const campo = document.getElementById('filter-tipo').value;
        return { filtro, campo };
    },

    applyCurrentFilter() {
        switch(this.currentTab) {
            case 'zonas-criticas':
                this.loadSectoresCriticos();
                break;
            case 'trafico':
                this.loadFlujoTiempoReal();
                break;
            case 'prediccion':
                this.loadPredicciones();
                break;
            case 'lluvias':
                this.loadRutasSeguras();
                break;
        }
    },

    switchTab(tabName) {
        this.currentTab = tabName;
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });
        document.querySelectorAll('.panel').forEach(panel => {
            panel.classList.toggle('hidden', panel.id !== `panel-${tabName}`);
        });

        this.clearMarkers();

        switch(tabName) {
            case 'zonas-criticas':
                this.loadSectoresCriticos();
                break;
            case 'trafico':
                this.loadFlujoTiempoReal();
                break;
            case 'prediccion':
                this.loadPredicciones();
                break;
            case 'lluvias':
                this.loadRutasSeguras();
                break;
        }
    },

    updateLegend() {
        const legend = document.getElementById('legend');
        legend.innerHTML = `
            <div class="legend-item"><div class="legend-color" style="background:#27ae60"></div> <span>Seguro</span></div>
            <div class="legend-item"><div class="legend-color" style="background:#f39c12"></div> <span>Precaución</span></div>
            <div class="legend-item"><div class="legend-color" style="background:#e94560"></div> <span>Peligro</span></div>
        `;
    },

    setLoading(show) {
        document.getElementById('loading').style.display = show ? 'flex' : 'none';
    },

    clearMarkers() {
        Object.values(this.markers).forEach(marker => this.map.removeLayer(marker));
        this.markers = {};
    },

    addMarker(lat, lng, color, popupContent) {
        const key = `${lat}-${lng}`;
        if (this.markers[key]) return;

        const marker = L.circleMarker([lat, lng], {
            radius: 8,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(this.map).bindPopup(popupContent);

        this.markers[key] = marker;
        return marker;
    },

    async loadSectoresCriticos() {
        this.setLoading(true);
        try {
            const { filtro, campo } = this.getFilterParams();
            const url = filtro ? `/sectores/?filtro=${encodeURIComponent(filtro)}&campo=${campo}` : '/sectores/';
            const response = await fetch(url);
            const data = await response.json();

            document.getElementById('total-sectores').textContent = data.total;
            document.getElementById('total-inundables').textContent = data.sectores.filter(s => s.es_inundable).length;

            this.clearMarkers();
            this.renderSectoresList(data.sectores);

            const responseAcc = await fetch('/api/historico-accidentes/');
            const accData = await responseAcc.json();
            document.getElementById('total-accidentes').textContent = accData.total;

            this.plotMarkers(data.sectores, 'sector');

            if (data.sectores.length > 0) this.flyToFirst(data.sectores[0]);

        } catch (error) {
            console.error('Error loading sectores:', error);
        } finally {
            this.setLoading(false);
        }
    },

    plotMarkers(items, type) {
        items.forEach(item => {
            let color = '#27ae60';
            if (type === 'sector' && item.es_inundable) color = '#e94560';
            else if (type === 'flujo' && item.nivel_congestion === 'Crítico') color = '#e94560';
            else if (type === 'flujo' && item.nivel_congestion === 'Moderado') color = '#f39c12';
            else if (type === 'prediccion' && item.probabilidad_congestion >= 0.7) color = '#e94560';
            else if (type === 'prediccion' && item.probabilidad_congestion >= 0.4) color = '#f39c12';

            this.addMarker(
                item.coordenadas.latitud,
                item.coordenadas.longitud,
                color,
                this.getPopupContent(item, type)
            );
        });
    },

    getPopupContent(item, type) {
        switch(type) {
            case 'sector':
                return `<b>${item.nombre_sector}</b><br>${item.municipio}, ${item.departamento}<br>Inundable: ${item.es_inundable ? 'Sí' : 'No'}`;
            case 'flujo':
                return `<b>${item.sector_nombre}</b><br>Velocidad: ${item.velocidad_promedio} km/h<br>Volumen: ${item.volumen_vehicular} veh`;
            case 'prediccion':
                return `<b>${item.sector_nombre}</b><br>Riesgo: ${(item.probabilidad_congestion * 100).toFixed(0)}%<br>Predicción: ${item.fecha_hora_predicha}`;
            default:
                return `<b>${item.sector_nombre}</b>`;
        }
    },

    flyToFirst(item) {
        if (item.coordenadas.latitud && item.coordenadas.longitud) {
            this.map.setView([item.coordenadas.latitud, item.coordenadas.longitud], 12);
        }
    },

    renderSectoresList(sectores) {
        const container = document.getElementById('sectores-list');
        container.innerHTML = sectores.map(s => `
            <div class="list-item ${s.es_inundable ? 'danger' : s.capacidad_vehicular_max < 50 ? 'warning' : 'success'}">
                <div class="list-item-header">${s.nombre_sector}</div>
                <div class="list-item-detail">${s.municipio}, ${s.departamento} | Capacidad: ${s.capacidad_vehicular_max} veh</div>
            </div>
        `).join('');
    },

    async loadFlujoTiempoReal() {
        this.setLoading(true);
        try {
            const { filtro, campo } = this.getFilterParams();
            const url = filtro ? `/api/flujo-tiempo-real/?filtro=${encodeURIComponent(filtro)}&campo=${campo}` : '/api/flujo-tiempo-real/';
            const response = await fetch(url);
            const data = await response.json();

            const stats = { fluido: 0, moderado: 0, critico: 0 };
            data.flujos.forEach(f => {
                if (f.nivel_congestion === 'Fluido') stats.fluido++;
                else if (f.nivel_congestion === 'Moderado') stats.moderado++;
                else stats.critico++;
            });

            document.getElementById('trafico-fluido').textContent = stats.fluido;
            document.getElementById('trafico-moderado').textContent = stats.moderado;
            document.getElementById('trafico-critico').textContent = stats.critico;

            this.clearMarkers();
            this.renderFlujoList(data.flujos);
            this.plotMarkers(data.flujos, 'flujo');

            if (data.flujos.length > 0) this.flyToFirst(data.flujos[0]);

        } catch (error) {
            console.error('Error loading flujo:', error);
        } finally {
            this.setLoading(false);
        }
    },

    renderFlujoList(flujos) {
        const container = document.getElementById('flujo-list');
        container.innerHTML = flujos.map(f => `
            <div class="list-item ${f.nivel_congestion === 'Crítico' ? 'danger' : f.nivel_congestion === 'Moderado' ? 'warning' : 'success'}">
                <div class="list-item-header">${f.sector_nombre}</div>
                <div class="list-item-detail">${f.municipio}, ${f.departamento} | ${f.velocidad_promedio} km/h | ${f.nivel_congestion}</div>
            </div>
        `).join('');
    },

    async loadPredicciones() {
        this.setLoading(true);
        try {
            const { filtro, campo } = this.getFilterParams();
            const url = filtro ? `/api/predicciones-trafico/?filtro=${encodeURIComponent(filtro)}&campo=${campo}` : '/api/predicciones-trafico/';
            const response = await fetch(url);
            const data = await response.json();

            const stats = { alta: 0, media: 0, baja: 0 };
            data.predicciones.forEach(p => {
                if (p.probabilidad_congestion >= 0.7) stats.alta++;
                else if (p.probabilidad_congestion >= 0.4) stats.media++;
                else stats.baja++;
            });

            document.getElementById('pred-alta').textContent = stats.alta;
            document.getElementById('pred-media').textContent = stats.media;
            document.getElementById('pred-baja').textContent = stats.baja;

            this.clearMarkers();
            this.renderPrediccionList(data.predicciones);
            this.plotMarkers(data.predicciones, 'prediccion');

            if (data.predicciones.length > 0) this.flyToFirst(data.predicciones[0]);

        } catch (error) {
            console.error('Error loading predicciones:', error);
        } finally {
            this.setLoading(false);
        }
    },

    renderPrediccionList(predicciones) {
        const container = document.getElementById('prediccion-list');
        container.innerHTML = predicciones.map(p => {
            const riskClass = p.probabilidad_congestion >= 0.7 ? 'danger' : p.probabilidad_congestion >= 0.4 ? 'warning' : 'success';
            return `
                <div class="list-item ${riskClass}">
                    <div class="list-item-header">${p.sector_nombre}</div>
                    <div class="list-item-detail">${p.municipio}, ${p.departamento} | Riesgo: ${(p.probabilidad_congestion * 100).toFixed(0)}% | ${p.fecha_hora_predicha}</div>
                </div>
            `;
        }).join('');
    },

    async loadRutasSeguras() {
        this.setLoading(true);
        try {
            const { filtro, campo } = this.getFilterParams();
            const [rutasResp, climaResp] = await Promise.all([
                fetch(`/api/rutas-seguras/?filtro=${encodeURIComponent(filtro)}&campo=${campo}`),
                fetch('/api/clima-actual/')
            ]);

            const rutasData = await rutasResp.json();
            const climaData = await climaResp.json();

            document.getElementById('alert-count').textContent = climaData.clima.filter(c => c.alerta_inundacion_activa).length;

            this.clearMarkers();
            this.renderRutasList(rutasData.rutas_peligrosas);

            rutasData.rutas_peligrosas.forEach(ruta => {
                this.addMarker(
                    ruta.coordenadas.latitud,
                    ruta.coordenadas.longitud,
                    '#e94560',
                    `<b>Zona de Riesgo</b><br>${ruta.sector_nombre}<br>Riesgo congestión: ${(ruta.riesgo_congestion * 100).toFixed(0)}%`
                );
            });

            if (rutasData.rutas_peligrosas.length > 0) this.flyToFirst(rutasData.rutas_peligrosas[0]);

        } catch (error) {
            console.error('Error loading rutas seguras:', error);
        } finally {
            this.setLoading(false);
        }
    },

    renderRutasList(rutas) {
        const container = document.getElementById('rutas-seguras-list');
        if (rutas.length === 0) {
            container.innerHTML = '<p class="list-item-detail">No hay rutas peligrosas registradas en este momento.</p>';
            return;
        }
        container.innerHTML = rutas.map(r => `
            <div class="list-item danger">
                <div class="list-item-header">${r.sector_nombre}</div>
                <div class="list-item-detail">${r.municipio}, ${r.departamento} | Riesgo: ${(r.riesgo_congestion * 100).toFixed(0)}%</div>
            </div>
        `).join('');
    },

    startAutoRefresh() {
        setInterval(() => {
            if (this.currentTab === 'trafico') this.loadFlujoTiempoReal();
            else if (this.currentTab === 'prediccion') this.loadPredicciones();
            else if (this.currentTab === 'lluvias') this.loadRutasSeguras();
        }, 300000);
    }
};

document.addEventListener('DOMContentLoaded', () => rutasSegurasApp.init());