# 🛡️ Irapuato Seguro - Mapa Delictivo Interactivo

Un portal web interactivo de alto impacto visual y funcional para el monitoreo y análisis de la incidencia delictiva por colonias en la ciudad de **Irapuato, Guanajuato**. Diseñado con una interfaz táctica oscura, moderna y responsiva, utilizando mapas dinámicos y gráficas en tiempo real.

Este proyecto es **100% estático** (HTML5, CSS3, JS Puro), lo que significa que no requiere de base de datos ni servidor activo para funcionar, y está listo para ser publicado instantáneamente en **GitHub Pages**.

---

## ✨ Características Principales

*   **🗺️ Mapa Táctico Interactivo (Leaflet.js):** Centrado geográficamente en Irapuato, con estilos oscuros de alta definición suministrados por *CartoDB Dark Matter*.
*   **🔴 Burbujas de Riesgo por Colonia:** Representación en burbujas transparentes con bordes de luz de color según el nivel de riesgo de cada colonia (Crítico, Alto, Moderado, Bajo), calculado dinámicamente según filtros activos.
*   **📍 Marcadores Pulsantes de Incidentes:** Visualización de puntos delictivos individuales mediante micro-animaciones pulsantes que cambian de color según el tipo de delito (homicidio, robo, asalto, extorsión, etc.).
*   **📊 Analíticas en Tiempo Real (Chart.js):** Sincronización instantánea de 3 gráficos estadísticos interactivos en el panel lateral:
    1.  *Distribución de Delitos* (Gráfico de dona).
    2.  *Línea de Tendencia Mensual* (Gráfico lineal suavizado con gradientes).
    3.  *Colonias de Mayor Riesgo* (Gráfico de barra horizontal dinámico).
*   **⚙️ Filtros Avanzados:** Filtrado inmediato por tipo de delito, severidad (Alta, Media, Baja) y período horario (Mañana, Tarde, Noche).
*   **🔍 Buscador Inteligente:** Barra de búsqueda para colonias con autocompletado en cascada y auto-enfoque de cámara del mapa.
*   **⏱️ Línea de Tiempo Animada:** Control deslizante cronológico con botón de reproducción (*Play*) para animar el historial delictivo acumulado mes a mes.
*   **📝 Simulador de Reporte Ciudadano:** Formulario para registrar nuevos incidentes seleccionando la colonia e indicando coordenadas de forma directa haciendo clic sobre el mapa. ¡Actualiza el mapa y los gráficos del dashboard instantáneamente en el estado local de la sesión!

---

## 📁 Estructura del Proyecto

```text
Mapa Irapuato/
├── index.html                  # Estructura e interfaz principal de la aplicación
├── css/
│   └── style.css               # Diseño de sistema, glassmorphism, responsive y doble panel lateral
├── data/
│   └── database.json           # Base de datos central en formato JSON (colonias y registros delictivos)
├── js/
│   └── app.js                  # Lógica del mapa (Leaflet), analíticas (Chart.js), filtros y buscador
├── scripts/
│   ├── init_database.py        # Script para inicializar/regenerar la base de datos JSON
│   └── update_crime_data.py    # Script mensual ejecutado por GitHub Actions para actualizar datos
├── .github/
│   └── workflows/
│       ├── deploy.yml          # Despliegue automático de la web a GitHub Pages al hacer push
│       └── monthly_update.yml  # Actualización automática mensual programada de los datos
└── README.md                   # Documentación del proyecto (esta guía)
```

---

## 🚀 Cómo Ejecutar Localmente

Dado que el navegador restringe la lectura de archivos locales (`data/database.json`) por seguridad (CORS) cuando se cargan vía `fetch()`, se requiere levantar un servidor local simple. No requiere instalar nada complejo, puedes usar Python que ya viene instalado en tu sistema operativo:

1.  Abre la terminal en la carpeta del proyecto.
2.  Ejecuta el siguiente comando:
    ```bash
    python3 -m http.server 8080
    ```
