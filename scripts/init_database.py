import json
import random
import os
from datetime import datetime, timedelta

# 1. Definición de Tipos de Delito
CRIME_TYPES = {
    "Homicidio": {
        "icon": "fa-person-falling-burst",
        "color": "#ff3b30",
        "glow": "rgba(255, 59, 48, 0.4)",
        "desc": "Delito de alto impacto que atenta contra la vida.",
        "defaultSeverity": "Alta"
    },
    "Robo a Transeúnte": {
        "icon": "fa-person-running",
        "color": "#ff9500",
        "glow": "rgba(255, 149, 0, 0.4)",
        "desc": "Robo o despojo de pertenencias a peatones en la vía pública.",
        "defaultSeverity": "Media"
    },
    "Robo de Vehículo": {
        "icon": "fa-car-burst",
        "color": "#ffcc00",
        "glow": "rgba(255, 204, 0, 0.4)",
        "desc": "Robo de autos, camionetas o motocicletas estacionadas o con violencia.",
        "defaultSeverity": "Media"
    },
    "Asalto/Lesiones": {
        "icon": "fa-hand-fist",
        "color": "#ff3b30",
        "glow": "rgba(255, 59, 48, 0.4)",
        "desc": "Agresiones físicas, riñas o atracos con armas blancas/de fuego.",
        "defaultSeverity": "Alta"
    },
    "Extorsión/Fraude": {
        "icon": "fa-phone-volume",
        "color": "#00c7fc",
        "glow": "rgba(0, 199, 252, 0.4)",
        "desc": "Llamadas de extorsión telefónica, cobro de piso o estafas.",
        "defaultSeverity": "Baja"
    },
    "Vandalismo": {
        "icon": "fa-spray-can",
        "color": "#34c759",
        "glow": "rgba(52, 199, 89, 0.4)",
        "desc": "Daños a propiedad pública o privada, pintas y alteración del orden.",
        "defaultSeverity": "Baja"
    }
}

# 2. Definición de Colonias
NEIGHBORHOODS_DATA = [
    { "id": "centro", "name": "Centro Histórico", "lat": 20.6740385, "lon": -101.3467244, "baseRisk": 45 },
    { "id": "las_heras", "name": "Las Heras", "lat": 20.6838749, "lon": -101.3745169, "baseRisk": 78 },
    { "id": "doce_diciembre", "name": "12 de Diciembre", "lat": 20.6553993, "lon": -101.3585337, "baseRisk": 82 },
    { "id": "morelos", "name": "Morelos", "lat": 20.6735495, "lon": -101.3635734, "baseRisk": 75 },
    { "id": "san_vicente", "name": "San Vicente de Malvas", "lat": 20.6847313, "lon": -101.3011883, "baseRisk": 68 },
    { "id": "constitucion", "name": "Constitución de Apatzingán", "lat": 20.6887183, "lon": -101.3158933, "baseRisk": 72 },
    { "id": "san_cayetano", "name": "Villas de San Cayetano", "lat": 20.6917785, "lon": -101.3231556, "baseRisk": 80 },
    { "id": "san_roque", "name": "San Roque", "lat": 20.5975306, "lon": -101.3390406, "baseRisk": 85 },
    { "id": "san_miguel", "name": "Barrio de San Miguel", "lat": 20.6793706, "lon": -101.3484627, "baseRisk": 65 },
    { "id": "santa_julia", "name": "Santa Julia", "lat": 20.6821829, "lon": -101.3511746, "baseRisk": 60 },
    { "id": "las_reynas", "name": "Las Reynas", "lat": 20.690646, "lon": -101.3547149, "baseRisk": 55 },
    { "id": "purisima_jardin", "name": "Purísima del Jardín", "lat": 20.6425314, "lon": -101.3869939, "baseRisk": 70 },
    { "id": "valle_sol", "name": "Valle del Sol", "lat": 20.6537678, "lon": -101.3485967, "baseRisk": 62 },
    { "id": "ganadera", "name": "La Ganadera", "lat": 20.6695, "lon": -101.3725, "baseRisk": 58 },
    { "id": "playa_azul", "name": "Playa Azul", "lat": 20.6639182, "lon": -101.3648503, "baseRisk": 50 },
    { "id": "san_martin", "name": "San Martín de Porres", "lat": 20.6622999, "lon": -101.3800252, "baseRisk": 74 },
    { "id": "los_cobos", "name": "Los Cobos", "lat": 20.7023987, "lon": -101.3676474, "baseRisk": 48 },
    { "id": "bella_vista", "name": "Bella Vista", "lat": 20.6970, "lon": -101.3420, "baseRisk": 42 },
    { "id": "juarez", "name": "Benito Juárez", "lat": 20.7045354, "lon": -101.35827, "baseRisk": 52 },
    { "id": "flores_magon", "name": "Flores Magón Sur", "lat": 20.662544, "lon": -101.3432126, "baseRisk": 64 },
    { "id": "tierra_nueva", "name": "Tierra Nueva", "lat": 20.6572094, "lon": -101.3265889, "baseRisk": 66 },
    { "id": "hacienda_virgen", "name": "Hacienda La Virgen", "lat": 20.6520243, "lon": -101.3324536, "baseRisk": 56 }
]

