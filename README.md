# 🚀 RUTA SEGURA MEDELLÍN: LA REVOLUCIÓN DE LA RESILIENCIA URBANA A TRAVÉS DEL CÓDIGO

**Ruta Segura Medellín** no es simplemente una base de datos o un sitio web convencional; representa un hito en la ingeniería de software aplicada al desarrollo de ciudades inteligentes (*Smart Cities*). Este ecosistema backend resuelve de raíz problemáticas estructurales e históricas de la capital antioqueña, transformando datos abiertos en un sistema automatizado de alerta temprana.

Lo que este proyecto soluciona combina una profunda comprensión del entorno urbano con un despliegue arquitectónico robusto, seguro y altamente escalable:

---

### 1. El Fin del Aislamiento de Datos: Unificación del Eje Geográfico y Telemetría

Históricamente, los datos de movilidad y el monitoreo ambiental en Medellín han operado en silos tecnológicos completamente aislados. Las autoridades de tránsito vigilan los flujos vehiculares mientras los sensores meteorológicos registran las precipitaciones de forma independiente, careciendo de una sincronización programática en tiempo real entre ambas variables.

El sistema soluciona esta fragmentación mediante un **modelo relacional normalizado** inyectado en MariaDB/MySQL a través del entorno local XAMPP. El núcleo de la solución radica en el desacoplamiento y enlace dinámico de datos:

* **El Eje Geográfico Base:** Estructurado rigurosamente en la tabla `sectores_criticos`, almacena con precisión georreferenciada la ubicación (`latitud`, `longitud`) de puntos con alta vulnerabilidad hidráulica y vial, tales como el deprimido de Los Músicos (Comuna 11 - Laureles) o el de la Feria de Ganado (Comuna 5 - Castilla).
* **Mapeo Automatizado por URL:** Mediante la configuración limpia de rutas en `core_app/urls.py`, la API expone el endpoint `/api/sectores/`. Este componente implementa filtros dinámicos basados en *Query Params* (parámetros de consulta en la URL como `?comuna=Laureles`), optimizando las consultas de la base de datos mediante índices activos para que el frontend renderice únicamente la información requerida sin sobrecargar el canal de comunicación.

---

### 2. De la Respuesta Reactiva a la Alerta Preventiva Automatizada

Tradicionalmente, la gestión del riesgo en los soterrados viales de la ciudad ha sido reactiva: las acciones de contingencia y los cierres de vías se activan únicamente cuando un vehículo ya ha quedado atrapado por una inundación relámpago.

Este software altera por completo ese paradigma, migrando el modelo hacia la prevención automatizada mediante código asíncrono y tareas en segundo plano:

* **Comandos de Consola Personalizados (*Custom Management Commands*):** El equipo desarrolló scripts independientes (`poblar_clima`) heredados de la clase `BaseCommand` de Django. Estos scripts ejecutan ciclos de extracción y actualización masiva de la tabla `clima_actual` para las 16 comunas de forma simultánea.
* **Lógica Predictiva y Banderas de Evacuación:** El backend evalúa constantemente la intensidad de lluvia en milímetros por hora ($mm/h$). Si el script detecta que las precipitaciones superan el umbral crítico de seguridad de **25.0 mm/h**, el sistema activa de forma inmediata y automatizada una bandera lógica de evacuación (`alerta_inundacion_activa = True`).
* **Consumo Frontend-Ready:** Este cambio de estado impacta instantáneamente el endpoint `/api/alertas-clima/`, sirviendo una estructura limpia en formato JSON plano con código de estado HTTP 200. Esto permite que el mapa interactivo del frontend ilumine alertas visuales rojas y trace desvíos preventivos **minutos antes** de que el deprimido sufra un colapso hidráulico, salvando vidas y evitando pérdidas materiales.

---

### 3. Democratización del Acceso: Persistencia Offline y Cero Fricción

En escenarios de emergencia vial o movilidad urbana, la conectividad a internet es una variable altamente inestable. Los conductores suelen perder cobertura de datos móviles al transitar por estructuras subterráneas, soterrados profundos o zonas de alta densidad edilicia, lo que inutilizaría cualquier aplicación web convencional en el momento más crítico.

El proyecto soluciona la exclusión digital convirtiendo el sistema en una **PWA (Progressive Web App)** de alto rendimiento, cuya lógica está integrada directamente en los archivos estáticos de la arquitectura:

* **El Motor Intermediario (`service-worker.js`):** Corriendo en un hilo de procesamiento aislado en segundo plano, intercepta todas las peticiones de red mediante el evento `fetch`. Implementa una estrategia de almacenamiento **"Cache First"** (Primero Caché), guardando localmente la hoja de estilos (`style.css`), los scripts de control (`app.js`) y los recursos gráficos. Si el usuario pierde la señal por completo, el Service Worker sirve los archivos desde la memoria del dispositivo en milisegundos, manteniendo la interfaz del mapa operativa.
* **Aislamiento de Rutas Críticas:** El código del Service Worker cuenta con reglas de filtrado que excluyen explícitamente las llamadas que contengan la ruta `/api/`. Esto garantiza que los datos meteorológicos y de tráfico nunca se vuelvan obsoletos en la caché; si hay red, se consume la telemetría fresca del backend; si no la hay, se despliega una pantalla de contingencia controlada (`offline.html`) en lugar del error genérico de conectividad del navegador.
* **Instalación sin Barreras de Almacenamiento:** Mediante el archivo de configuración `manifest.json` enlazado en los `Meta Tags` del HTML principal, el navegador reconoce la plataforma como un software instalable. Configurado bajo el modo de visualización `standalone`, remueve la barra de direcciones y las herramientas del navegador al ejecutarse, ofreciendo una experiencia inmersiva de aplicación móvil nativa sin consumir el almacenamiento interno de un empaquetado tradicional para tiendas (Play Store o App Store).

---

### 🔍 Conclusión de Arquitectura

El valor de este ecosistema radica en que el código escrito no es estático; es un motor vivo que interactúa con la realidad climática de Medellín. Al abstraer la complejidad de las consultas relacionales mediante el **ORM de Django** para mitigar vulnerabilidades como la inyección SQL, y al estructurar entidades listas para la analítica (a través de la tabla `predicciones_trafico`), el equipo ha diseñado una arquitectura limpia, robusta y escalable preparada para los desafíos de la movilidad del futuro.
