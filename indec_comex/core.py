from datetime import datetime
import pandas as pd
import requests
import json
import time

# (Mantén tus funciones anteriores: fetch_with_retries, fetch_comex_data y automate_indec_comex)

def search_ncm_codes(term, year):
    """
    Consulta la API de productos y devuelve un DataFrame con los códigos NCM 
    que coinciden con el término de búsqueda y su descripción.
    """
    url = f"https://comexbe.indec.gob.ar/public-api/search/products?i18n=es&term={term}&year={year}"
    
    print(f"Consultando sub-partidas NCM para el prefijo '{term}' en {year}...")
    data = fetch_with_retries(url)
    
    if not data:
        print("No se encontraron resultados.")
        return None
        
    results = []
    for item in data:
        ncm = item.get('id')
        desc = item.get('description', {}).get('es', 'Sin descripción')
        
        # Filtrar para asegurarse de que empiezan con el término de búsqueda
        if str(ncm).startswith(str(term)):
            results.append({'NCM': str(ncm), 'Descripción': desc})
            
    df = pd.DataFrame(results)
    
    if not df.empty:
        # Alerta amigable si llegamos al tope (truncamiento de la API)
        if len(df) >= 30:
            print(f"  [!] Atención: La API devolvió {len(df)} resultados. La lista podría estar cortada.")
            print(f"      Si no encuentras el código de 8 dígitos, prueba buscando con un dígito más (ej. de '{term}' a '{term}0').")
            
    return df

def fetch_with_retries(url, max_retries=3, timeout=15):
    """
    Realiza una petición HTTP de forma segura. Si el servidor está sobrecargado (503), 
    limita la tasa de peticiones (429) o se agota el tiempo de espera, 
    espera unos segundos y reintenta en lugar de interrumpir el programa.
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            
            if response.status_code == 429:
                print(f"    [!] Límite de peticiones alcanzado (429). Esperando 10 segundos antes de reintentar...")
                time.sleep(10)
                continue
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"    [!] Intento {attempt + 1}/{max_retries} fallido: {e}")
            if attempt < max_retries - 1:
                time.sleep(5) 
            else:
                print(f"    [!] Se alcanzó el límite máximo de reintentos. Omitiendo esta petición.")
                return None

def fetch_comex_data(year, products, commerce_type="import"):
    """Construye la URL compleja y recupera el JSON con los datos comerciales."""
    products_json = json.dumps(products, separators=(',', ':')) 
    products_encoded = products_json.replace('"', '%22')
    
    url = f"https://comexbe.indec.gob.ar/public-api/search/?commerceType={commerce_type}&year={year}&period=month&countryQuery=allCountries&products={products_encoded}&countries=[]"
    
    return fetch_with_retries(url)

def automate_indec_comex(hs_codes, years, commerce_type="import", output_filename="comex_data.csv"):
    """
    Toma directamente una lista de códigos NCM a 8 dígitos y descarga su información.
    """
    all_data = []
    
    # Asegurarnos de que todos los códigos sean de tipo string (texto)
    hs_codes = [str(code) for code in hs_codes]
    
    print(f"Iniciando descarga directa para los códigos: {hs_codes}")
    
    for year in years:
        print(f"  -> Obteniendo datos para el año {year}...")
        
        # Saltamos la búsqueda general y pedimos directamente los datos
        year_data = fetch_comex_data(year, hs_codes, commerce_type)
        if not year_data:
            continue
        
        records = year_data if isinstance(year_data, list) else year_data.get('data', [])
        
        if not records:
             print(f"     [!] No hay registros comerciales registrados para el año {year}.")
             continue
        
        for record in records:
            record['Año'] = year 
            
        all_data.extend(records)
        time.sleep(1) 
        
    if all_data:
        df = pd.DataFrame(all_data)
        
        if 'country' in df.columns:
            df['ISO2'] = df['country'].apply(lambda x: x.get('iso2') if isinstance(x, dict) else None)
            df['country'] = df['country'].apply(lambda x: x.get('name') if isinstance(x, dict) else x)
            
        if 'product' in df.columns:
            df['NCM'] = df['product'].apply(lambda x: x.get('id') if isinstance(x, dict) else None)
            df['Descripción'] = df['product'].apply(
                lambda x: x.get('description', {}).get('es') if isinstance(x, dict) and isinstance(x.get('description'), dict) else None
            )

        column_mapping = {
            'country': 'País',
            'month': 'Mes',
            'weight': 'Peso Neto (KG)',  
            'amount': 'USD CIF' 
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        if 'Peso Neto (KG)' in df.columns:
            df['Peso Neto (KG)'] = pd.to_numeric(df['Peso Neto (KG)'], errors='coerce')
        if 'USD CIF' in df.columns:
            df['USD CIF'] = pd.to_numeric(df['USD CIF'], errors='coerce')
        
        desired_columns = ['NCM', 'Descripción', 'País', 'ISO2', 'Mes', 'Peso Neto (KG)', 'USD CIF', 'Año']
        existing_columns = [col for col in desired_columns if col in df.columns]
        df = df[existing_columns]
        
        df.to_csv(output_filename, index=False, encoding='utf-8-sig')
        print(f"\nSe compilaron {len(df)} registros y se exportaron a '{output_filename}'.")
        return df
    else:
        print("\nNo se recuperaron datos en ninguno de los años solicitados.")
        return None