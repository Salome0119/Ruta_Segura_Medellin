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
        this.map = L.map('map').setView([6.2442, -75.5812], 12);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
        this.updateLegend();
    },

    bindEvents() {
        const self = this;
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const tabName = this.getAttribute('data-tab');
                if (tabName) self.switchTab(tabName);
            });
        });
        document.getElementById('apply-filter')?.addEventListener('click', () => this.applyCurrentFilter());
        document.getElementById('filter-valor')?.addEventListener('keyup', (e) => {
            if (e.key === 'Enter') this.applyCurrentFilter();
        });
        this.initChatbot();
    },

    initChatbot() {
        const chatbot = document.getElementById('chatbot');
        const openBtn = document.getElementById('chatbot-open-btn');
        const closeBtn = document.getElementById('chatbot-close');
        openBtn?.addEventListener('click', () => chatbot.classList.add('chatbot-visible'));
        closeBtn?.addEventListener('click', () => chatbot.classList.remove('chatbot-visible'));
        document.getElementById('chatbot-send')?.addEventListener('click', () => this.sendChatbotMessage());
        document.getElementById('chatbot-input')?.addEventListener('keyup', (e) => {
            if (e.key === 'Enter') this.sendChatbotMessage();
        });
    },

    getFilterParams() {
        const filtro = document.getElementById('filter-valor')?.value || '';
        return { filtro, campo: 'barrio' };
    },

    applyCurrentFilter() {
        switch(this.currentTab) {
            case 'zonas-criticas': this.loadSectoresCriticos(); break;
            case 'trafico': this.loadFlujoTiempoReal(); break;
            case 'prediccion': this.loadPredicciones(); break;
            case 'lluvias': this.loadRutasSeguras(); break;
        }
    },

    switchTab(tabName) {
        this.currentTab = tabName;
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-tab') === tabName);
        });
        document.querySelectorAll('.panel').forEach(panel => {
            panel.classList.toggle('hidden', panel.id !== `panel-${tabName}`);
        });
        this.clearMarkers();
        this.applyCurrentFilter();
    },

    updateLegend() {
        document.getElementById('legend').innerHTML = `
            <div class="legend-item"><div class="legend-color" style="background:#27ae60"></div><span>Seguro</span></div>
            <div class="legend-item"><div class="legend-color" style="background:#f39c12"></div><span>Precaución</span></div>
            <div class="legend-item"><div class="legend-color" style="background:#e94560"></div><span>Peligro</span></div>
        `;
    },

    setLoading(show) {
        document.getElementById('loading').style.display = show ? 'flex' : 'none';
    },

    clearMarkers() {
        Object.values(this.markers).forEach(m => this.map.removeLayer(m));
        this.markers = {};
    },

    addMarker(lat, lng, color, popup) {
        const key = `${lat}-${lng}`;
        if (this.markers[key]) return;
        this.markers[key] = L.circleMarker([lat, lng], {
            radius: 8, fillColor: color, color: '#fff', weight: 2, fillOpacity: 0.8
        }).addTo(this.map).bindPopup(popup);
    },

    plotMarkers(items, type) {
        items.forEach(item => {
            let color = '#27ae60';
            if (type === 'sector' && item.es_inundable) color = '#e94560';
            else if (type === 'flujo' && item.nivel_congestion === 'Crítico') color = '#e94560';
            else if (type === 'flujo' && item.nivel_congestion === 'Moderado') color = '#f39c12';
            else if (type === 'prediccion' && item.probabilidad_congestion >= 0.7) color = '#e94560';
            else if (type === 'prediccion' && item.probabilidad_congestion >= 0.4) color = '#f39c12';
            this.addMarker(item.coordenadas.latitud, item.coordenadas.longitud, color, this.getPopupContent(item, type));
        });
    },

    getPopupContent(item, type) {
        switch(type) {
            case 'sector': return `<b>${item.nombre_sector}</b><br>${item.barrio || ''} | Inundable: ${item.es_inundable ? 'Sí' : 'No'}`;
            case 'flujo': return `<b>${item.sector_nombre}</b><br>Vel: ${item.velocidad_promedio} km/h`;
            case 'prediccion': return `<b>${item.sector_nombre}</b><br>Riesgo: ${(item.probabilidad_congestion*100).toFixed(0)}%`;
            default: return `<b>${item.sector_nombre}</b>`;
        }
    },

    flyToFirst(item) {
        if (item?.coordenadas?.latitud) this.map.setView([item.coordenadas.latitud, item.coordenadas.longitud], 13);
    },

    renderList(containerId, items, type) {
        const container = document.getElementById(containerId);
        container.innerHTML = items.map((item, idx) => {
            const danger = type === 'sector' ? item.es_inundable : (type === 'flujo' ? item.nivel_congestion === 'Crítico' : item.probabilidad_congestion >= 0.7);
            const warning = type === 'flujo' ? item.nivel_congestion === 'Moderado' : type === 'prediccion' && item.probabilidad_congestion >= 0.4;
            const cls = danger ? 'danger' : warning ? 'warning' : 'success';
            const badge = danger ? 'ALERTA' : warning ? 'PRECAUCIÓN' : 'OK';
            const detail = type === 'sector' ? `${item.barrio || 'N/A'} | ${item.capacidad_vehicular_max} veh` : 
                          type === 'flujo' ? `${item.velocidad_promedio} km/h | ${item.volumen_vehicular} veh` : 
                          `${(item.probabilidad_congestion*100).toFixed(0)}%`;
            return `<div class="list-item ${cls}" data-type="${type}" data-idx="${idx}">
                <div class="list-item-header"><span>${item.nombre_sector || item.sector_nombre}</span><span class="notification-badge">${badge}</span></div>
                <div class="list-item-detail">${detail}</div>
                <div class="detail-card" id="detail-${type}-${idx}" style="display:none">
                    <div class="detail-content">
                        <h4>${item.nombre_sector || item.sector_nombre}</h4>
                        ${type === 'sector' ? `<p><strong>Barrio:</strong> ${item.barrio || 'N/A'}</p><p><strong>Inundable:</strong> ${item.es_inundable ? 'Sí' : 'No'}</p>` : ''}
                        ${type === 'flujo' ? `<p><strong>Estado:</strong> ${item.nivel_congestion}</p><p><strong>Velocidad:</strong> ${item.velocidad_promedio} km/h</p>` : ''}
                        ${type === 'prediccion' ? `<p><strong>Riesgo:</strong> ${(item.probabilidad_congestion*100).toFixed(0)}%</p><p><strong>Hora:</strong> ${item.fecha_hora_predicha}</p>` : ''}
                    </div>
                </div>
            </div>`;
        }).join('');
        this.bindItemClick();
    },

    bindItemClick() {
        document.querySelectorAll('.list-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const type = item.dataset.type;
                const idx = item.dataset.idx;
                this.toggleDetail(type, idx);
            });
        });
    },

    toggleDetail(type, idx) {
        document.querySelectorAll('.detail-card').forEach(card => {
            if (card.id !== `detail-${type}-${idx}`) card.style.display = 'none';
        });
        const card = document.getElementById(`detail-${type}-${idx}`);
        if (card) card.style.display = card.style.display === 'none' ? 'block' : 'none';
    },

    async loadSectoresCriticos() {
        this.setLoading(true);
        try {
            const { filtro } = this.getFilterParams();
            const url = filtro ? `/sectores/?filtro=${encodeURIComponent(filtro)}&campo=barrio` : '/sectores/';
            const [resp, accResp] = await Promise.all([fetch(url), fetch('/api/historico-accidentes/')]);
            const data = await resp.json();
            const accData = await accResp.json();
            document.getElementById('total-sectores').textContent = data.total;
            document.getElementById('total-inundables').textContent = data.sectores.filter(s => s.es_inundable).length;
            document.getElementById('total-accidentes').textContent = accData.total;
            this.clearMarkers();
            this.renderList('sectores-list', data.sectores, 'sector');
            this.plotMarkers(data.sectores, 'sector');
            if (data.sectores.length > 0) this.flyToFirst(data.sectores[0]);
        } catch (e) { console.error(e); }
        this.setLoading(false);
    },

    async loadFlujoTiempoReal() {
        this.setLoading(true);
        try {
            const { filtro } = this.getFilterParams();
            const resp = await fetch(filtro ? `/api/flujo-tiempo-real/?filtro=${encodeURIComponent(filtro)}` : '/api/flujo-tiempo-real/');
            const data = await resp.json();
            const stats = { fluido: 0, moderado: 0, critico: 0 };
            data.flujos.forEach(f => {
                if (f.nivel_congestion === 'Fluido') stats.fluido++;
                else if (f.nivel_congestion === 'Moderado') stats.moderado++;
                else stats.critico++;
            });
            Object.entries(stats).forEach(([k,v]) => document.getElementById(`trafico-${k}`).textContent = v);
            this.clearMarkers();
            this.renderList('flujo-list', data.flujos, 'flujo');
            this.plotMarkers(data.flujos, 'flujo');
        } catch (e) { console.error(e); }
        this.setLoading(false);
    },

    async loadPredicciones() {
        this.setLoading(true);
        try {
            const { filtro } = this.getFilterParams();
            const resp = await fetch(filtro ? `/api/predicciones-trafico/?filtro=${encodeURIComponent(filtro)}` : '/api/predicciones-trafico/');
            const data = await resp.json();
            const stats = { alta: 0, media: 0, baja: 0 };
            data.predicciones.forEach(p => {
                if (p.probabilidad_congestion >= 0.7) stats.alta++;
                else if (p.probabilidad_congestion >= 0.4) stats.media++;
                else stats.baja++;
            });
            Object.entries(stats).forEach(([k,v]) => document.getElementById(`pred-${k}`).textContent = v);
            this.clearMarkers();
            this.renderList('prediccion-list', data.predicciones, 'prediccion');
            this.plotMarkers(data.predicciones, 'prediccion');
        } catch (e) { console.error(e); }
        this.setLoading(false);
    },

    async loadRutasSeguras() {
        this.setLoading(true);
        try {
            const [rutasResp, climaResp] = await Promise.all([fetch('/api/rutas-seguras/'), fetch('/api/clima-actual/')]);
            const rutasData = await rutasResp.json();
            const climaData = await climaResp.json();
            document.getElementById('alert-count').textContent = climaData.clima.filter(c => c.alerta_inundacion_activa).length;
            this.clearMarkers();
            this.renderList('rutas-seguras-list', rutasData.rutas_peligrosas, 'ruta');
        } catch (e) { console.error(e); }
        this.setLoading(false);
    },

    startAutoRefresh() {
        setInterval(() => {
            if (this.currentTab === 'zonas-criticas') this.loadSectoresCriticos();
            else if (this.currentTab === 'trafico') this.loadFlujoTiempoReal();
            else if (this.currentTab === 'prediccion') this.loadPredicciones();
            else if (this.currentTab === 'lluvias') this.loadRutasSeguras();
        }, 300000);
    },

    async sendChatbotMessage() {
        const input = document.getElementById('chatbot-input');
        const messages = document.getElementById('chatbot-messages');
        const pregunta = input.value.trim();
        if (!pregunta) return;

        const time = new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
        messages.innerHTML += `<div class="chatbot-message user">${pregunta}<span style="font-size:0.7rem;opacity:0.7;display:block;text-align:right">${time}</span></div>`;
        input.value = '';
        messages.scrollTop = messages.scrollHeight;

        try {
            const resp = await fetch(`/api/chatbot/?pregunta=${encodeURIComponent(pregunta)}`);
            const data = await resp.json();
            let r = data.respuesta.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
            messages.innerHTML += `<div class="chatbot-message bot">${r}<span style="font-size:0.7rem;opacity:0.7;display:block;text-align:right">IA • ${time}</span></div>`;
        } catch (e) {
            messages.innerHTML += `<div class="chatbot-message bot">Error. Intenta nuevamente.<span style="font-size:0.7rem;opacity:0.7;display:block;text-align:right">${time}</span></div>`;
        }
        messages.scrollTop = messages.scrollHeight;
    }
};

document.addEventListener('DOMContentLoaded', () => rutasSegurasApp.init());