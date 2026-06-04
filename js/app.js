/**
 * Irapuato Crime Map Dashboard - Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  // ==========================================================================
  // ESTADO GLOBAL DE LA APLICACIÓN
  // ==========================================================================
  const state = {
    // Filtros activos
    selectedCrimeTypes: [], // Cargado dinámicamente
    selectedSeverity: "all",
    selectedTimePeriod: "all",
    selectedMonthIndex: 12, // 12 representa "Todos" en el slider (Julio 2025 - Junio 2026)
    
    // Capas de mapas
    map: null,
    zonesLayerGroup: null,
    markersLayerGroup: null,
    heatmapLayer: null,
    
    // Modo de visualización activo: 'zones' | 'markers' | 'heatmap'
    activeViewMode: 'zones', 
    
    // Gráficos (Chart.js)
    charts: {
      type: null,
      trend: null,
      topZones: null
    },
    
    // Reportes creados por el usuario (en sesión)
    customReports: [],
    
    // Coordenadas seleccionadas para reporte temporal
    pickedCoords: null,
    
    // Estado de animación de la línea de tiempo
    timelineInterval: null,
    isTimelinePlaying: false
  };

  // Mapeo cronológico de los meses del slider
  const timelineMonths = [
    { label: "Jul 25", month: 7, year: 2025 },
    { label: "Ago 25", month: 8, year: 2025 },
    { label: "Sep 25", month: 9, year: 2025 },
    { label: "Oct 25", month: 10, year: 2025 },
    { label: "Nov 25", month: 11, year: 2025 },
    { label: "Dic 25", month: 12, year: 2025 },
    { label: "Ene 26", month: 1, year: 2026 },
    { label: "Feb 26", month: 2, year: 2026 },
    { label: "Mar 26", month: 3, year: 2026 },
    { label: "Abr 26", month: 4, year: 2026 },
    { label: "May 26", month: 5, year: 2026 },
    { label: "Jun 26", month: 6, year: 2026 },
    { label: "Todos", month: null, year: null }
  ];

  // Ponderaciones de severidad para cálculo dinámico de riesgo
  const CRIME_WEIGHTS = {
    "Homicidio": 5.0,
    "Asalto/Lesiones": 3.0,
    "Robo de Vehículo": 2.5,
    "Robo a Transeúnte": 1.5,
    "Extorsión/Fraude": 1.2,
    "Vandalismo": 0.8
  };

  // ==========================================================================
  // INICIALIZACIÓN
  // ==========================================================================
  let DATABASE = null; // Cargado dinámicamente desde JSON

  async function init() {
    initMap();
    try {
      const response = await fetch('./data/database.json');
      DATABASE = await response.json();
      
      // Sincronizar tipos de delito activos en el estado
      state.selectedCrimeTypes = Object.keys(DATABASE.crimeTypes);
      
      initUI();
      updateDashboard();
    } catch (err) {
      console.error("Error al cargar la base de datos de crímenes:", err);
      alert("Error al cargar la base de datos de crímenes. Asegúrese de iniciar un servidor local.");
    }
  }

  // 1. Inicializar Mapa (Leaflet)
  function initMap() {
    // Coordenadas céntricas de Irapuato
    const irapuatoCenter = [20.6758, -101.3521];
    
    // Crear el mapa restringiendo zoom
    state.map = L.map("map", {
      center: irapuatoCenter,
      zoom: 13,
      minZoom: 12,
      maxZoom: 16,
      zoomControl: true
    });

    // Agregar tileset oscuro de CartoDB (completamente libre, sin API key)
    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 20,
      crossOrigin: true
    }).addTo(state.map);

    // Ajustar posición de zoom a top-right
    state.map.zoomControl.setPosition('topleft');

    // Inicializar Grupos de Capas
    state.zonesLayerGroup = L.layerGroup().addTo(state.map);
    state.markersLayerGroup = L.layerGroup(); // No añadido aún por defecto
    
    // Configurar listener para picking de coordenadas al hacer clic en mapa
    state.map.on("click", (e) => {
      const modal = document.getElementById("reportModal");
      if (modal.classList.contains("active")) {
        setPickedCoordinates(e.latlng.lat, e.latlng.lng);
        showToast("Coordenadas seleccionadas en el mapa", false);
      }
    });
  }

  // 2. Inicializar Elementos de UI y Eventos
  function initUI() {
    // -- Llenar Filtros de Tipos de Delito --
    const filterContainer = document.getElementById("crimeTypesFilter");
    filterContainer.innerHTML = "";
    
    Object.keys(DATABASE.crimeTypes).forEach(type => {
      const info = DATABASE.crimeTypes[type];
      const tag = document.createElement("button");
      tag.className = "filter-tag active";
      tag.dataset.type = type;
      tag.innerHTML = `
        <span class="tag-dot" style="background-color: ${info.color}"></span>
        <span>${type}</span>
      `;
      tag.addEventListener("click", () => toggleCrimeTypeFilter(type, tag));
      filterContainer.appendChild(tag);
    });

    // -- Rellenar select del Formulario de Reportes --
    const selectNeighborhood = document.getElementById("reportNeighborhood");
    DATABASE.neighborhoods.sort((a,b) => a.name.localeCompare(b.name)).forEach(n => {
      const opt = document.createElement("option");
      opt.value = n.id;
      opt.textContent = n.name;
      selectNeighborhood.appendChild(opt);
    });

    // Centrar en colonia al seleccionarla en formulario
    selectNeighborhood.addEventListener("change", (e) => {
      const selectedColId = e.target.value;
      const colonia = DATABASE.neighborhoods.find(n => n.id === selectedColId);
      if (colonia) {
        state.map.panTo([colonia.lat, colonia.lon]);
        setPickedCoordinates(colonia.lat, colonia.lon);
      }
    });

    // -- Eventos de Filtros de Severidad --
    document.querySelectorAll(".severity-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".severity-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        state.selectedSeverity = btn.dataset.severity;
        updateDashboard();
      });
    });

    // -- Eventos de Filtros de Período Horario --
    document.querySelectorAll(".time-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".time-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        state.selectedTimePeriod = btn.dataset.time;
        updateDashboard();
      });
    });

    // -- Autocomplete en buscador de Colonias --
    const searchInput = document.getElementById("neighborhoodSearch");
    const autocompleteBox = document.getElementById("searchAutocomplete");
    const clearSearchBtn = document.getElementById("clearSearchBtn");

    searchInput.addEventListener("input", (e) => {
      const term = e.target.value.toLowerCase().trim();
      if (!term) {
        autocompleteBox.style.display = "none";
        clearSearchBtn.style.display = "none";
        return;
      }
      
      clearSearchBtn.style.display = "block";
      const matches = DATABASE.neighborhoods.filter(n => n.name.toLowerCase().includes(term));
      
      if (matches.length > 0) {
        autocompleteBox.innerHTML = "";
        matches.forEach(match => {
          const item = document.createElement("div");
          item.className = "autocomplete-item";
          
          // Calcular riesgo actual para esta colonia
          const incidents = getFilteredIncidents().filter(inc => inc.colonia === match.id);
          const riskIndex = calculateRiskIndexForColonia(match, incidents);
          const riskMeta = getRiskLevelMetadata(riskIndex);
          
          item.innerHTML = `
            <span>${match.name}</span>
            <span class="item-risk" style="background-color: ${riskMeta.glow}; color: ${riskMeta.color}; border: 1px solid ${riskMeta.color}">
              ${riskMeta.label}
            </span>
          `;
          
          item.addEventListener("click", () => {
            searchInput.value = match.name;
            autocompleteBox.style.display = "none";
            focusOnNeighborhood(match);
          });
          autocompleteBox.appendChild(item);
        });
        autocompleteBox.style.display = "block";
      } else {
        autocompleteBox.style.display = "none";
      }
    });

    clearSearchBtn.addEventListener("click", () => {
      searchInput.value = "";
      autocompleteBox.style.display = "none";
      clearSearchBtn.style.display = "none";
      // Restablecer vista del mapa
      state.map.setView([20.6758, -101.3521], 13);
    });

    // Ocultar buscador si se hace click fuera
    document.addEventListener("click", (e) => {
      if (!e.target.closest(".search-box")) {
        autocompleteBox.style.display = "none";
      }
    });

    // -- Toggles de Visualización superior derecha --
    document.getElementById("btnShowZones").addEventListener("click", () => switchViewMode("zones"));
    document.getElementById("btnShowMarkers").addEventListener("click", () => switchViewMode("markers"));
    document.getElementById("btnShowHeatmap").addEventListener("click", () => switchViewMode("heatmap"));

    // -- Controles de la línea de tiempo --
    const timelineSlider = document.getElementById("timelineSlider");
    const timelineTicksContainer = document.getElementById("timelineTicks");
    
    // Rellenar marcas (ticks) en slider
    timelineTicksContainer.innerHTML = "";
    timelineMonths.forEach((m, idx) => {
      const tick = document.createElement("span");
      tick.className = `timeline-tick ${idx === 12 ? 'active' : ''}`;
      tick.textContent = m.label;
      tick.addEventListener("click", () => {
        timelineSlider.value = idx;
        handleTimelineSliderChange(idx);
      });
      timelineTicksContainer.appendChild(tick);
    });

    timelineSlider.addEventListener("input", (e) => {
      handleTimelineSliderChange(parseInt(e.target.value));
    });

    document.getElementById("timelinePlayBtn").addEventListener("click", toggleTimelinePlayback);

    // -- Modales y reportes --
    const reportModal = document.getElementById("reportModal");
    document.getElementById("openReportFormBtn").addEventListener("click", () => {
      reportModal.classList.add("active");
      // Inicializar fecha con la actual
      const now = new Date();
      now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
      document.getElementById("reportDate").value = now.toISOString().slice(0, 16);
      
      // Auto-rellenar coordenadas iniciales si hay algo picked
      if (!state.pickedCoords) {
        setPickedCoordinates(20.6758, -101.3521); // Centro por defecto
      }
    });

    const closeModal = () => {
      reportModal.classList.remove("active");
      document.getElementById("crimeReportForm").reset();
      state.pickedCoords = null;
      document.getElementById("pickedLat").textContent = "N/A";
      document.getElementById("pickedLon").textContent = "N/A";
    };

    document.getElementById("closeReportModalBtn").addEventListener("click", closeModal);
    document.getElementById("cancelReportBtn").addEventListener("click", closeModal);

    // Enviar Reporte
    document.getElementById("crimeReportForm").addEventListener("submit", handleReportSubmission);

    // -- Mobile Sidebar toggles --
    const sidebar = document.getElementById("sidebar");
    const openBtn = document.getElementById("sidebarOpenBtn");
    const closeBtn = document.getElementById("sidebarCloseBtn");

    openBtn.addEventListener("click", () => sidebar.classList.add("active"));
    closeBtn.addEventListener("click", () => sidebar.classList.remove("active"));

    // -- Mobile Right Sidebar (Charts) toggles --
    const chartsSidebar = document.getElementById("chartsSidebar");
    const chartsOpenBtn = document.getElementById("chartsSidebarOpenBtn");
    const chartsCloseBtn = document.getElementById("chartsSidebarCloseBtn");

    chartsOpenBtn.addEventListener("click", () => chartsSidebar.classList.add("active"));
    chartsCloseBtn.addEventListener("click", () => chartsSidebar.classList.remove("active"));

    // -- Botones de Exportación (PNG / PDF) --
    document.getElementById("btnExportPng").addEventListener("click", exportMapToPng);
    document.getElementById("btnExportPdf").addEventListener("click", exportMapToPdf);
  }

  // ==========================================================================
  // FILTRADO Y MANEJO DE DATOS
  // ==========================================================================

  // Obtener incidentes aplicando todos los filtros activos
  function getFilteredIncidents() {
    // Unir incidentes estáticos y dinámicos creados en sesión
    const allIncidents = [...DATABASE.incidents, ...state.customReports];
    
    return allIncidents.filter(inc => {
      // 1. Filtro Tipo de Delito
      if (!state.selectedCrimeTypes.includes(inc.type)) return false;
      
      // 2. Filtro Severidad
      if (state.selectedSeverity !== "all" && inc.severity !== state.selectedSeverity) return false;
      
      // 3. Filtro Período Horario
      if (state.selectedTimePeriod !== "all" && inc.timePeriod !== state.selectedTimePeriod) return false;
      
      // 4. Filtro Historial de Tiempo (Timeline Slider)
      if (state.selectedMonthIndex !== 12) { // 12 es "Todos"
        const timelineTarget = timelineMonths[state.selectedMonthIndex];
        const incDate = new Date(inc.date);
        const incMonth = incDate.getMonth() + 1; // 0-indexed
        const incYear = incDate.getFullYear();
        
        // Mostrar incidentes ocurridos EN o ANTES del mes seleccionado en la animación
        // O bien, si es una simulación paso a paso, mostramos acumulado hasta ese mes
        if (incYear > timelineTarget.year) return false;
        if (incYear === timelineTarget.year && incMonth > timelineTarget.month) return false;
      }
      
      return true;
    });
  }

  // Calcular índice de riesgo ponderado para una colonia
  function calculateRiskIndexForColonia(colonia, incidents) {
    if (incidents.length === 0) return 0;
    
    let weightedSum = 0;
    incidents.forEach(inc => {
      weightedSum += (CRIME_WEIGHTS[inc.type] || 1.0);
    });

    // Escalado logarítmico para suavizar picos y normalizar en rango [0 - 100]
    // Considera el riesgo base estático de la colonia también
    const dynamicScore = Math.min(100, Math.log1p(weightedSum) * 18);
    const finalScore = (colonia.baseRisk * 0.4) + (dynamicScore * 0.6);
    
    return Math.round(finalScore);
  }

  // Obtener metadatos de riesgo (color, etiqueta) a partir del puntaje [0-100]
  function getRiskLevelMetadata(score) {
    if (score >= 75) {
      return { label: "Crítico", color: "var(--color-critical)", glow: "var(--color-critical-glow)", rating: "critical" };
    } else if (score >= 55) {
      return { label: "Alto", color: "var(--color-high)", glow: "var(--color-high-glow)", rating: "high" };
    } else if (score >= 35) {
      return { label: "Moderado", color: "var(--color-moderate)", glow: "var(--color-moderate-glow)", rating: "moderate" };
    } else {
      return { label: "Bajo", color: "var(--color-low)", glow: "var(--color-low-glow)", rating: "low" };
    }
  }

  // ==========================================================================
  // FLUJOS DE TRABAJO E INTERACCIÓN CON EL MAPA
  // ==========================================================================

  // Alternar el estado de un tipo de delito en el filtro
  function toggleCrimeTypeFilter(type, tagElement) {
    const idx = state.selectedCrimeTypes.indexOf(type);
    if (idx > -1) {
      // Quitar filtro (debe quedar al menos 1 seleccionado)
      if (state.selectedCrimeTypes.length === 1) {
        showToast("Debe mantener al menos un tipo de delito seleccionado", true);
        return;
      }
      state.selectedCrimeTypes.splice(idx, 1);
      tagElement.classList.remove("active");
    } else {
      // Agregar filtro
      state.selectedCrimeTypes.push(type);
      tagElement.classList.add("active");
    }
    updateDashboard();
  }

  // Cambiar modo de visualización en el mapa (Zonas, Marcadores individuales o Heatmap)
  function switchViewMode(mode) {
    state.activeViewMode = mode;
    
    // Quitar todas las capas activas primero
    state.map.removeLayer(state.zonesLayerGroup);
    state.map.removeLayer(state.markersLayerGroup);
    if (state.heatmapLayer) {
      state.map.removeLayer(state.heatmapLayer);
    }

    // Remover clases activas de botones
    document.querySelectorAll(".layer-btn").forEach(b => b.classList.remove("active"));

    if (mode === "zones") {
      document.getElementById("btnShowZones").classList.add("active");
      state.zonesLayerGroup.addTo(state.map);
    } else if (mode === "markers") {
      document.getElementById("btnShowMarkers").classList.add("active");
      state.markersLayerGroup.addTo(state.map);
    } else if (mode === "heatmap") {
      document.getElementById("btnShowHeatmap").classList.add("active");
      renderHeatmap();
    }

    updateMapLayers();
  }

  // Centrar mapa en una colonia seleccionada y abrir su ficha informativa
  function focusOnNeighborhood(colonia) {
    state.map.setView([colonia.lat, colonia.lon], 14.5);
    
    // Si estamos en modo zonas, buscar el círculo y abrir su popup
    if (state.activeViewMode === "zones") {
      state.zonesLayerGroup.eachLayer(layer => {
        if (layer.options.id === colonia.id) {
          setTimeout(() => layer.openPopup(), 300);
        }
      });
    }
  }

  // Ajustar coordenadas capturadas para el formulario
  function setPickedCoordinates(lat, lon) {
    state.pickedCoords = { lat: parseFloat(lat), lon: parseFloat(lon) };
    document.getElementById("pickedLat").textContent = lat.toFixed(5);
    document.getElementById("pickedLon").textContent = lon.toFixed(5);
  }

  // ==========================================================================
  // RENDERIZADO DEL MAPA
  // ==========================================================================

  // Actualizar los elementos geométricos en el mapa basado en filtros activos
  function updateMapLayers() {
    const filteredIncidents = getFilteredIncidents();

    // 1. Limpiar capas de trabajo
    state.zonesLayerGroup.clearLayers();
    state.markersLayerGroup.clearLayers();

    // 2. Trazar Círculos de Zona (Zonas de riesgo por colonia)
    DATABASE.neighborhoods.forEach(colonia => {
      // Filtrar incidentes de esta colonia concreta
      const colIncidents = filteredIncidents.filter(inc => inc.colonia === colonia.id);
      const riskIndex = calculateRiskIndexForColonia(colonia, colIncidents);
      const riskMeta = getRiskLevelMetadata(riskIndex);

      // Agrupar conteos de incidentes para el popup
      const typeCounts = {};
      colIncidents.forEach(inc => {
        typeCounts[inc.type] = (typeCounts[inc.type] || 0) + 1;
      });

      let breakDownHtml = "";
      Object.keys(DATABASE.crimeTypes).forEach(type => {
        const count = typeCounts[type] || 0;
        if (count > 0) {
          const info = DATABASE.crimeTypes[type];
          breakDownHtml += `
            <div class="popup-card-row">
              <span class="label"><i class="fa-solid ${info.icon}" style="color: ${info.color}"></i> ${type}</span>
              <span class="value">${count}</span>
            </div>
          `;
        }
      });

      if (!breakDownHtml) breakDownHtml = "<div class='popup-card-row text-success'>Sin incidentes registrados</div>";

      // Diseñar popup personalizado para la colonia
      const popupContent = `
        <div class="popup-card">
          <h3><i class="fa-solid fa-map-location-dot"></i> ${colonia.name}</h3>
          <div class="popup-card-row">
            <span class="label">Nivel de Riesgo:</span>
            <span class="value" style="color: ${riskMeta.color}; font-weight:700;">${riskMeta.label} (${riskIndex}%)</span>
          </div>
          <div class="popup-card-row" style="margin-bottom:0.75rem;">
            <span class="label">Total del periodo:</span>
            <span class="value" style="font-weight:700;">${colIncidents.length}</span>
          </div>
          <div style="border-top:1px solid rgba(255,255,255,0.08); padding-top:0.5rem;">
            <h4 style="font-size:0.75rem; color:var(--text-muted); margin-bottom:0.35rem; text-transform:uppercase;">Desglose:</h4>
            ${breakDownHtml}
          </div>
        </div>
      `;

      // Dibujar burbuja táctica (círculo)
      const zoneCircle = L.circle([colonia.lat, colonia.lon], {
        id: colonia.id,
        color: riskMeta.color,
        weight: 1.5,
        fillColor: riskMeta.color,
        fillOpacity: 0.25,
        radius: 400 + (riskIndex * 2.5) // El radio escala levemente con el riesgo
      });

      // Efectos hover interactivos
      zoneCircle.on("mouseover", () => {
        zoneCircle.setStyle({ fillOpacity: 0.45, weight: 3 });
      });
      zoneCircle.on("mouseout", () => {
        zoneCircle.setStyle({ fillOpacity: 0.25, weight: 1.5 });
      });

      zoneCircle.bindPopup(popupContent);
      state.zonesLayerGroup.addLayer(zoneCircle);
    });

    // 3. Trazar Marcadores de Incidentes Individuales
    filteredIncidents.forEach(inc => {
      const typeInfo = DATABASE.crimeTypes[inc.type] || { color: "#ffffff", icon: "fa-question" };
      const dateFormatted = new Date(inc.date).toLocaleDateString('es-MX', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });

      const coloniaName = DATABASE.neighborhoods.find(n => n.id === inc.colonia)?.name || "Desconocida";

      const popupContent = `
        <div class="popup-card">
          <h3>
            <i class="fa-solid ${typeInfo.icon}" style="color: ${typeInfo.color}; filter: drop-shadow(0 0 5px ${typeInfo.glow});"></i> 
            ${inc.type}
          </h3>
          <div class="popup-card-row">
            <span class="label">Colonia:</span>
            <span class="value">${coloniaName}</span>
          </div>
          <div class="popup-card-row">
            <span class="label">Fecha:</span>
            <span class="value">${dateFormatted}</span>
          </div>
          <div class="popup-card-row">
            <span class="label">Severidad:</span>
            <span class="value">${inc.severity}</span>
          </div>
          <div class="popup-card-row">
            <span class="label">Horario:</span>
            <span class="value">${inc.timePeriod}</span>
          </div>
          <div class="popup-desc">${inc.description}</div>
        </div>
      `;

      // Icono flotante con CSS pulse animado
      const customIcon = L.divIcon({
        className: 'glowing-marker-icon',
        html: `<div class="marker-pulse" style="color: ${typeInfo.color}; background-color: ${typeInfo.color}"></div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10]
      });

      const marker = L.marker([inc.lat, inc.lon], { icon: customIcon });
      marker.bindPopup(popupContent);
      state.markersLayerGroup.addLayer(marker);
    });

    // 4. Si estamos en modo Mapa de Calor (Heatmap), regenerarlo
    if (state.activeViewMode === "heatmap") {
      renderHeatmap();
    }
  }

  // Generar capa de heatmap (densidad de crímenes)
  function renderHeatmap() {
    if (state.heatmapLayer) {
      state.map.removeLayer(state.heatmapLayer);
    }

    const filteredIncidents = getFilteredIncidents();
    
    // Mapear los puntos a formato requerido por leaflet.heat [lat, lon, intensidad]
    const heatPoints = filteredIncidents.map(inc => {
      const weight = CRIME_WEIGHTS[inc.type] || 1.0;
      // Normalizar intensidad de acuerdo a la severidad
      let intensity = 0.5;
      if (inc.severity === "Alta") intensity = 1.0;
      else if (inc.severity === "Media") intensity = 0.7;
      
      return [inc.lat, inc.lon, intensity * weight * 0.15];
    });

    // Inicializar plugin heatmap con gradiente estético oscuro/cálido
    state.heatmapLayer = L.heatLayer(heatPoints, {
      radius: 35,
      blur: 20,
      maxZoom: 15,
      gradient: {
        0.2: '#00c7fc', // Cian
        0.4: '#34c759', // Verde
        0.6: '#ffcc00', // Amarillo
        0.8: '#ff9500', // Naranja
        1.0: '#ff3b30'  // Rojo Crítico
      }
    }).addTo(state.map);
  }

  // ==========================================================================
  // RENDERIZADO DEL DASHBOARD & ESTADÍSTICAS
  // ==========================================================================

  // Sincronizar estadísticas y gráficos principales del sidebar
  function updateDashboard() {
    const filteredIncidents = getFilteredIncidents();

    // 1. Actualizar números globales en cards
    document.getElementById("statTotalCrimes").textContent = filteredIncidents.length;

    // Calcular riesgo general promedio del mapa
    let totalRisk = 0;
    let safeCount = 0;
    
    DATABASE.neighborhoods.forEach(col => {
      const colInc = filteredIncidents.filter(i => i.colonia === col.id);
      const score = calculateRiskIndexForColonia(col, colInc);
      totalRisk += score;
      if (score < 35) safeCount++;
    });

    const averageRisk = DATABASE.neighborhoods.length > 0 ? Math.round(totalRisk / DATABASE.neighborhoods.length) : 0;
    const generalRiskMeta = getRiskLevelMetadata(averageRisk);

    const riskLevelLabel = document.getElementById("statRiskLevel");
    const riskLevelCard = document.getElementById("statRiskCard");
    
    riskLevelLabel.textContent = `${generalRiskMeta.label} (${averageRisk}%)`;
    riskLevelCard.className = `stat-card risk-rating ${generalRiskMeta.rating}-risk`;

    document.getElementById("statSafeCount").textContent = safeCount;

    // 2. Renderizar los gráficos usando Chart.js
    renderCharts(filteredIncidents);
    
    // 3. Refrescar el mapa
    updateMapLayers();

    // 4. Actualizar fecha de última actualización en footer
    const allInc = [...DATABASE.incidents, ...state.customReports];
    if (allInc.length > 0) {
      let maxDateStr = "2025-07-01T00:00:00";
      allInc.forEach(inc => {
        if (inc.date > maxDateStr) {
          maxDateStr = inc.date;
        }
      });
      const maxDate = new Date(maxDateStr);
      const options = { month: 'long', year: 'numeric' };
      const formattedDate = maxDate.toLocaleDateString('es-MX', options);
      const capitalizedDate = formattedDate.charAt(0).toUpperCase() + formattedDate.slice(1);
      document.getElementById("lastUpdateLabel").textContent = capitalizedDate;
    } else {
      document.getElementById("lastUpdateLabel").textContent = "N/A";
    }
  }

  // Dibujar/Actualizar gráficos de Chart.js
  function renderCharts(incidents) {
    // -- Gráfico 1: Doughnut de Tipos de Delito --
    const typeCounts = {};
    Object.keys(DATABASE.crimeTypes).forEach(t => typeCounts[t] = 0);
    incidents.forEach(inc => {
      if (typeCounts[inc.type] !== undefined) {
        typeCounts[inc.type]++;
      }
    });

    const typeLabels = Object.keys(typeCounts);
    const typeData = Object.values(typeCounts);
    const typeColors = typeLabels.map(label => DATABASE.crimeTypes[label].color);

    if (state.charts.type) {
      state.charts.type.data.datasets[0].data = typeData;
      state.charts.type.update();
    } else {
      const ctx = document.getElementById("crimeTypeChart").getContext("2d");
      state.charts.type = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: typeLabels,
          datasets: [{
            data: typeData,
            backgroundColor: typeColors,
            borderColor: '#0f111a',
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false } // Ocultar leyenda para ahorrar espacio en sidebar
          },
          cutout: '65%'
        }
      });
    }

    // -- Gráfico 2: Línea de Tendencia Mensual --
    // Agrupar incidentes por mes (Jul 25 - Jun 26)
    const monthCounts = Array(12).fill(0);
    
    incidents.forEach(inc => {
      const date = new Date(inc.date);
      const m = date.getMonth(); // 0-11 (Ene-Dic)
      const y = date.getFullYear();
      
      // Buscar índice en nuestro array timelineMonths (excluyendo "Todos" en posición 12)
      const index = timelineMonths.findIndex(t => t.month === (m + 1) && t.year === y);
      if (index > -1 && index < 12) {
        monthCounts[index]++;
      }
    });

    const trendLabels = timelineMonths.slice(0, 12).map(t => t.label);

    if (state.charts.trend) {
      state.charts.trend.data.datasets[0].data = monthCounts;
      state.charts.trend.update();
    } else {
      const ctx = document.getElementById("crimeTrendChart").getContext("2d");
      
      // Crear gradiente estético debajo de la línea
      const gradient = ctx.createLinearGradient(0, 0, 0, 140);
      gradient.addColorStop(0, 'rgba(99, 102, 241, 0.4)');
      gradient.addColorStop(1, 'rgba(99, 102, 241, 0.0)');

      state.charts.trend = new Chart(ctx, {
        type: 'line',
        data: {
          labels: trendLabels,
          datasets: [{
            label: 'Incidentes',
            data: monthCounts,
            borderColor: '#6366f1',
            borderWidth: 2,
            pointBackgroundColor: '#6366f1',
            fill: true,
            backgroundColor: gradient,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: {
              grid: { display: false },
              ticks: { color: 'rgba(255, 255, 255, 0.5)', font: { size: 9 } }
            },
            y: {
              grid: { color: 'rgba(255, 255, 255, 0.05)' },
              ticks: { color: 'rgba(255, 255, 255, 0.5)', font: { size: 9 }, precision: 0 }
            }
          }
        }
      });
    }

    // -- Gráfico 3: Horizontal Bar de Colonias Críticas --
    // Calcular índice de riesgo por colonia para el set actual
    const colRisks = DATABASE.neighborhoods.map(col => {
      const colInc = incidents.filter(inc => inc.colonia === col.id);
      return {
        name: col.name,
        risk: calculateRiskIndexForColonia(col, colInc)
      };
    });

    // Ordenar y obtener top 5
    colRisks.sort((a, b) => b.risk - a.risk);
    const top5 = colRisks.slice(0, 5);
    const topLabels = top5.map(c => c.name);
    const topData = top5.map(c => c.risk);

    if (state.charts.topZones) {
      state.charts.topZones.data.labels = topLabels;
      state.charts.topZones.data.datasets[0].data = topData;
      state.charts.topZones.update();
    } else {
      const ctx = document.getElementById("topNeighborhoodsChart").getContext("2d");
      state.charts.topZones = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: topLabels,
          datasets: [{
            data: topData,
            backgroundColor: 'rgba(255, 59, 48, 0.75)',
            borderColor: '#ff3b30',
            borderWidth: 1,
            borderRadius: 4
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: {
              max: 100,
              grid: { display: false },
              ticks: { color: 'rgba(255, 255, 255, 0.5)', font: { size: 9 } }
            },
            y: {
              grid: { display: false },
              ticks: { color: 'rgba(255, 255, 255, 0.7)', font: { size: 10 } }
            }
          }
        }
      });
    }
  }

  // ==========================================================================
  // TIMELINE SLIDER Y ANIMACIÓN
  // ==========================================================================

  // Manejar el cambio del slider manual
  function handleTimelineSliderChange(idx) {
    state.selectedMonthIndex = idx;
    
    // Actualizar estilo activo en los ticks de UI
    document.querySelectorAll(".timeline-tick").forEach((tick, i) => {
      if (i === idx) tick.classList.add("active");
      else tick.classList.remove("active");
    });

    // Actualizar etiqueta del mes
    const label = document.getElementById("timelineDateLabel");
    if (idx === 12) {
      label.textContent = "Todos los meses (Histórico)";
    } else {
      const m = timelineMonths[idx];
      label.textContent = `Acumulado hasta: ${m.label} (${m.year})`;
    }

    updateDashboard();
  }

  // Animar el historial mes a mes
  function toggleTimelinePlayback() {
    const playBtn = document.getElementById("timelinePlayBtn");
    
    if (state.isTimelinePlaying) {
      // Detener
      clearInterval(state.timelineInterval);
      state.isTimelinePlaying = false;
      playBtn.innerHTML = '<i class="fa-solid fa-play"></i>';
      showToast("Animación detenida", false);
    } else {
      // Iniciar
      state.isTimelinePlaying = true;
      playBtn.innerHTML = '<i class="fa-solid fa-pause"></i>';
      showToast("Iniciando línea de tiempo delictiva", false);
      
      // Si está en el final (Todos), resetear al mes 0
      let currentVal = parseInt(document.getElementById("timelineSlider").value);
      if (currentVal >= 12) {
        currentVal = 0;
        document.getElementById("timelineSlider").value = 0;
        handleTimelineSliderChange(0);
      }

      state.timelineInterval = setInterval(() => {
        currentVal++;
        if (currentVal > 12) {
          // Bucle terminado, parar reproducción
          clearInterval(state.timelineInterval);
          state.isTimelinePlaying = false;
          playBtn.innerHTML = '<i class="fa-solid fa-play"></i>';
          document.getElementById("timelineSlider").value = 12;
          handleTimelineSliderChange(12);
          showToast("Visualización completada", false);
        } else {
          document.getElementById("timelineSlider").value = currentVal;
          handleTimelineSliderChange(currentVal);
        }
      }, 1500); // 1.5 segundos por mes
    }
  }

  // ==========================================================================
  // ENVIAR REPORTES SIMULADOS
  // ==========================================================================

  function handleReportSubmission(e) {
    e.preventDefault();

    const neighborhoodId = document.getElementById("reportNeighborhood").value;
    const type = document.getElementById("reportCrimeType").value;
    const dateVal = document.getElementById("reportDate").value;
    const timePeriod = document.getElementById("reportTimePeriod").value;
    const severity = document.getElementById("reportSeverity").value;
    const description = document.getElementById("reportDescription").value;

    const coloniaObj = DATABASE.neighborhoods.find(n => n.id === neighborhoodId);
    if (!coloniaObj) {
      showToast("Por favor selecciona una colonia válida", true);
      return;
    }

    // Coordenadas elegidas: usar picked si concuerdan, si no añadir una variación leve al centro de la colonia
    let lat = coloniaObj.lat;
    let lon = coloniaObj.lon;

    if (state.pickedCoords) {
      lat = state.pickedCoords.lat;
      lon = state.pickedCoords.lon;
    } else {
      // Desplazamiento aleatorio para simular que no están todos amontonados
      lat += (Math.random() - 0.5) * 0.004;
      lon += (Math.random() - 0.5) * 0.004;
    }

    // Crear reporte temporal en memoria local
    const newReport = {
      id: `custom_inc_${Date.now()}`,
      type: type,
      colonia: neighborhoodId,
      lat: lat,
      lon: lon,
      date: dateVal,
      timePeriod: timePeriod,
      severity: severity,
      description: description
    };

    state.customReports.push(newReport);
    
    // Cerrar modal
    document.getElementById("reportModal").classList.remove("active");
    document.getElementById("crimeReportForm").reset();
    state.pickedCoords = null;

    // Feedback visual
    showToast(`Reporte registrado con éxito en ${coloniaObj.name}!`, false);

    // Actualizar todo
    updateDashboard();

    // Enfocar el mapa hacia el incidente reportado para dar feedback inmediato al usuario
    state.map.setView([lat, lon], 15.5);
    
    // Si estamos en modo incidentes/markers, abrir el popup del nuevo elemento
    setTimeout(() => {
      state.markersLayerGroup.eachLayer(layer => {
        if (layer.getLatLng().lat === lat && layer.getLatLng().lng === lon) {
          layer.openPopup();
        }
      });
    }, 500);
  }

  // Exportar mapa visible a formato PNG con marca de agua y branding
  function exportMapToPng() {
    showToast("Generando imagen PNG... Por favor espera.", false);
    
    const mapElement = document.getElementById("map");
    
    html2canvas(mapElement, {
      useCORS: true,
      allowTaint: false,
      backgroundColor: "#08090f",
      onclone: (clonedDoc) => {
        const clonedMap = clonedDoc.getElementById("map");
        if (!clonedMap) return;
        
        // Ocultar controles de Leaflet
        const controls = clonedDoc.querySelectorAll(".leaflet-control-container");
        controls.forEach(ctrl => ctrl.style.display = "none");
        
        // Agregar overlay de marca de agua/título
        const titleOverlay = clonedDoc.createElement("div");
        titleOverlay.style.position = "absolute";
        titleOverlay.style.top = "20px";
        titleOverlay.style.left = "20px";
        titleOverlay.style.zIndex = "9999";
        titleOverlay.style.background = "rgba(15, 17, 26, 0.85)";
        titleOverlay.style.border = "1px solid rgba(255, 255, 255, 0.1)";
        titleOverlay.style.borderRadius = "12px";
        titleOverlay.style.padding = "12px 18px";
        titleOverlay.style.fontFamily = "'Outfit', sans-serif";
        titleOverlay.style.color = "#f3f4f6";
        titleOverlay.style.boxShadow = "0 8px 32px 0 rgba(0, 0, 0, 0.5)";
        titleOverlay.style.backdropFilter = "blur(8px)";
        titleOverlay.innerHTML = `
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <i class="fa-solid fa-shield-halved" style="color: #6366f1; font-size: 16px;"></i>
            <span style="font-weight: 700; font-size: 16px; letter-spacing: 0.5px; background: linear-gradient(135deg, #ffffff 30%, #a5b4fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Irapuato Seguro</span>
          </div>
          <div style="font-size: 11px; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.5px;">Mapa de Monitoreo e Incidencia</div>
        `;
        clonedMap.appendChild(titleOverlay);

        // Agregar pie de página con créditos y fecha
        const dateStr = new Date().toLocaleDateString('es-MX', {
          day: '2-digit',
          month: 'long',
          year: 'numeric'
        });
        const footerOverlay = clonedDoc.createElement("div");
        footerOverlay.style.position = "absolute";
        footerOverlay.style.bottom = "20px";
        footerOverlay.style.right = "20px";
        footerOverlay.style.zIndex = "9999";
        footerOverlay.style.background = "rgba(15, 17, 26, 0.85)";
        footerOverlay.style.border = "1px solid rgba(255, 255, 255, 0.1)";
        footerOverlay.style.borderRadius = "8px";
        footerOverlay.style.padding = "8px 12px";
        footerOverlay.style.fontFamily = "'Outfit', sans-serif";
        footerOverlay.style.color = "#9ca3af";
        footerOverlay.style.fontSize = "10px";
        footerOverlay.style.boxShadow = "0 8px 32px 0 rgba(0, 0, 0, 0.5)";
        footerOverlay.style.backdropFilter = "blur(8px)";
        footerOverlay.innerHTML = `
          <div>Desarrollado por: <strong>chrystian.dev</strong></div>
          <div style="font-size: 8px; color: #6b7280; margin-top: 2px; text-align: right;">${dateStr}</div>
        `;
        clonedMap.appendChild(footerOverlay);
      }
    }).then(canvas => {
      try {
        const dataUrl = canvas.toDataURL("image/png");
        const link = document.createElement("a");
        const dateFormatted = new Date().toISOString().slice(0, 10).replace(/-/g, "");
        link.download = `mapa-irapuato-seguro-${dateFormatted}.png`;
        link.href = dataUrl;
        link.click();
        showToast("¡Mapa PNG descargado con éxito!", false);
      } catch (err) {
        console.error("Error al exportar PNG:", err);
        showToast("Error al exportar PNG. Intente de nuevo.", true);
      }
    }).catch(err => {
      console.error("Error al capturar el mapa con html2canvas:", err);
      showToast("Error al capturar el mapa.", true);
    });
  }

  // Exportar mapa y análisis actual a reporte PDF estructurado (Formato A4 Horizontal)
  function exportMapToPdf() {
    showToast("Generando reporte PDF... Por favor espera.", false);

    const mapElement = document.getElementById("map");

    html2canvas(mapElement, {
      useCORS: true,
      allowTaint: false,
      backgroundColor: "#08090f",
      onclone: (clonedDoc) => {
        // En el clon ocultamos los controles del mapa
        const controls = clonedDoc.querySelectorAll(".leaflet-control-container");
        controls.forEach(ctrl => ctrl.style.display = "none");
      }
    }).then(canvas => {
      try {
        const mapImgData = canvas.toDataURL("image/png");
        
        // Obtener constructor jsPDF
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF({
          orientation: 'landscape',
          unit: 'mm',
          format: 'a4'
        });

        // Dimensiones A4 Horizontal: 297mm x 210mm
        const pageW = 297;
        const pageH = 210;

        // 1. Fondo Oscuro Principal (#08090f)
        doc.setFillColor(8, 9, 15);
        doc.rect(0, 0, pageW, pageH, 'F');

        // 2. Línea decorativa superior (Glow Indigo)
        doc.setFillColor(99, 102, 241);
        doc.rect(0, 0, pageW, 2.5, 'F');

        // 3. Encabezado del Reporte
        // Título Principal (Blanco)
        doc.setTextColor(255, 255, 255);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(16);
        doc.text("IRAPUATO SEGURO", 15, 12);

        // Subtítulo
        doc.setTextColor(156, 163, 175); // #9ca3af (muted)
        doc.setFont("helvetica", "normal");
        doc.setFontSize(9);
        doc.text("PORTAL INTERACTIVO DE MONITOREO DE RIESGO E INCIDENCIA DELICTIVA", 15, 17);

        // Fecha de generación y hora (Alineado a la derecha)
        const now = new Date();
        const dateStr = now.toLocaleDateString('es-MX', {
          day: '2-digit',
          month: 'short',
          year: 'numeric'
        }).toUpperCase();
        const timeStr = now.toLocaleTimeString('es-MX', {
          hour: '2-digit',
          minute: '2-digit',
          hour12: false
        });
        
        doc.setFontSize(8);
        doc.setTextColor(107, 114, 128); // #6b7280
        doc.text(`REPORTE EMITIDO EL: ${dateStr} - ${timeStr} HRS`, pageW - 15, 15, { align: "right" });

        // Línea divisora sutil debajo del encabezado
        doc.setDrawColor(30, 35, 55); // #1e2337
        doc.setLineWidth(0.5);
        doc.line(15, 20, pageW - 15, 20);

        // 4. Espacio para el Mapa (Lado Izquierdo)
        // Calcular aspect ratio para ajustarse a un contenedor
        const mapWMax = 195;
        const mapHMax = 155;
        const aspect = canvas.width / canvas.height;
        let mapW = mapWMax;
        let mapH = mapW / aspect;

        if (mapH > mapHMax) {
          mapH = mapHMax;
          mapW = mapH * aspect;
        }

        // Centrar verticalmente en la zona del mapa
        const mapX = 15;
        const mapY = 24 + (mapHMax - mapH) / 2;

        // Marco del mapa (Estilo Tarjeta)
        doc.setDrawColor(40, 47, 77); // #282f4d
        doc.setLineWidth(1);
        doc.setFillColor(15, 17, 26); // #0f111a
        doc.rect(mapX - 0.5, mapY - 0.5, mapW + 1, mapH + 1, 'F');
        
        // Insertar imagen del mapa
        doc.addImage(mapImgData, 'PNG', mapX, mapY, mapW, mapH);

        // 5. Sidebar Derecho de Métricas y Filtros
        const sideX = 220;
        const sideY = 24;
        const sideW = 62;
        const sideH = 155;

        // Tarjeta Sidebar (Fondo e iluminación de bordes)
        doc.setFillColor(15, 17, 26); // #0f111a
        doc.setDrawColor(99, 102, 241); // #6366f1
        doc.setLineWidth(0.3);
        doc.roundedRect(sideX, sideY, sideW, sideH, 3, 3, 'FD'); // FD = Fill then Draw

        let currentY = sideY + 7;

        // --- SUBSECCIÓN A: RESUMEN DE INDICADORES ---
        doc.setTextColor(99, 102, 241); // Indigo
        doc.setFont("helvetica", "bold");
        doc.setFontSize(8.5);
        doc.text("RESUMEN DE INDICADORES", sideX + 4, currentY);
        currentY += 1.5;
        doc.setDrawColor(40, 47, 77);
        doc.line(sideX + 4, currentY, sideX + sideW - 4, currentY);
        currentY += 5.5;

        // Obtener métricas reales de la app
        const filteredInc = getFilteredIncidents();
        
        // Total de incidentes
        doc.setFont("helvetica", "normal");
        doc.setFontSize(8);
        doc.setTextColor(156, 163, 175);
        doc.text("Incidentes Filtrados:", sideX + 6, currentY);
        doc.setFont("helvetica", "bold");
        doc.setTextColor(255, 255, 255);
        doc.text(filteredInc.length.toString(), sideX + sideW - 6, currentY, { align: "right" });
        currentY += 5;

        // Riesgo general
        let totalRisk = 0;
        let safeCount = 0;
        DATABASE.neighborhoods.forEach(col => {
          const colInc = filteredInc.filter(i => i.colonia === col.id);
          const score = calculateRiskIndexForColonia(col, colInc);
          totalRisk += score;
          if (score < 35) safeCount++;
        });
        const averageRisk = DATABASE.neighborhoods.length > 0 ? Math.round(totalRisk / DATABASE.neighborhoods.length) : 0;
        const generalRiskMeta = getRiskLevelMetadata(averageRisk);

        doc.setFont("helvetica", "normal");
        doc.setTextColor(156, 163, 175);
        doc.text("Riesgo Promedio:", sideX + 6, currentY);
        
        // Asignar color al texto de riesgo según severidad
        let rColor = [52, 199, 89]; // low
        if (generalRiskMeta.rating === "critical") rColor = [255, 59, 48];
        else if (generalRiskMeta.rating === "high") rColor = [255, 149, 0];
        else if (generalRiskMeta.rating === "moderate") rColor = [255, 204, 0];
        
        doc.setFont("helvetica", "bold");
        doc.setTextColor(rColor[0], rColor[1], rColor[2]);
        doc.text(`${averageRisk}% (${generalRiskMeta.label})`, sideX + sideW - 6, currentY, { align: "right" });
        currentY += 5;

        // Zonas Seguras
        doc.setFont("helvetica", "normal");
        doc.setTextColor(156, 163, 175);
        doc.text("Zonas Seguras (Bajo):", sideX + 6, currentY);
        doc.setFont("helvetica", "bold");
        doc.setTextColor(255, 255, 255);
        doc.text(safeCount.toString(), sideX + sideW - 6, currentY, { align: "right" });
        
        currentY += 9;

        // --- SUBSECCIÓN B: FILTROS APLICADOS ---
        doc.setTextColor(99, 102, 241);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(8.5);
        doc.text("FILTROS APLICADOS", sideX + 4, currentY);
        currentY += 1.5;
        doc.setDrawColor(40, 47, 77);
        doc.line(sideX + 4, currentY, sideX + sideW - 4, currentY);
        currentY += 5.5;

        // Nivel de severidad
        doc.setFont("helvetica", "normal");
        doc.setFontSize(7.5);
        doc.setTextColor(156, 163, 175);
        doc.text("Severidad:", sideX + 6, currentY);
        doc.setTextColor(255, 255, 255);
        const sevVal = state.selectedSeverity === "all" ? "Todos" : state.selectedSeverity;
        doc.text(sevVal, sideX + 35, currentY);
        currentY += 4.5;

        // Periodo horario
        doc.setTextColor(156, 163, 175);
        doc.text("Horario:", sideX + 6, currentY);
        doc.setTextColor(255, 255, 255);
        const timeVal = state.selectedTimePeriod === "all" ? "Todos" : state.selectedTimePeriod;
        doc.text(timeVal, sideX + 35, currentY);
        currentY += 4.5;

        // Rango de meses
        doc.setTextColor(156, 163, 175);
        doc.text("Rango Histórico:", sideX + 6, currentY);
        doc.setTextColor(255, 255, 255);
        let monthVal = "Histórico Total";
        if (state.selectedMonthIndex !== 12) {
          monthVal = timelineMonths[state.selectedMonthIndex].label;
        }
        doc.text(monthVal, sideX + 35, currentY);
        currentY += 4.5;

        // Delitos activos (contar seleccionados)
        doc.setTextColor(156, 163, 175);
        doc.text("Tipos Delito:", sideX + 6, currentY);
        doc.setTextColor(255, 255, 255);
        const totalDelitos = Object.keys(DATABASE.crimeTypes).length;
        const selDelitos = state.selectedCrimeTypes.length;
        doc.text(`${selDelitos} de ${totalDelitos} act.`, sideX + 35, currentY);

        currentY += 9;

        // --- SUBSECCIÓN C: LEYENDA ---
        doc.setTextColor(99, 102, 241);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(8.5);
        doc.text("LEYENDA DE RIESGOS", sideX + 4, currentY);
        currentY += 1.5;
        doc.setDrawColor(40, 47, 77);
        doc.line(sideX + 4, currentY, sideX + sideW - 4, currentY);
        currentY += 6;

        const legends = [
          { label: "Crítico (Riesgo >= 75%)", color: [255, 59, 48] },
          { label: "Alto (Riesgo 55% - 74%)", color: [255, 149, 0] },
          { label: "Moderado (Riesgo 35% - 54%)", color: [255, 204, 0] },
          { label: "Bajo (Riesgo < 35%)", color: [52, 199, 89] }
        ];

        legends.forEach(leg => {
          // Dibujar círculo color
          doc.setFillColor(leg.color[0], leg.color[1], leg.color[2]);
          doc.circle(sideX + 7, currentY - 1, 1.2, 'F');
          
          // Escribir texto de la leyenda
          doc.setFont("helvetica", "normal");
          doc.setFontSize(7);
          doc.setTextColor(156, 163, 175);
          doc.text(leg.label, sideX + 11, currentY);
          
          currentY += 4.5;
        });

        currentY += 6;

        // --- SUBSECCIÓN D: AUTORÍA ---
        doc.setTextColor(99, 102, 241);
        doc.setFont("helvetica", "bold");
        doc.setFontSize(8.5);
        doc.text("DESARROLLADO POR", sideX + 4, currentY);
        currentY += 1.5;
        doc.setDrawColor(40, 47, 77);
        doc.line(sideX + 4, currentY, sideX + sideW - 4, currentY);
        currentY += 6;

        doc.setFont("helvetica", "bold");
        doc.setFontSize(7.5);
        doc.setTextColor(255, 255, 255);
        doc.text("Chrystian Fabian Lozano Ramirez", sideX + 6, currentY);
        currentY += 3.8;
        
        doc.setFont("helvetica", "normal");
        doc.setFontSize(7);
        doc.setTextColor(0, 199, 252); // Cian link color
        doc.text("https://chrystian.dev", sideX + 6, currentY);

        // 6. Pie de Página del Reporte
        const footerY = 194;
        doc.setDrawColor(30, 35, 55); // #1e2337
        doc.setLineWidth(0.5);
        doc.line(15, footerY, pageW - 15, footerY);

        doc.setFont("helvetica", "normal");
        doc.setFontSize(7.5);
        doc.setTextColor(107, 114, 128); // #6b7280
        doc.text("Fuente de datos: Basado en el Observatorio Ciudadano Irapuato ¿Cómo Vamos? del periodo Julio 2025 - Junio 2026.", 15, footerY + 5);
        doc.text("Este documento es una representación digital generada localmente y contiene información estadística simulada.", 15, footerY + 8);
        doc.text("IRAPUATO SEGURO PORTAL", pageW - 15, footerY + 5, { align: "right" });

        // Guardar reporte PDF
        const dateFormatted = new Date().toISOString().slice(0, 10).replace(/-/g, "");
        doc.save(`reporte-irapuato-seguro-${dateFormatted}.pdf`);
        showToast("¡Reporte PDF descargado con éxito!", false);
      } catch (err) {
        console.error("Error al generar el PDF:", err);
        showToast("Error al exportar PDF. Intente de nuevo.", true);
      }
    }).catch(err => {
      console.error("Error al capturar el mapa para el PDF:", err);
      showToast("Error al capturar el mapa.", true);
    });
  }

  // Toast UI feedback helper
  function showToast(message, isDanger = false) {
    const container = document.getElementById("toastContainer");
    const toast = document.createElement("div");
    toast.className = `toast ${isDanger ? 'toast-danger' : ''}`;
    
    const icon = isDanger ? 'fa-triangle-exclamation' : 'fa-circle-check';
    toast.innerHTML = `
      <i class="fa-solid ${icon}"></i>
      <span>${message}</span>
    `;

    container.appendChild(toast);

    // Auto eliminar de UI al terminar animación (3.8 segundos en CSS)
    setTimeout(() => {
      toast.remove();
    }, 3800);
  }

  // ==========================================================================
  // ARRANQUE DE LA APP
  // ==========================================================================
  init();
});
