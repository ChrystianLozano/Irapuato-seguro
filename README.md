# 🛡️ Irapuato Seguro - Portal de Monitoreo e Incidencia Delictiva

Un portal web interactivo de alto impacto visual y funcional para el monitoreo y análisis de la incidencia delictiva por colonias en la ciudad de **Irapuato, Guanajuato**. Diseñado con una interfaz táctica oscura, moderna y responsiva, utilizando mapas dinámicos y gráficas en tiempo real.

El sitio es **100% estático** (HTML5, CSS3, JS Puro), lo que significa que no requiere de bases de datos complejas del lado del servidor para funcionar, y está configurado para publicarse de forma automática en **GitHub Pages** bajo el dominio personalizado:

🌐 **[irapuato-seguro.chrystian.dev](https://irapuato-seguro.chrystian.dev/)**

---

## ✨ Características Principales

*   **🗺️ Mapa Táctico Interactivo (Leaflet.js):** Centrado geográficamente en Irapuato, con estilos oscuros de alta definición suministrados por *CartoDB Dark Matter*.
*   **🔴 Burbujas de Riesgo por Colonia:** Representación en burbujas transparentes con bordes de luz de color según el nivel de riesgo de cada colonia (Crítico, Alto, Moderado, Bajo), calculado dinámicamente según filtros activos.
*   **📍 Marcadores Pulsantes de Incidentes:** Visualización de puntos delictivos individuales mediante micro-animaciones pulsantes que cambian de color según el tipo de delito (homicidio, robo, asalto, extorsión, etc.).
*   **📊 Analíticas en Tiempo Real (Chart.js):** Sincronización de 3 gráficos estadísticos interactivos en el panel lateral:
    1.  *Distribución de Delitos* (Gráfico de dona).
    2.  *Línea de Tendencia Dinámica* (Muestra totales anuales históricos en vista "Todos", y cambia automáticamente a comportamiento mensual detallado [Ene-Dic] al seleccionar un año específico).
    3.  *Colonias de Mayor Riesgo* (Gráfico de barra horizontal dinámico).
*   **⚙️ Filtros Avanzados:** Filtrado inmediato por tipo de delito, severidad (Alta, Media, Baja) y período horario (Mañana, Tarde, Noche).
*   **🔍 Buscador Inteligente:** Barra de búsqueda para colonias con autocompletado en cascada y enfoque de cámara en el mapa.
*   **⏱️ Línea de Tiempo del Historial (2015-2025):** Control deslizante anual con botón de reproducción (*Play*) para animar la evolución de los delitos año con año.
*   **📥 Opciones de Exportación Profesional:** 
    - **Exportar PNG:** Descarga una captura limpia del mapa visible libre de botones de control, con una tarjeta flotante de título y marca de agua de créditos y fecha.
    - **Exportar PDF:** Genera un reporte formal en formato A4 Horizontal, con el mapa escalado al lado izquierdo y una tarjeta con indicadores consolidados (filtros activos, totales, riesgo promedio y leyenda de colores) en el lado derecho.
*   **📝 Simulador de Reporte Ciudadano:** Formulario para registrar nuevos incidentes temporales de forma interactiva en la sesión del navegador.

---

## 📁 Estructura del Proyecto

```text
Mapa Irapuato/
├── index.html                  # Estructura principal y metatags SEO/Open Graph
├── CNAME                       # Archivo de enrutamiento a dominio personalizado chrystian.dev
├── og-image.png                # Imagen de alta resolución para previsualizaciones en redes sociales
├── favicon.svg                 # Icono del escudo del portal
├── css/
│   └── style.css               # Diseño visual, responsive, tipografías y glassmorphism
├── data/
│   └── database.json           # Base de datos JSON de incidentes y colonias
├── js/
│   └── app.js                  # Controladores de mapa, exportaciones, filtros y Chart.js
├── scripts/
│   ├── import_all_sesnsp.py    # Importa el historial total (2015-2025) a la base de datos
│   ├── update_from_sesnsp.py   # Actualiza la base de datos localmente con el corte mensual del CSV
│   └── update_crime_data.py    # Generador automatizado opcional para GitHub Actions (simulado)
├── .github/
│   └── workflows/
│       ├── deploy.yml          # Pipeline automático de despliegue a GitHub Pages (Node.js 24)
│       └── monthly_update.yml  # Automatización mensual de GitHub Actions (Node.js 24)
└── README.md                   # Documentación del proyecto (esta guía)
```

---

## 🚀 Cómo Ejecutar Localmente

Para previsualizar la página en tu navegador, levanta un servidor estático local simple:

1.  Abre la terminal en la carpeta del proyecto.
2.  Ejecuta el siguiente comando:
    ```bash
    python3 -m http.server 8080
    ```
3.  Ingresa a tu navegador en: [http://localhost:8080](http://localhost:8080)

---

## 📂 Integración de Datos Oficiales y Reales (SESNSP)

El portal utiliza las estadísticas delictivas reales de Irapuato provenientes de los conjuntos de datos abiertos del **Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública (SESNSP)**.

> [!NOTE]
> **Modelo Híbrido de Geolocalización:**
> Debido a que las estadísticas del SESNSP se publican a nivel municipal y carecen de coordenadas o colonias exactas, los scripts de importación emplean un algoritmo híbrido. Este distribuye el total de incidentes reportados oficialmente de forma proporcional en las colonias de Irapuato, ponderándolas según su nivel histórico de riesgo (baseRisk) y aplicando un desplazamiento geográfico (offset) controlado en coordenadas para visualizarlos como incidentes individuales en el mapa táctico.

### Paso 1: Descargar la base de datos municipal oficial
1. Ingresa al portal oficial de [Datos Abiertos de Incidencia Delictiva (gob.mx/sesnsp)](https://www.gob.mx/sesnsp/acciones-y-programas/datos-abiertos-de-incidencia-delictiva).
2. Descarga el archivo de **Incidencia delictiva municipal** (fuero común). Es un archivo ZIP de gran tamaño.
3. Descomprime el archivo y colócalo en la carpeta `data/` del proyecto. El archivo debe conservar la extensión `.csv` (por ejemplo, `IDM_NM_dic25.csv` o similar).

### Paso 2: Importar todo el Historial (2015 - 2025)
Si deseas reconstruir la base de datos completa con más de 39,000 registros históricos de Irapuato:
1. Asegúrate de tener el archivo `data/IDM_NM_dic25.csv` (o actualiza el nombre del archivo en la variable `CSV_PATH` dentro de `scripts/import_all_sesnsp.py`).
2. Ejecuta el script de importación completa:
   ```bash
   python3 scripts/import_all_sesnsp.py
   ```
3. Esto borrará la base de datos anterior y compilará la distribución histórica en `data/database.json`.

### Paso 3: Mantener actualizado el mapa mensualmente
Cuando el SESNSP publique un nuevo reporte mensual:
1. Descarga el CSV más reciente del sitio gubernamental y guárdalo en la carpeta `data/`.
2. Ejecuta el script actualizador:
   ```bash
   python3 scripts/update_from_sesnsp.py
   ```
3. El script escaneará la carpeta `data/`, detectará el último mes con incidencias delictivas registradas en el CSV, extraerá las cifras oficiales para Irapuato, limpiará cualquier registro previo del mismo mes para evitar duplicados y guardará la actualización en `data/database.json`.
4. Sube la actualización a GitHub:
   ```bash
   git add data/database.json
   git commit -m "data: actualización oficial SESNSP para [Mes] [Año]"
   git push
   ```

---

## 🌐 Publicación y Dominio Personalizado

Hemos configurado el enrutamiento y despliegue automático mediante GitHub Actions:

### Paso 1: Configurar en GitHub
1. Sube tu código a tu repositorio de GitHub:
   ```bash
   git remote add origin https://github.com/ChrystianLozano/Irapuato-seguro.git
   git branch -M main
   git push -u origin main
   ```
2. En GitHub, ve a **Settings** -> **Pages**.
3. Cambia la opción **Source** a **GitHub Actions**. El workflow `.github/workflows/deploy.yml` gestionará el despliegue automático con Node.js 24.

### Paso 2: Configurar tu DNS (Subdominio)
Para habilitar tu dominio personalizado `irapuato-seguro.chrystian.dev`:
1. Entra al panel de control de tu proveedor DNS para `chrystian.dev`.
2. Agrega un registro tipo **CNAME**:
   - **Nombre / Host:** `irapuato-seguro`
   - **Valor / Destino:** `ChrystianLozano.github.io`
3. En la sección **Custom domain** de GitHub Pages, verifica el dominio y marca **Enforce HTTPS** para activar el certificado SSL.

---

## 🛠️ Optimización SEO y Accesibilidad

*   **Estructura Semántica:** Se reestructuró la jerarquía de etiquetas de títulos utilizando un único elemento `<h1>` para la identidad principal de la marca, `<h2>` para los paneles de filtros y controles, y `<h3>` para las tarjetas de analíticas estadísticas.
*   **JSON-LD Dataset:** Se integró un esquema de datos estructurados `Schema.org/Dataset` en el código de cabecera de la página para que motores de búsqueda reconozcan e indexen correctamente el conjunto de datos de incidencia delictiva.
*   **Open Graph Premium:** Equipado con etiquetas Open Graph y Twitter Cards integradas para compartir en redes sociales, vinculando directamente a `og-image.png` para visualizaciones de alta fidelidad.