3.  Abre tu navegador e ingresa a: [http://localhost:8080](http://localhost:8080)

---

## 🌐 Publicación en GitHub y GitHub Pages

Sigue estos sencillos pasos para subir tu proyecto a GitHub y publicarlo para que cualquiera pueda visitarlo en la web:

### Paso 1: Inicializar Git y subir a tu Repositorio
1.  Entra a tu cuenta de GitHub y crea un nuevo repositorio llamado `Irapuato-seguro`.
2.  En tu terminal local, dentro de la carpeta del proyecto, ejecuta:
    ```bash
    git init
    git add .
    git commit -m "feat: version modularizada con base de datos json y acciones programadas"
    git branch -M main
    git remote add origin https://github.com/ChrystianLozano/Irapuato-seguro.git
    git push -u origin main
    ```

### Paso 2: Activar el Despliegue con GitHub Actions
Hemos incluido una configuración en `.github/workflows/deploy.yml` para automatizar completamente la publicación. Solo debes activarla en la interfaz de GitHub:

1.  En la página de tu repositorio de GitHub, ve a la pestaña **Settings** (Configuración).
2.  En el menú lateral izquierdo, haz clic en **Pages** (dentro de la sección *Code and automation*).
3.  Bajo **Build and deployment**, localiza la opción **Source**.
4.  Cambia la selección de `Deploy from a branch` a **GitHub Actions**.
5.  ¡Listo! En unos segundos se ejecutará el flujo de trabajo automáticamente. Puedes ver su progreso en la pestaña **Actions** de tu repositorio. Cuando termine, te proporcionará el enlace público (por ejemplo, `https://ChrystianLozano.github.io/Irapuato-seguro/`).

---

## ⚙️ Actualizaciones Mensuales Automatizadas

El proyecto está configurado para actualizarse automáticamente el **día 1 de cada mes** sin que tengas que intervenir.

* **Cómo funciona:** El flujo de trabajo `.github/workflows/monthly_update.yml` ejecuta el script de Python `scripts/update_crime_data.py` en los servidores de GitHub.
* **El script:** Compara la fecha del último incidente registrado contra la fecha real actual. Si ha transcurrido un nuevo mes, genera incidentes delictivos simulados realistas para ese mes, los anexa a `data/database.json` y sube los cambios de vuelta a tu repositorio de GitHub de forma segura.
* **Despliegue automático:** Al guardarse los nuevos datos en la rama `main`, se activa automáticamente el pipeline `deploy.yml`, reflejando la información del nuevo mes en el sitio web de inmediato.
* **Ejecución Manual:** Si deseas forzar la actualización en cualquier momento sin esperar al primer día del mes, puedes ir a la pestaña **Actions** en tu repositorio de GitHub, seleccionar **Automated Monthly Crime Data Update** en la izquierda y hacer clic en el botón **Run workflow**.

---

## 🛠️ Personalización Manual de Datos

Si en lugar de simulación automática prefieres capturar registros reales tú mismo, puedes desactivar la acción automática y modificar directamente el archivo **`data/database.json`**:

*   **`neighborhoods` (Colonias):** Puedes agregar o modificar coordenadas e IDs de colonias:
    ```json
    { "id": "colonia_id", "name": "Nombre Colonia", "lat": 20.XXXX, "lon": -101.XXXX, "baseRisk": 50 }
    ```
*   **`incidents` (Incidentes delictivos):** Agrega filas al listado vinculándolas al ID de la colonia:
    ```json
    {
      "id": "inc_unico_real",
      "type": "Robo a Transeúnte",
      "colonia": "colonia_id",
      "lat": 20.XXXX,
      "lon": -101.XXXX,
      "date": "2026-06-04T12:00:00",
      "timePeriod": "Tarde",
      "severity": "Media",
      "description": "Reporte ciudadano sobre hurto..."
    }
    ```