# 3. Incidentes Históricos Base (Julio 2025 - Junio 2026)
HISTORICAL_INCIDENTS = [
  {
    "id": "inc_1",
    "type": "Homicidio",
    "colonia": "san_roque",
    "lat": 20.597810, "lon": -101.339240,
    "date": "2025-07-04T23:15:00",
    "timePeriod": "Noche",
    "severity": "Alta",
    "description": "Ataque directo con arma de fuego a las afueras de una tienda de conveniencia en la calle Principal."
  },
  {
    "id": "inc_2",
    "type": "Robo a Transeúnte",
    "colonia": "centro",
    "lat": 20.674310, "lon": -101.347020,
    "date": "2025-07-12T10:30:00",
    "timePeriod": "Mañana",
    "severity": "Media",
    "description": "Sujeto despojó de teléfono celular y cartera a estudiante cerca del Templo del Hospitalito."
  },
  {
    "id": "inc_3",
    "type": "Robo de Vehículo",
    "colonia": "las_reynas",
    "lat": 20.691140, "lon": -101.355120,
    "date": "2025-07-19T21:40:00",
    "timePeriod": "Noche",
    "severity": "Media",
    "description": "Robo de camioneta pickup estacionada sobre Paseo de las Reynas."
  },
  {
    "id": "inc_4",
    "type": "Asalto/Lesiones",
    "colonia": "las_heras",
    "lat": 20.684250, "lon": -101.375120,
    "date": "2025-07-28T19:50:00",
    "timePeriod": "Noche",
    "severity": "Alta",
    "description": "Riña con arma blanca entre particulares en la calle Limón, dejando una persona lesionada."
  },
  {
    "id": "inc_5",
    "type": "Vandalismo",
    "colonia": "doce_diciembre",
    "lat": 20.655810, "lon": -101.358990,
    "date": "2025-08-03T15:20:00",
    "timePeriod": "Tarde",
    "severity": "Baja",
    "description": "Grupo de jóvenes realizando pintas (graffiti) en bardas de viviendas privadas en la Av. Solidaridad."
  },
  {
    "id": "inc_6",
    "type": "Extorsión/Fraude",
    "colonia": "centro",
    "lat": 20.673820, "lon": -101.345850,
    "date": "2025-08-11T11:00:00",
    "timePeriod": "Mañana",
    "severity": "Baja",
    "description": "Comerciante reportó llamada de extorsión telefónica exigiendo 'cobro de cuota'. Colgó a tiempo."
  },
  {
    "id": "inc_7",
    "type": "Homicidio",
    "colonia": "san_cayetano",
    "lat": 20.692010, "lon": -101.323540,
    "date": "2025-08-22T02:10:00",
    "timePeriod": "Noche",
    "severity": "Alta",
    "description": "Hallazgo de persona sin vida con impactos de proyectil de arma de fuego en lote baldío."
  },
  {
    "id": "inc_8",
    "type": "Robo a Transeúnte",
    "colonia": "morelos",
    "lat": 20.673980, "lon": -101.364010,
    "date": "2025-08-30T20:15:00",
    "timePeriod": "Noche",
    "severity": "Media",
    "description": "Asalto a mano armada por parte de dos sujetos a bordo de una motocicleta en la Av. Reforma."
  },
  {
    "id": "inc_9",
    "type": "Robo de Vehículo",
    "colonia": "san_miguel",
    "lat": 20.680010, "lon": -101.349100,
    "date": "2025-09-05T04:30:00",
    "timePeriod": "Noche",
    "severity": "Media",
    "description": "Robo de motocicleta Italika color negra estacionada afuera de domicilio particular."
  },
  {
    "id": "inc_10",
    "type": "Asalto/Lesiones",
    "colonia": "san_martin",
    "lat": 20.662650, "lon": -101.380420,
    "date": "2025-09-14T22:00:00",
    "timePeriod": "Noche",
    "severity": "Alta",
    "description": "Asalto violento a transeúnte; víctima fue agredida físicamente tras oponer resistencia al robo."
  },
  {
    "id": "inc_11",
    "type": "Vandalismo",
    "colonia": "morelos",
    "lat": 20.673120, "lon": -101.363120,
    "date": "2025-09-22T17:40:00",
    "timePeriod": "Tarde",
    "severity": "Baja",
    "description": "Daños causados a luminarias públicas y cristales de paradero de autobús por vándalos."
  },
  {
    "id": "inc_12",
    "type": "Homicidio",
    "colonia": "las_heras",
    "lat": 20.683410, "lon": -101.373990,
    "date": "2025-09-29T21:10:00",
    "timePeriod": "Noche",
    "severity": "Alta",
    "description": "Intervención de la fiscalía tras agresión armada contra fachada de vivienda que dejó un fallecido."
  },
  {
    "id": "inc_13",
    "type": "Robo a Transeúnte",
    "colonia": "santa_julia",
    "lat": 20.682540, "lon": -101.351650,
    "date": "2025-10-06T13:15:00",
    "timePeriod": "Tarde",
    "severity": "Media",
    "description": "Arrebato de bolsa de mano a mujer mayor mientras caminaba por la calle Tulipanes."
  },
  {
    "id": "inc_14",
    "type": "Extorsión/Fraude",
    "colonia": "las_reynas",
    "lat": 20.690120, "lon": -101.354120,
    "date": "2025-10-15T15:00:00",
    "timePeriod": "Tarde",
    "severity": "Media",
    "description": "Fraude mediante compra-venta falsa de vehículo reportado en la zona comercial aledaña."
  },
  {
    "id": "inc_15",
    "type": "Robo de Vehículo",
    "colonia": "valle_sol",
    "lat": 20.654010, "lon": -101.349010,
    "date": "2025-10-23T19:30:00",
    "timePeriod": "Noche",
    "severity": "Media",
    "description": "Sujetos armados despojaron a conductor de su vehículo sedán al llegar a su domicilio."
  },
  {
    "id": "inc_16",
    "type": "Asalto/Lesiones",
    "colonia": "doce_diciembre",
    "lat": 20.655100, "lon": -101.358110,
    "date": "2025-11-01T20:50:00",
    "timePeriod": "Noche",
    "severity": "Alta",
    "description": "Atraco violento en tienda de abarrotes; el tendero fue herido levemente con arma blanca."
  },
  {
    "id": "inc_17",
    "type": "Homicidio",
    "colonia": "san_roque",
    "lat": 20.597110, "lon": -101.338810,
    "date": "2025-11-09T23:45:00",
    "timePeriod": "Noche",
    "severity": "Alta",
    "description": "Enfrentamiento violento en las inmediaciones de la colonia que derivó en la pérdida de una vida."
  },
  {
    "id": "inc_18",
    "type": "Vandalismo",
    "colonia": "purisima_jardin",
    "lat": 20.642990, "lon": -101.387220,
    "date": "2025-11-18T18:25:00",
    "timePeriod": "Tarde",
    "severity": "Baja",
    "description": "Deterioro de juegos infantiles en el parque vecinal y quema de basura deliberada."
  },
  {
    "id": "inc_19",
    "type": "Robo a Transeúnte",
    "colonia": "flores_magon",
    "lat": 20.662890, "lon": -101.343890,
    "date": "2025-11-26T07:15:00",
    "timePeriod": "Mañana",
    "severity": "Media",
    "description": "Robo de mochila y pertenencias a obrero que se dirigía a su parada de transporte de personal."
  },
  {
    "id": "inc_20",
    "type": "Robo de Vehículo",
    "colonia": "tierra_nueva",
    "lat": 20.657510, "lon": -101.326900,
    "date": "2025-12-03T18:40:00",
    "timePeriod": "Tarde",
    "severity": "Media",
    "description": "Cristalazo y robo de objetos de valor del interior de vehículo estacionado."
  },
  {
    "id": "inc_21",
    "type": "Asalto/Lesiones",
    "colonia": "ganadera",
    "lat": 20.670010, "lon": -101.373010,
    "date": "2025-12-11T20:10:00",
    "timePeriod": "Noche",
    "severity": "Media",
    "description": "Asalto a repartidor de comida rápida por dos delincuentes armados con navajas."
  },
  {
    "id": "inc_22",
    "type": "Homicidio",
    "colonia": "constitucion",
    "lat": 20.689020, "lon": -101.316220,
    "date": "2025-12-21T01:30:00",
    "timePeriod": "Noche",
    "severity": "Alta",
    "description": "Detonaciones de arma de fuego en vía pública resultando en el deceso de un hombre."
  },
  {
    "id": "inc_23",
    "type": "Extorsión/Fraude",
    "colonia": "playa_azul",
    "lat": 20.664210, "lon": -101.365120,
    "date": "2025-12-29T10:45:00",
    "timePeriod": "Mañana",
    "severity": "Baja",
    "description": "Cobro indebido de estacionamiento público mediante amenazas por sujetos no identificados."
  },
  {
    "id": "inc_24",
    "type": "Robo de Vehículo",
    "colonia": "hacienda_virgen",
    "lat": 20.652410, "lon": -101.332850,
    "date": "2026-01-05T22:30:00",
    "timePeriod": "Noche",
    "severity": "Media",
    "description": "Hurto de motocicleta de cochera abierta durante altas horas de la noche."
  },
  {
    "id": "inc_25",
    "type": "Asalto/Lesiones",
    "colonia": "san_vicente",
    "lat": 20.685120, "lon": -101.301540,
    "date": "2026-01-14T21:15:00",
    "timePeriod": "Noche",
    "severity": "Alta",
    "description": "Riña familiar campal en festividad local que terminó en lesiones de gravedad con machete."
  },
  {
    "id": "inc_26",
    "type": "Homicidio",
    "colonia": "doce_diciembre",
    "lat": 20.655950, "lon": -101.358850,
    "date": "2026-01-23T22:50:00",
    "timePeriod": "Noche",
    "severity": "Alta",
    "description": "Homicidio doloso derivado de un ataque armado directo en la calle San Juan."
  },
  {
    "id": "inc_27",
    "type": "Robo a Transeúnte",
    "colonia": "centro",
    "lat": 20.673890, "lon": -101.346120,
    "date": "2026-02-02T16:40:00",
    "timePeriod": "Tarde",
    "severity": "Media",
    "description": "Arrebato de teléfono celular a una mujer en el pasaje peatonal junto a la Presidencia Municipal."
  },
  {
    "id": "inc_28",
    "type": "Vandalismo",
    "colonia": "san_cayetano",
    "lat": 20.692210, "lon": -101.323950,
    "date": "2026-02-10T12:00:00",
    "timePeriod": "Tarde",
    "severity": "Baja",
    "description": "Pintadas de grafiti en cristales del centro comunitario recién inaugurado."
  },
  {
    "id": "inc_29",
    "type": "Homicidio",
    "colonia": "las_heras",
    "lat": 20.684120, "lon": -101.374850,
    "date": "2026-02-18T20:30:00",
    "timePeriod": "Noche",
    "severity": "Alta",
    "description": "Ataque directo perpetrado por motociclistas contra una barbería local, fallece una persona."
  },
  {
    "id": "inc_30",
    "type": "Robo de Vehículo",
    "colonia": "santa_julia",
    "lat": 20.681980, "lon": -101.350850,
    "date": "2026-02-26T05:20:00",
    "timePeriod": "Mañana",
    "severity": "Media",
    "description": "Hurto de un automóvil sedan Nissan Tsuru estacionado frente a la iglesia."
  },
  {
    "id": "inc_31",
    "type": "Asalto/Lesiones",
    "colonia": "morelos",
    "lat": 20.673650, "lon": -101.363990,
    "date": "2026-03-05T20:10:00",
    "timePeriod": "Noche",
    "severity": "Media",
    "description": "Asalto violento a gasolinera; amagaron a los despachadores con armas cortas."
  },
  {
    "id": "inc_32",
    "type": "Extorsión/Fraude",
    "colonia": "las_reynas",
    "lat": 20.690850, "lon": -101.355200,
    "date": "2026-03-13T11:30:00",
    "timePeriod": "Mañana",
    "severity": "Baja",
    "description": "Denuncia de extorsión mediante cobro de piso virtual a locatarios del mercado regional."
  },
  {
    "id": "inc_33",
    "type": "Homicidio",
    "colonia": "san_roque",
    "lat": 20.597950, "lon": -101.339250,
    "date": "2026-03-22T23:00:00",
    "timePeriod": "Noche",
    "severity": "Alta",
    "description": "Homicidio con proyectiles de arma de fuego en las inmediaciones del campo deportivo de la colonia."
  },
  {
    "id": "inc_34",
    "type": "Robo a Transeúnte",
    "colonia": "san_miguel",
    "lat": 20.679120, "lon": -101.348120,
    "date": "2026-03-30T19:45:00",
    "timePeriod": "Noche",
    "severity": "Media",
    "description": "Despojo violento de celular a una joven por parte de un sujeto que huyó corriendo hacia el arroyo."
  },
  {
    "id": "inc_35",
    "type": "Robo de Vehículo",
    "colonia": "valle_sol",
    "lat": 20.653450, "lon": -101.348120,
    "date": "2026-04-07T03:00:00",
    "timePeriod": "Noche",
    "severity": "Media",
    "description": "Robo de auto estacionado en la vía pública; ladrones forzaron la chapa de la puerta."
  },
  {
    "id": "inc_36",
    "type": "Asalto/Lesiones",
    "colonia": "tierra_nueva",
    "lat": 20.657020, "lon": -101.326120,
    "date": "2026-04-15T21:10:00",
    "timePeriod": "Noche",
    "severity": "Media",
    "description": "Atraco violento en farmacia de la colonia; daños materiales al forzar la caja registradora."
  },
  {
    "id": "inc_37",
    "type": "Vandalismo",
    "colonia": "bella_vista",
    "lat": 20.697210, "lon": -101.342510,
    "date": "2026-04-23T22:30:00",
    "timePeriod": "Noche",
    "severity": "Baja",
    "description": "Pintado de grafitis en monumentos y paradas de camión en la zona residencial."
  },
  {
    "id": "inc_38",
    "type": "Homicidio",
    "colonia": "san_cayetano",
    "lat": 20.691520, "lon": -101.322950,
    "date": "2026-05-02T22:00:00",
    "timePeriod": "Noche",
    "severity": "Alta",
    "description": "Persona del sexo masculino agredida a disparos en un parque público."
  },
  {
    "id": "inc_39",
    "type": "Robo a Transeúnte",
    "colonia": "purisima_jardin",
    "lat": 20.642120, "lon": -101.386210,
    "date": "2026-05-10T14:15:00",
    "timePeriod": "Tarde",
    "severity": "Media",
    "description": "Asalto a transeúnte con arma blanca en callejón poco transitado cerca del río."
  },
  {
    "id": "inc_40",
    "type": "Robo de Vehículo",
    "colonia": "las_heras",
    "lat": 20.684250, "lon": -101.374990,
    "date": "2026-05-18T18:50:00",
    "timePeriod": "Tarde",
    "severity": "Media",
    "description": "Despojo violento de una motocicleta en semáforo de cruce principal."
  },
  {
    "id": "inc_41",
    "type": "Asalto/Lesiones",
    "colonia": "san_martin",
    "lat": 20.662010, "lon": -101.379850,
    "date": "2026-05-26T20:30:00",
    "timePeriod": "Noche",
    "severity": "Alta",
    "description": "Detonaciones de arma de fuego en riña callejera dejan una persona herida en una pierna."
  },
  {
    "id": "inc_42",
    "type": "Homicidio",
    "colonia": "doce_diciembre",
    "lat": 20.655210, "lon": -101.358210,
    "date": "2026-06-01T23:15:00",
    "timePeriod": "Noche",
    "severity": "Alta",
    "description": "Incidente armado de alta gravedad reportado cerca del bulevar; una víctima mortal."
  },
  {
    "id": "inc_43",
    "type": "Extorsión/Fraude",
    "colonia": "centro",
    "lat": 20.674120, "lon": -101.346990,
    "date": "2026-06-02T12:00:00",
    "timePeriod": "Tarde",
    "severity": "Baja",
    "description": "Simulación de sorteo fraudulento detectado en la plazuela comercial del Centro."
  }
]

