import json
import random
import os
from datetime import datetime

# Rutas de archivos
DB_PATH = "/Users/chrystian/Documents/Mapa Irapuato/data/database.json"

# Si corre en GitHub Actions, la ruta relativa será diferente (el directorio de trabajo es la raíz del repositorio)
if not os.path.exists(DB_PATH):
    DB_PATH = "data/database.json"

# Descripciones simuladas de acuerdo con el tipo de delito
DETAILS_TEMPLATES = {
    "Homicidio": [
        "Ataque con proyectil de arma de fuego reportado por vecinos en calle principal.",
        "Incidente armado frente a negocio de comida que deja una víctima mortal.",
        "Riña violenta entre grupos que culmina en deceso por herida de arma."
    ],
    "Robo a Transeúnte": [
        "Sujetos despojaron a peatón de sus pertenencias (celular y cartera) mediante amenazas.",
        "Arrebato de pertenencias a transeúnte que caminaba por callejón poco iluminado.",
        "Asalto en vía pública con arma blanca; el asaltante escapó a bordo de una bicicleta."
    ],
    "Robo de Vehículo": [
        "Robo de motocicleta estacionada en la banqueta; dueños reportaron falta del vehículo.",
        "Sujetos encapuchados obligaron a conductor a descender de su vehículo en semáforo.",
        "Robo a interior de vehículo (cristalazo) llevándose bolsos y herramientas."
    ],
    "Asalto/Lesiones": [
        "Atraco violento en tienda de abarrotes de la colonia; lesionan levemente al encargado.",
        "Riña callejera que deja dos personas heridas por golpes y objetos contundentes.",
        "Asalto a repartidor local quitándole la mercancía bajo amenazas físicas."
    ],
    "Extorsión/Fraude": [
        "Comerciante local recibió llamada intimidatoria exigiendo pago de cuota telefónica.",
        "Estafa reportada mediante billete falso de alta denominación en establecimiento comercial.",
        "Fraude electrónico mediante simulación de entrega de paquetes a domicilio."
    ],
    "Vandalismo": [
        "Bardas de viviendas particulares vandalizadas con pintas de aerosol.",
        "Daño intencional a luminarias y botes de basura del parque público.",
        "Cristales de paradero de autobús dañados deliberadamente por grupo de desconocidos."
    ]
}

def load_database():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_database(db):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def generate_monthly_crimes(year, month, neighborhoods, crime_types):
    """Genera una tanda realista de 5 a 12 incidentes simulados para un mes/año dado"""
    incidents = []
    num_incidents = random.randint(5, 12)
    
    crimes = list(crime_types.keys())
    periods = ["Mañana", "Tarde", "Noche"]
    
    for i in range(num_incidents):
        day = random.randint(1, 28)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        
        colonia = random.choice(neighborhoods)
        
        # Determinar delito condicionado por el riesgo de la colonia
        rand_val = random.random()
        if colonia["baseRisk"] > 75:
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
                
        severity = crime_types[crime_type]["defaultSeverity"]
        desc = random.choice(DETAILS_TEMPLATES[crime_type])
        
        if hour >= 6 and hour < 12:
            time_period = "Mañana"
        elif hour >= 12 and hour < 19:
            time_period = "Tarde"
        else:
            time_period = "Noche"
            
        # Desviación de coordenadas respecto al centroide de la colonia
        offset_lat = (random.random() - 0.5) * 0.007
        offset_lon = (random.random() - 0.5) * 0.007
        
        date_str = f"{year}-{month:02d}-{day:02d}T{hour:02d}:{minute:02d}:00"
        timestamp_id = int(datetime(year, month, day, hour, minute).timestamp())
        
        incidents.append({
            "id": f"auto_inc_{timestamp_id}_{random.randint(100,999)}",
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

def main():
    print(f"Abriendo base de datos en: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("ERROR: La base de datos no existe.")
        return
        
    db = load_database()
    incidents = db.get("incidents", [])
    
    # 1. Encontrar la fecha del último incidente registrado
    latest_date_str = "2025-07-01T00:00:00"
    for inc in incidents:
        if inc["date"] > latest_date_str:
            latest_date_str = inc["date"]
            
    latest_date = datetime.fromisoformat(latest_date_str)
    latest_y = latest_date.year
    latest_m = latest_date.month
    
    # 2. Obtener fecha de ejecución actual
    now = datetime.now()
    current_y = now.year
    current_m = now.month
    
    print(f"Último mes registrado: {latest_y:04d}-{latest_m:02d}")
    print(f"Mes de ejecución actual: {current_y:04d}-{current_m:02d}")
    
    # 3. Calcular e incrementar meses faltantes
    new_incidents = []
    
    # Bucle para avanzar mes a mes
    while (latest_y, latest_m) < (current_y, current_m):
        # Avanzar al siguiente mes
        latest_m += 1
        if latest_m > 12:
            latest_m = 1
            latest_y += 1
            
        print(f"Generando incidencias del mes: {latest_y:04d}-{latest_m:02d}...")
        monthly_batch = generate_monthly_crimes(latest_y, latest_m, db["neighborhoods"], db["crimeTypes"])
        new_incidents.extend(monthly_batch)
        print(f"  -> Creados {len(monthly_batch)} incidentes para {latest_y:04d}-{latest_m:02d}.")

    # 4. Guardar si hubo actualizaciones
    if new_incidents:
        db["incidents"].extend(new_incidents)
        save_database(db)
        print(f"PROCESO TERMINADO. Se añadieron {len(new_incidents)} nuevos incidentes en total.")
    else:
        print("PROCESO TERMINADO. La base de datos ya se encuentra al día con la fecha actual.")

if __name__ == "__main__":
    main()
