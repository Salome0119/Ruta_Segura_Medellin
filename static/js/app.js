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
            btn.addEventListener('click', function(e) {
                const tabName = this.getAttribute('data-tab');
                if (tabName) {
                    self.switchTab(tabName);
                }
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
        const filtro = document.getElementById('filter-valor')?.value || '';
        return { filtro, campo: 'barrio' };
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
            console.log('Fetching sectores:', url);
            const response = await fetch(url);
            const data = await response.json();
            console.log('Sectores data:', data);

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
            <div class="list-item ${s.es_inundable ? 'danger' : s.capacidad_vehicular_max < 50 ? 'warning' : 'success'}" data-id="${s.id}" data-type="sector">
                <div class="list-item-header">
                    <span>${s.nombre_sector}</span>
                    <span class="notification-badge ${s.es_inundable ? '' : 'hidden'}">Inundable</span>
                </div>
                <div class="list-item-detail">${s.barrio ? s.barrio + ' | ' : ''}${s.municipio} | ${s.capacidad_vehicular_max} veh</div>
                <div class="detail-card" id="detail-${s.id}" style="display:none;">
                    <div class="detail-content">
                        <h4>${s.nombre_sector}</h4>
                        <p><strong>Barrio:</strong> ${s.barrio || 'N/A'}</p>
                        <p><strong>Municipio:</strong> ${s.municipio}</p>
                        <p><strong>Capacidad:</strong> ${s.capacidad_vehicular_max} veh/h</p>
                        <p><strong>Zona Inundable:</strong> ${s.es_inundable ? 'Sí ⚠️' : 'No'}</p>
                    </div>
                </div>
            </div>
        `).join('');
        this.bindItemClick();
    },

    toggleDetailCard(id, type) {
        let cardId;
        if (type === 'sector') {
            cardId = `detail-${id}`;
        } else if (type === 'flujo') {
            cardId = `detail-flujo-${id}`;
        } else if (type === 'prediccion') {
            cardId = `detail-pred-${id}`;
        } else if (type === 'ruta') {
            cardId = `detail-ruta-${id}`;
        }
        
        // Close all other cards
        document.querySelectorAll('.detail-card').forEach(card => {
            if (card.id !== cardId) {
                card.style.display = 'none';
            }
        });
        
        const card = document.getElementById(cardId);
        if (card) {
            card.style.display = card.style.display === 'none' ? 'block' : 'none';
        }
    },

    bindItemClick() {
        document.querySelectorAll('.list-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const type = item.dataset.type;
                const id = item.dataset.type === 'sector' ? item.dataset.id : 
                          item.dataset.type === 'ruta' || item.dataset.type === 'flujo' || item.dataset.type === 'prediccion' ? 
                          item.dataset.idx : null;
                if (type && id !== null) {
                    this.toggleDetailCard(id, type);
                }
            });
        });
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
        container.innerHTML = flujos.map((f, idx) => `
            <div class="list-item ${f.nivel_congestion === 'Crítico' ? 'danger' : f.nivel_congestion === 'Moderado' ? 'warning' : 'success'}" data-type="flujo" data-idx="${idx}">
                <div class="list-item-header">
                    <span>${f.sector_nombre}</span>
                    <span class="notification-badge ${f.nivel_congestion === 'Crítico' ? '' : 'hidden'}">${f.nivel_congestion}</span>
                </div>
                <div class="list-item-detail">${f.velocidad_promedio} km/h | ${f.volumen_vehicular} veh</div>
                <div class="detail-card" id="detail-flujo-${idx}" style="display:none;">
                    <div class="detail-content">
                        <h4>${f.sector_nombre}</h4>
                        <p><strong>Velocidad:</strong> ${f.velocidad_promedio} km/h</p>
                        <p><strong>Volumen:</strong> ${f.volumen_vehicular} vehículos</p>
                        <p><strong>Estado:</strong> ${f.nivel_congestion}</p>
                        <p><strong>Última actualización:</strong> ${f.fecha_hora_registro}</p>
                    </div>
                </div>
            </div>
        `).join('');
        this.bindItemClick();
    },

    renderPrediccionList(predicciones) {
        const container = document.getElementById('prediccion-list');
        container.innerHTML = predicciones.map((p, idx) => {
            const riskClass = p.probabilidad_congestion >= 0.7 ? 'danger' : p.probabilidad_congestion >= 0.4 ? 'warning' : 'success';
            return `
                <div class="list-item ${riskClass}" data-type="prediccion" data-idx="${idx}">
                    <div class="list-item-header">
                        <span>${p.sector_nombre}</span>
                        <span class="notification-badge ${p.probabilidad_congestion >= 0.7 ? '' : 'hidden'}">${Math.round(p.probabilidad_congestion * 100)}%</span>
                    </div>
                    <div class="list-item-detail">${p.fecha_hora_predicha}</div>
                    <div class="detail-card" id="detail-pred-${idx}" style="display:none;">
                        <div class="detail-content">
                            <h4>${p.sector_nombre}</h4>
                            <p><strong>Riesgo de congestión:</strong> ${(p.probabilidad_congestion * 100).toFixed(0)}%</p>
                            <p><strong>Hora predicción:</strong> ${p.fecha_hora_predicha}</p>
                            <p><strong>Ejecutado:</strong> ${p.fecha_hora_ejecucion}</p>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        this.bindItemClick();
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
        container.innerHTML = rutas.map((r, idx) => `
            <div class="list-item danger" data-type="ruta" data-idx="${idx}">
                <div class="list-item-header">
                    <span>${r.sector_nombre}</span>
                    <span class="notification-badge">${Math.round(r.riesgo_congestion * 100)}%</span>
                </div>
                <div class="list-item-detail">${r.municipio} | Riesgo alto</div>
                <div class="detail-card" id="detail-ruta-${idx}" style="display:none;">
                    <div class="detail-content">
                        <h4>${r.sector_nombre}</h4>
                        <p><strong>Municipio:</strong> ${r.municipio}</p>
                        <p><strong>Riesgo congestión:</strong> ${(r.riesgo_congestion * 100).toFixed(0)}%</p>
                        <p><strong>Zona inundable:</strong> ${r.es_inundable ? 'Sí ⚠️' : 'No'}</p>
                    </div>
                </div>
            </div>
        `).join('');
        this.bindItemClick();
    },

    startAutoRefresh() {
        setInterval(() => {
            if (this.currentTab === 'zonas-criticas') this.loadSectoresCriticos();
            else if (this.currentTab === 'trafico') this.loadFlujoTiempoReal();
            else if (this.currentTab === 'prediccion') this.loadPredicciones();
            else if (this.currentTab === 'lluvias') this.loadRutasSeguras();
        }, 300000);
    },

    initChatbot() {
        const chatbot = document.getElementById('chatbot');
        const openBtn = document.getElementById('chatbot-open-btn');
        const closeBtn = document.getElementById('chatbot-close');
        const input = document.getElementById('chatbot-input');
        const sendBtn = document.getElementById('chatbot-send');

        if (openBtn && chatbot) {
            openBtn.addEventListener('click', () => {
                chatbot.classList.add('chatbot-visible');
            });
        }

        if (closeBtn && chatbot) {
            closeBtn.addEventListener('click', () => {
                chatbot.classList.remove('chatbot-visible');
            });
        }

        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendChatbotMessage());
        }
        
        if (input) {
            input.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') this.sendChatbotMessage();
            });
        }
    },

    async sendChatbotMessage() {
        const input = document.getElementById('chatbot-input');
        const messages = document.getElementById('chatbot-messages');
        const pregunta = input.value.trim();
        
        if (!pregunta) return;
        
        const timeNow = new Date().toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' });
        
        messages.innerHTML += `<div class="chatbot-message user">${pregunta}<span class="time-indicator">${timeNow}</span></div>`;
        input.value = '';
        messages.scrollTop = messages.scrollHeight;
        
        try {
            const response = await fetch(`/api/chatbot/?pregunta=${encodeURIComponent(pregunta)}`);
            const data = await response.json();
            
            // Parse markdown-like formatting
            let formattedResponse = data.respuesta
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\n/g, '<br>');
            
            messages.innerHTML += `<div class="chatbot-message bot">${formattedResponse}<span class="time-indicator">IA • ${timeNow}</span></div>`;
        } catch (error) {
            messages.innerHTML += `<div class="chatbot-message bot">Lo siento, hubo un error. Intenta nuevamente.<span class="time-indicator">${timeNow}</span></div>`;
        }
        messages.scrollTop = messages.scrollHeight;
    }
};

document.addEventListener('DOMContentLoaded', () => {
    rutasSegurasApp.init();
    rutasSegurasApp.initChatbot();
});