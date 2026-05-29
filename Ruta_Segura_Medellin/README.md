# 🗺️ Ruta Segura Medellín - Backend API

![Django](https://img.shields.io/badge/Django-3.2-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![MySQL / MariaDB](https://img.shields.io/badge/MySQL-XAMPP-4479A1?style=for-the-badge&logo=mysql&logoColor=white)

**Ruta Segura Medellín** es un sistema backend centralizado diseñado para mitigar los riesgos de movilidad y gestión ambiental en los puntos viales más vulnerables de la ciudad de Medellín. La plataforma unifica datos de infraestructura geográfica con un motor automatizado de simulación climática y de tráfico, ofreciendo alertas tempranas en tiempo real para evitar incidentes en deprimidos y corredores críticos de alta densidad.

---

## 🚀 Características y Arquitectura del Sistema

El backend está construido sobre un modelo relacional normalizado que conecta un **Eje Geográfico** base con múltiples módulos dinámicos:

* **Eje Geográfico:** Puntos e infraestructura crítica (coordenadas exactas, capacidad vehicular y susceptibilidad a inundaciones) indexados por comunas y barrios.
* **Módulo Meteorológico (Scraping Automatizado):** Sistema de alerta temprana automatizado que calcula la intensidad de lluvia en mm/h para las 16 comunas de Medellín, activando banderas lógicas de evacuación (`alerta_inundacion_activa`) si los niveles superan los 25.0 mm/h.
* **Módulo de Tránsito:** Estructura lista para procesar el flujo vehicular, velocidad promedio y niveles de congestión.
* **API REST (JSON Ready):** Endpoints limpios optimizados con filtros dinámicos (parámetros por URL) para ser consumidos por interfaces de mapas o tableros de control en el frontend.

---

## 🛠️ Requisitos e Instalación Local

Sigue estos pasos para desplegar el entorno de desarrollo local utilizando XAMPP:

### 1. Clonar el repositorio e ingresar a la carpeta
```bash
git clone [https://github.com/tu_usuario/ruta_segura_medellin.git](https://github.com/tu_usuario/ruta_segura_medellin.git)
cd ruta_segura_medellin
