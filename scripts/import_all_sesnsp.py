#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SESNSP Full History Import Utility
Imports all mapped crimes for Irapuato from 2015 to 2025 into database.json.
"""

import os
import glob
import csv
import json
import random
from datetime import datetime

# Path configurations
DB_PATH = "data/database.json"
CSV_PATH = "data/IDM_NM_dic25.csv"

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

def select_neighborhood_by_weight(neighborhoods):
    total_risk = sum(n["baseRisk"] for n in neighborhoods)
    r = random.uniform(0, total_risk)
    upto = 0
    for n in neighborhoods:
        if upto + n["baseRisk"] >= r:
            return n
        upto += n["baseRisk"]
    return neighborhoods[-1]

def main():
    print("==========================================================")
    print("    IMPORTADOR DE HISTORIAL COMPLETO (2015-2025) SESNSP   ")
    print("==========================================================\n")
    
    if not os.path.exists(CSV_PATH):
        print(f"ERROR: No se encontró el archivo CSV en {CSV_PATH}.")
        return
        
    db = load_database()
    
    # Try different encodings
    encodings = ["utf-8", "latin-1", "iso-8859-15", "cp1252"]
    rows = []
    
    for encoding in encodings:
        try:
            with open(CSV_PATH, mode="r", encoding=encoding) as f:
                sample = f.read(2048)
                separator = ";" if ";" in sample else ","
                f.seek(0)
                
                reader = csv.DictReader(f, delimiter=separator)
                reader.fieldnames = [name.strip().replace('\ufeff', '') for name in reader.fieldnames]
                
                for row in reader:
                    cleaned_row = {k.strip() if k else "": v.strip() if v else "" for k, v in row.items()}
                    cve_ent = cleaned_row.get("Clave_Ent", "").replace(".0", "")
                    cve_mun = cleaned_row.get("Cve. Municipio", "").replace(".0", "")
                    if not cve_mun:
                        cve_mun = cleaned_row.get("Clave_Mun", "").replace(".0", "")
                    if not cve_mun:
                        cve_mun = cleaned_row.get("Cve_Municipio", "").replace(".0", "")
                    mun_name = cleaned_row.get("Municipio", "").lower()
                    
                    is_irapuato = False
                    if cve_ent == "11" and (cve_mun == "17" or cve_mun == "017"):
                        is_irapuato = True
                    elif mun_name == "irapuato":
                        is_irapuato = True
                        
                    if is_irapuato:
                        rows.append(cleaned_row)
            if rows:
                print(f"-> Leídas {len(rows)} filas de Irapuato con codificación '{encoding}'.")
                break
        except Exception as e:
            continue
            
    if not rows:
        print("ERROR: No se pudieron leer las filas de Irapuato.")
        return
        
    # Group counts by Year, Month, and Crime Category
    # structure: counts[year][month_idx][crime_type] = count
    counts = {}
    
    print("-> Consolidando totales por año y mes...")
    for row in rows:
        try:
            year = int(row.get("Año", 0))
        except ValueError:
            continue
            
        # Limit to 2015-2025 range
        if not (2015 <= year <= 2025):
            continue
            
        if year not in counts:
            counts[year] = {}
            
        tipo = row.get("Tipo de delito", "").strip()
        subtipo = row.get("Subtipo de delito", "").strip()
        
        # Classification mapping
        crime_type = None
        if tipo == "Homicidio" and subtipo == "Homicidio doloso":
            crime_type = "Homicidio"
        elif tipo == "Robo" and subtipo == "Robo a transeúnte en vía pública":
            crime_type = "Robo a Transeúnte"
        elif tipo == "Robo" and subtipo in ["Robo de coche de 4 ruedas", "Robo de motocicleta"]:
            crime_type = "Robo de Vehículo"
        elif tipo == "Lesiones" and subtipo == "Lesiones dolosas":
            crime_type = "Asalto/Lesiones"
        elif tipo in ["Feminicidio", "Secuestro"]:
            crime_type = "Asalto/Lesiones"
        elif tipo in ["Extorsión", "Fraude"]:
            crime_type = "Extorsión/Fraude"
        elif tipo == "Daño a la propiedad":
            crime_type = "Vandalismo"
            
        if not crime_type:
            continue
            
        for m_name, m_idx in MONTHS_MAPPING:
            if m_idx not in counts[year]:
                counts[year][m_idx] = {c: 0 for c in DETAILS_TEMPLATES.keys()}
                
            val_str = row.get(m_name, "0").replace(",", "")
            try:
                val = int(float(val_str)) if val_str else 0
            except ValueError:
                val = 0
                
            if val > 0:
                counts[year][m_idx][crime_type] += val
                
    # Reset incidents array
    db["incidents"] = []
    
    print("-> Generando registros geolocalizados dispersos...")
    random.seed(42)  # For reproducibility
    generated_count = 0
    
    for year in sorted(counts.keys()):
        year_total = 0
        for m_idx in sorted(counts[year].keys()):
            for crime_type, count in counts[year][m_idx].items():
                if count <= 0:
                    continue
                    
                severity = "Alta" if crime_type in ["Homicidio", "Asalto/Lesiones"] else ("Media" if crime_type in ["Robo a Transeúnte", "Robo de Vehículo"] else "Baja")
                
                for i in range(count):
                    colonia = select_neighborhood_by_weight(db["neighborhoods"])
                    
                    day = random.randint(1, 28)
                    hour = random.randint(0, 23)
                    minute = random.randint(0, 59)
                    
                    if hour >= 6 and hour < 12:
                        time_period = "Mañana"
                    elif hour >= 12 and hour < 19:
                        time_period = "Tarde"
                    else:
                        time_period = "Noche"
                        
                    offset_lat = (random.random() - 0.5) * 0.007
                    offset_lon = (random.random() - 0.5) * 0.007
                    
                    date_str = f"{year}-{m_idx:02d}-{day:02d}T{hour:02d}:{minute:02d}:00"
                    timestamp = int(datetime(year, m_idx, day, hour, minute).timestamp())
                    
                    desc = random.choice(DETAILS_TEMPLATES[crime_type])
                    
                    db["incidents"].append({
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
                    
                    generated_count += 1
                    year_total += 1
        print(f"   * Año {year}: generados {year_total} incidentes.")
        
    print(f"\n-> Total de incidentes generados e importados: {generated_count}")
    
    # Save the database
    save_database(db)
    print(f"✓ Base de datos guardada con éxito en {DB_PATH}.")
    print("==========================================================")

if __name__ == "__main__":
    main()