# 4. Generar incidentes adicionales aleatorios
def generate_additional_incidents():
    crimes = list(CRIME_TYPES.keys())
    periods = ["Mañana", "Tarde", "Noche"]
    severities = ["Baja", "Media", "Alta"]
    
    details = {
        "Homicidio": [
            "Agresión letal con arma de fuego frente a establecimiento.",
            "Ataque directo que cobró la vida de una persona en vía pública.",
            "Ataque armado en riña entre presuntas bandas rivales."
        ],
        "Robo a Transeúnte": [
            "Robo de celular y dinero bajo amenazas por ciclista.",
            "Sujeto arrebató bolso con pertenencias y huyó con cómplice.",
            "Asalto con navaja a transeúnte en cruce con poca iluminación."
        ],
        "Robo de Vehículo": [
            "Robo de motocicleta estacionada frente a local comercial.",
            "Cristalazo a auto sedán sustrayendo equipo de sonido y bolsas.",
            "Robo violento de automóvil despojando al dueño al estacionarse."
        ],
        "Asalto/Lesiones": [
            "Atraco a mini-supermercado vecinal amagando con arma blanca.",
            "Riña campal vecinal que deja heridos con objetos contundentes.",
            "Agresión física a transeúnte al intentar resistirse a asalto."
        ],
        "Extorsión/Fraude": [
            "Llamada telefónica intimidatoria a locatario exigiendo depósitos.",
            "Intento de estafa mediante billetes falsos en negocio pequeño.",
            "Extorsión telefónica simulando secuestro de familiar."
        ],
        "Vandalismo": [
            "Fachada dañada con grafitis alusivos a pandillas.",
            "Pintado ilegal en cortina metálica de comercio céntrico.",
            "Daño intencional a medidores de agua de casas habitación."
        ]
    }

    incidents = list(HISTORICAL_INCIDENTS)
    
    months = [
        (2025, 7), (2025, 8), (2025, 9), (2025, 10), (2025, 11), (2025, 12),
        (2026, 1), (2026, 2), (2026, 3), (2026, 4), (2026, 5), (2026, 6)
    ]
    
    # Usar semilla reproducible
    random.seed(42)
    
    for i in range(85):
        year, month = random.choice(months)
        day = random.randint(1, 28)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        
        colonia = random.choice(NEIGHBORHOODS_DATA)
        
        # Más probabilidad de crímenes severos en colonias con alto riesgo base
        if colonia["baseRisk"] > 75:
            rand_val = random.random()
            if rand_val < 0.25:
                crime_type = "Homicidio"
            elif rand_val < 0.55:
                crime_type = "Asalto/Lesiones"
            elif rand_val < 0.75:
                crime_type = "Robo de Vehículo"
            elif rand_val < 0.90:
                crime_type = "Robo a Transeúnte"
            else:
                crime_type = "Vandalismo"
        else:
            rand_val = random.random()
            if rand_val < 0.10:
                crime_type = "Homicidio"
            elif rand_val < 0.30:
                crime_type = "Robo a Transeúnte"
            elif rand_val < 0.50:
                crime_type = "Robo de Vehículo"
            elif rand_val < 0.70:
                crime_type = "Extorsión/Fraude"
            elif rand_val < 0.85:
                crime_type = "Vandalismo"
            else:
                crime_type = "Asalto/Lesiones"
                
        severity = CRIME_TYPES[crime_type]["defaultSeverity"]
        desc = random.choice(details[crime_type])
        
        if hour >= 6 and hour < 12:
            time_period = "Mañana"
        elif hour >= 12 and hour < 19:
            time_period = "Tarde"
        else:
            time_period = "Noche"
            
        offset_lat = (random.random() - 0.5) * 0.007
        offset_lon = (random.random() - 0.5) * 0.007
        
        date_str = f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00"
        
        incidents.append({
            "id": f"gen_inc_{i}",
            "type": crime_type,
            "colonia": colonia["id"],
            "lat": colonia["lat"] + offset_lat,
            "lon": colonia["lon"] + offset_lon,
            "date": date_str,
            "timePeriod": time_period,
            "severity": severity,
            "description": desc
        })
        
    return incidents

# 5. Generar JSON final
def init_db():
    full_db = {
        "crimeTypes": CRIME_TYPES,
        "neighborhoods": NEIGHBORHOODS_DATA,
        "incidents": generate_additional_incidents()
    }
    
    os.makedirs("/Users/chrystian/Documents/Mapa Irapuato/data", exist_ok=True)
    
    with open("/Users/chrystian/Documents/Mapa Irapuato/data/database.json", "w", encoding="utf-8") as f:
        json.dump(full_db, f, indent=2, ensure_ascii=False)
        
    print("Database JSON initialized successfully.")

if __name__ == "__main__":
    init_db()
