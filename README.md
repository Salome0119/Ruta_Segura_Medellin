Aquí tienes la sección de **Requisitos e Instalación Local** completamente reestructurada, ampliada y detallada paso a paso. Se agregaron las explicaciones conceptuales de lo que hace cada comando técnico para que el documento mantenga un estándar profesional en tu repositorio, explicando claramente el aprovisionamiento del entorno aislado y el despliegue del servidor.

---

## 🛠️ Requisitos del Sistema y Guía de Instalación Local

Para garantizar un despliegue exitoso en tu entorno local, el sistema requiere la previa instalación de **Python 3.11** y la suite de servidores locales **XAMPP (con MariaDB/MySQL)**. Sigue minuciosamente cada una de las fases descritas a continuación para configurar la base de datos, inicializar el entorno virtual aislado y ejecutar las tareas de aprovisionamiento de datos viales y meteorológicos.

---

### Fase 1: Clonación del Repositorio y Acceso al Espacio de Trabajo

El primer paso consiste en descargar una réplica exacta del código fuente de la API desde el repositorio remoto en la nube (GitHub) hacia tu almacenamiento local, e ingresar al directorio raíz del proyecto mediante la consola de comandos.

1. Abre tu terminal favorita (se recomienda **Git Bash** o **PowerShell** en entornos Windows).
2. Ejecuta el comando de clonación e ingresa a la carpeta del proyecto:
```bash
git clone https://github.com/tu_usuario/ruta_segura_medellin.git
cd ruta_segura_medellin

```



```
   > 🔍 **¿Qué hace esto?** El comando `git clone` descarga todo el historial de versiones, ramas y archivos de la aplicación. Al hacer `cd`, apuntas la terminal directamente a la raíz de la arquitectura, permitiéndote ejecutar scripts y comandos de Django.

---

### Fase 2: Configuración e Inicialización del Entorno Virtual Aislado

Para prevenir conflictos de dependencias, colisiones de versiones o problemas con librerías globales de Python instaladas en el sistema operativo, es de carácter obligatorio inicializar y activar un entorno virtual exclusivo (`venv`) para el proyecto.

1. **Creación del entorno virtual (si no está creado):**
   ```bash
   python -m venv venv

```

2. **Activación del entorno aislado:**
* **En Windows (Git Bash / MINGW64):**
```bash
source venv/Scripts/activate

```





```
   * **En Windows (PowerShell con permisos activos):**
     ```bash
     .\venv\Scripts\Activate.ps1

```

* **En Linux / macOS:**
```bash
source venv/bin/activate

```



```
   > 💡 **Validación Visual:** Sabrás que el entorno se activó correctamente porque verás el prefijo `(venv)` al inicio de la línea de comandos de tu terminal.

3. **Instalación de Dependencias Críticas:**
   Una vez que el entorno se encuentre activo, procede a instalar las librerías necesarias para el funcionamiento del framework y la conectividad SQL:
   ```bash
   pip install django==3.2.x pymysql cryptography

```

---

### Fase 3: Configuración de la Capa de Persistencia (Servidor Local XAMPP)

La aplicación utiliza un motor relacional para garantizar la integridad referencial de los datos geográficos de Medellín. Configuraremos este servicio a través del panel de control de XAMPP.

1. Abre el **Panel de Control de XAMPP** en tu computadora.
2. Inicia los servicios de **Apache** y **MySQL** presionando el botón *Start* al lado de cada módulo.
3. Abre tu navegador web favorito e ingresa al gestor de bases de datos gráfico en la URL: **`http://localhost/phpmyadmin/`**
4. Dirígete a la pestaña **Bases de datos (Databases)**, escribe exactamente el nombre `ruta_segura_medellin` en el campo correspondiente y selecciona la colación por defecto (`utf8mb4_general_ci`). Haz clic en **Crear**.

---

### Fase 4: Ejecución de Migraciones e Inyección Automatizada de Datos

Con la base de datos vacía creada en XAMPP y el entorno virtual activo, el paso final es estructurar las tablas lógicas y alimentarlas con la información geográfica base de la infraestructura de la ciudad.

1. **Sincronización del Modelo de Datos (Migraciones):**
Ejecuta el siguiente comando para que el ORM de Django traduzca tus modelos de Python a tablas SQL reales dentro de tu base de datos local:
```bash
python manage.py migrate

```



```
   > ⚙️ **Resultado esperado:** La consola desplegará una lista de confirmaciones en verde (`OK`), creando de forma automática las tablas de sectores críticos, variables climáticas y registros de tránsito en PHPMyAdmin.

2. **Inyección Geográfica del Eje Vial:**
   Corre el comando personalizado para poblar los deprimidos y puntos de monitoreo estratégico:
   ```bash
python manage.py poblar_sectores

```

3. **Iniciación del Servidor de Desarrollo:**
Finalmente, enciende la API REST para dejar los endpoints de consumo listos para el frontend:
```bash

```



python manage.py runserver

```
   El sistema te indicará que la API se encuentra transmitiendo con total éxito en la dirección local **`[http://127.0.0.1:8000/](http://127.0.0.1:8000/)`**.

```
