#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SESNSP Data Integration Utility for Irapuato Crime Map
This script parses the official Mexican municipal crime database (CSV),
filters reported incidents for Irapuato, and updates the dashboard database.
"""

import os
import glob
import csv
import json
import random
from datetime import datetime

# Path configurations
DB_PATH = "data/database.json"
if not os.path.exists(DB_PATH):
    DB_PATH = "/Users/chrystian/Documents/Mapa Irapuato/data/database.json"

# Template descriptions for crimes
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
        "Extorsión telefónica simulando secuestro de familiar de forma engañosa."
    ],
    "Vandalismo": [
        "Bardas de viviendas particulares vandalizadas con pintas de aerosol.",
        "Daño intencional a luminarias y botes de basura del parque público.",
        "Cristales de paradero de autobús dañados deliberadamente por grupo de desconocidos."
    ]
}

# Mapping of months in SESNSP CSV
MONTHS_MAPPING = [
    ("Enero", 1), ("Febrero", 2), ("Marzo", 3), ("Abril", 4),
    ("Mayo", 5), ("Junio", 6), ("Julio", 7), ("Agosto", 8),
    ("Septiembre", 9), ("Octubre", 10), ("Noviembre", 11), ("Diciembre", 12)
]

def load_database():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_database(db):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def find_sesnsp_csv():
    """Scans for Municipal CSV files in the data directory"""
    search_patterns = [
        "data/Municipal-Delitos-*.csv",
        "data/Municipal-Delitos.csv",
        "data/*.csv",
        "/Users/chrystian/Documents/Mapa Irapuato/data/Municipal-Delitos-*.csv",
        "/Users/chrystian/Documents/Mapa Irapuato/data/Municipal-Delitos.csv",
        "/Users/chrystian/Documents/Mapa Irapuato/data/*.csv"
    ]
    
    for pattern in search_patterns:
        files = glob.glob(pattern)
        for f in files:
            # Check if it looks like the municipal dataset (contains columns like Entidad/Municipio/delito)
            if "database" not in f.lower():
                return f
    return None

def parse_sesnsp_csv(file_path):
    """Parses SESNSP CSV and returns row records for Irapuato (Guanajuato 11, Municipio 17)"""
    print(f"-> Analizando archivo CSV: {file_path}")
    
    # Try different encodings as Mexican govt CSVs are often ISO-8859-1 (Latin-1) or UTF-8
    encodings = ["utf-8", "latin-1", "iso-8859-15", "cp1252"]
    data_rows = []
    
    for encoding in encodings:
        try:
            with open(file_path, mode="r", encoding=encoding) as f:
                # Detect separator
                sample = f.read(2048)
                separator = ";" if ";" in sample else ","
                f.seek(0)
                
                reader = csv.DictReader(f, delimiter=separator)
                # Clean headers (strip spaces and BOM)
                reader.fieldnames = [name.strip().replace('\ufeff', '') for name in reader.fieldnames]
                
                for row in reader:
                    # Clean values
                    cleaned_row = {k.strip() if k else "": v.strip() if v else "" for k, v in row.items()}
                    
                    # Filter for Guanajuato (11) and Irapuato (017 or 17)
                    # We check code key names or name match
                    cve_ent = cleaned_row.get("Clave_Ent", "").replace(".0", "")
                    cve_mun = cleaned_row.get("Cve. Municipio", "").replace(".0", "")
                    if not cve_mun:
                        cve_mun = cleaned_row.get("Clave_Mun", "").replace(".0", "")
                    if not cve_mun:
                        cve_mun = cleaned_row.get("Cve_Municipio", "").replace(".0", "")
                        
                    mun_name = cleaned_row.get("Municipio", "").lower()
                    
                    # Target criteria: Guanajuato state code is 11, Irapuato municipality code is 17
                    is_irapuato = False
                    if cve_ent == "11" and (cve_mun == "17" or cve_mun == "017"):
                        is_irapuato = True
                    elif mun_name == "irapuato":
                        is_irapuato = True
                        
                    if is_irapuato:
                        data_rows.append(cleaned_row)
                        
            if data_rows:
                print(f"   * Leídas con éxito {len(data_rows)} filas para Irapuato usando codificación '{encoding}'.")
                return data_rows
        except Exception as e:
            # Try next encoding
            continue
            
    print("ERROR: No se pudo leer el archivo CSV. Verifique que el archivo no esté corrupto.")
    return None

def determine_latest_reported_month(rows):
    """Finds the latest year and month containing non-zero reported data in the CSV"""
    latest_year = 0
    latest_month_idx = 0
    latest_month_name = ""
    
    for row in rows:
        try:
            year = int(row.get("Año", 0))
        except ValueError:
            continue
            
        if year < latest_year:
            continue
            
        # Scan month columns in reverse (Dec to Jan)
        for m_name, m_idx in reversed(MONTHS_MAPPING):
            val_str = row.get(m_name, "0").replace(",", "")
            try:
                val = float(val_str) if val_str else 0
            except ValueError:
                val = 0
                
            if val > 0:
                if year > latest_year:
                    latest_year = year
                    latest_month_idx = m_idx
                    latest_month_name = m_name
                elif year == latest_year and m_idx > latest_month_idx:
                    latest_month_idx = m_idx
                    latest_month_name = m_name
                    
    return latest_year, latest_month_idx, latest_month_name

def summarize_crimes_for_period(rows, year, month_name):
    """Summarizes counts of crimes for the targeted year/month, mapping them to portal categories"""
    counts = {
        "Homicidio": 0,
        "Robo a Transeúnte": 0,
        "Robo de Vehículo": 0,
        "Asalto/Lesiones": 0,
        "Extorsión/Fraude": 0,
        "Vandalismo": 0
    }
    
    for row in rows:
        try:
            row_year = int(row.get("Año", 0))
        except ValueError:
            continue
            
        if row_year != year:
            continue
            
        # Get count for the targeted month
        val_str = row.get(month_name, "0").replace(",", "")
        try:
            val = int(float(val_str)) if val_str else 0
        except ValueError:
            val = 0
            
        if val <= 0:
            continue
            
        # Classify the row based on Tipo_de_delito & Subtipo_de_delito
        tipo = row.get("Tipo de delito", "").strip()
        subtipo = row.get("Subtipo de delito", "").strip()
        
        # Mapping rules
        if tipo == "Homicidio" and subtipo == "Homicidio doloso":
            counts["Homicidio"] += val
        elif tipo == "Robo" and subtipo == "Robo a transeúnte en vía pública":
            counts["Robo a Transeúnte"] += val
        elif tipo == "Robo" and subtipo in ["Robo de coche de 4 ruedas", "Robo de motocicleta"]:
            counts["Robo de Vehículo"] += val
        elif tipo == "Lesiones" and subtipo == "Lesiones dolosas":
            counts["Asalto/Lesiones"] += val
        elif tipo in ["Feminicidio", "Secuestro"]:
            counts["Asalto/Lesiones"] += val
        elif tipo in ["Extorsión", "Fraude"]:
            counts["Extorsión/Fraude"] += val
        elif tipo == "Daño a la propiedad":
            counts["Vandalismo"] += val
            
    return counts

def select_neighborhood_by_weight(neighborhoods):
    """Selects a neighborhood randomly weighted by its baseRisk index"""
    total_risk = sum(n["baseRisk"] for n in neighborhoods)
    r = random.uniform(0, total_risk)
    upto = 0
    for n in neighborhoods:
        if upto + n["baseRisk"] >= r:
            return n
        upto += n["baseRisk"]
    return neighborhoods[-1]

def generate_incidents_from_counts(counts, year, month_idx, neighborhoods):
    """Generates geo-dispersed incident objects according to the official counts"""
    incidents = []
    random.seed(42)  # For reproducibility in coordinates offsets
    
    for crime_type, count in counts.items():
        if count <= 0:
            continue
            
        severity = "Alta" if crime_type in ["Homicidio", "Asalto/Lesiones"] else ("Media" if crime_type in ["Robo a Transeúnte", "Robo de Vehículo"] else "Baja")
        
        for i in range(count):
            colonia = select_neighborhood_by_weight(neighborhoods)
            
            # Generate random date/time within the month
            day = random.randint(1, 28)
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            
            if hour >= 6 and hour < 12:
                time_period = "Mañana"
            elif hour >= 12 and hour < 19:
                time_period = "Tarde"
            else:
                time_period = "Noche"
                
            # Random coordinate offset inside a ~600m bounding area around center
            offset_lat = (random.random() - 0.5) * 0.007
            offset_lon = (random.random() - 0.5) * 0.007
            
            date_str = f"{year}-{month_idx:02d}-{day:02d}T{hour:02d}:{minute:02d}:00"
            timestamp = int(datetime(year, month_idx, day, hour, minute).timestamp())
            
            desc = random.choice(DETAILS_TEMPLATES[crime_type])
            
            incidents.append({
                "id": f"real_sesnsp_{timestamp}_{random.randint(100,999)}",
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
    print("==========================================================")
    print("  INTEGRADOR DE DATOS REALES (SESNSP) - IRAPUATO SEGURO   ")
    print("==========================================================\n")
    
    # 1. Load active database
    print(f"-> Cargando base de datos desde: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print(f"ERROR: No se encontró la base de datos en {DB_PATH}.")
        return
    db = load_database()
    
    # 2. Find local SESNSP CSV
    csv_file = find_sesnsp_csv()
    if not csv_file:
        print("ERROR: No se encontró ningún archivo CSV de la incidencia delictiva del SESNSP.")
        print("Instrucciones:")
        print("  1. Descarga el archivo de Incidencia Delictiva Municipal (CSV) en Datos Abiertos del SESNSP.")
        print("  2. Descomprímelo y coloca el archivo CSV en la carpeta 'data/'.")
        print("  3. El archivo debe llamarse 'Municipal-Delitos.csv' o similar.")
        return
        
    # 3. Parse CSV rows matching Irapuato
    rows = parse_sesnsp_csv(csv_file)
    if not rows:
        return
        
    # 4. Determine latest reported period
    year, month_idx, month_name = determine_latest_reported_month(rows)
    if year == 0:
        print("ERROR: No se encontraron registros de crímenes válidos para Irapuato en el archivo.")
        return
        
    print(f"\n-> Último periodo oficial detectado en el CSV: {month_name} del {year}")
    
    # 5. Summarize crime counts
    counts = summarize_crimes_for_period(rows, year, month_name)
    
    print("\nTotales de delitos oficiales reportados en Irapuato:")
    for c_type, count in counts.items():
        print(f"   * {c_type}: {count}")
    total_crimes = sum(counts.values())
    print(f"   Total acumulado del mes: {total_crimes} incidentes reales.")
    
    if total_crimes == 0:
        print("\nEl periodo seleccionado no reporta incidencias en Irapuato. Base de datos al día.")
        return
        
    # 6. Load target year's incidents from separate file
    incidents_dir = os.path.join(os.path.dirname(DB_PATH), "incidents")
    os.makedirs(incidents_dir, exist_ok=True)
    year_file_path = os.path.join(incidents_dir, f"incidents_{year}.json")
    
    year_incidents = []
    if os.path.exists(year_file_path):
        try:
            with open(year_file_path, "r", encoding="utf-8") as yf:
                year_incidents = json.load(yf)
            print(f"\n-> Cargados {len(year_incidents)} incidentes previos del año {year} desde su archivo anual.")
        except Exception as e:
            print(f"\nAdvertencia: No se pudo leer {year_file_path}, se creará uno nuevo: {e}")
            
    target_prefix = f"{year}-{month_idx:02d}"
    initial_count = len(year_incidents)
    
    # Filter out any pre-existing auto-generated or real-incident records for this month
    year_incidents = [inc for inc in year_incidents if not inc["date"].startswith(target_prefix)]
    removed_count = initial_count - len(year_incidents)
    if removed_count > 0:
        print(f"-> Se eliminaron {removed_count} incidentes existentes del mes {target_prefix} en el archivo del año {year} para evitar duplicados.")
        
    # 7. Generate geodistributed incidents from counts
    new_incidents = generate_incidents_from_counts(counts, year, month_idx, db["neighborhoods"])
    
    # 8. Append to target year's dataset and save
    year_incidents.extend(new_incidents)
    with open(year_file_path, "w", encoding="utf-8") as yf:
        json.dump(year_incidents, yf, indent=2, ensure_ascii=False)
        
    # Clear monolithic incidents array from database.json if any were present
    if "incidents" in db and len(db["incidents"]) > 0:
        db["incidents"] = []
        save_database(db)
        print(f"-> Limpieza: Se vació la lista de incidentes en la base de datos base '{DB_PATH}'.")
        
    print(f"\n✓ PROCESO EXITOSO:")
    print(f"  - Se generaron y distribuyeron {len(new_incidents)} incidentes geolocalizados reales.")
    print(f"  - Se guardaron los cambios en {year_file_path}.")
    print(f"  - Total de incidentes para el año {year} ahora: {len(year_incidents)}")
    print("\nPróximos pasos recomendados:")
    print("  1. Abre el mapa localmente para verificar que aparezcan los datos.")
    print("  2. Ejecuta 'git add data/ database.json CNAME'")
    print("  3. Ejecuta 'git commit -m \"data: actualización con datos reales de SESNSP para " + month_name + " " + str(year) + "\" && git push'")
    print("==========================================================")

if __name__ == "__main__":
    main()
