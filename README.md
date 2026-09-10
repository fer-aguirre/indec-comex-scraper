# INDEC Comex Scraper 🇦🇷

Un paquete de Python y herramienta de línea de comandos (CLI) diseñado para descargar, limpiar y exportar datos de comercio exterior (importaciones y exportaciones) desde la API pública del INDEC de Argentina. 

Al especificar posiciones arancelarias (códigos NCM a 8 dígitos) y años fiscales, la herramienta extrae los volúmenes y valores (USD CIF / Peso Neto) desagregados por país y por periodo (anual o mensual), generando un archivo CSV listo para su análisis. Además, incluye un explorador integrado de nomenclatura arancelaria en el Mercosur que te ayuda a explorar los códigos de 8 dígitos y su descripción si solo conoces el código de 2, 4 o 6 dígitos.

> **Limitación importante de la API del INDEC:** El buscador de productos del INDEC corta automáticamente los resultados al alcanzar los 35 registros. Para sortear esta limitación y no perder códigos ocultos, es fundamental realizar búsquedas usando los códigos arancelarios más específicos posibles (entre más cerca de los 8 dígitos, mejor).

## Características
- **Búsqueda de NCM integrada:** ¿No conoces el código exacto para el Mercosur? Usa la función de búsqueda para explorar el catálogo oficial del INDEC a partir de prefijos cortos y obtener las descripciones exactas antes de descargar.
- **Ventajas sobre la web oficial:** Permite obtener en una sola descarga las operaciones con todos los países, eliminando la necesidad de buscar y descargar la información año por año manualmente.
- **Datos enriquecidos:** Recupera información exclusiva de la API que no se visualiza en las tablas del sitio web del INDEC, como la descripción oficial de cada partida NCM y el código ISO2 del país.
- **Flexibilidad temporal:** Elige entre descargar los totales anuales consolidados (por defecto) o los datos desagregados mes a mes.
- **Doble interfaz:** Úsalo directamente desde la terminal (CLI) o impórtalo en tus Jupyter Notebooks.
- **Exportación inteligente:** Genera archivos CSV ordenados y nombra los archivos dinámicamente con fechas de ejecución para mantener un historial limpio.

## Instalación

Asegúrate de tener Python instalado y preferiblemente un entorno virtual activado (se recomienda el uso de `uv`).

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu-usuario/indec-comex-scraper.git
   cd indec-comex-scraper
   ```

2. Instala el paquete en modo editable:
   ```bash
   uv pip install -e .
   ```
   *(Si usas el entorno de Python tradicional, reemplaza `uv pip` por `pip`).*

## Uso

Puedes utilizar esta herramienta de dos maneras según tus necesidades:

### Opción A: Línea de Comandos (CLI)
Ideal para descargas rápidas y automatización en la terminal. El comando `indec-descargar` estará disponible globalmente en tu entorno.

**1. Explorar códigos:**
Si solo tienes los primeros dígitos de un producto (ej. `9306`), usa el parámetro `-b` (buscar) para ver el catálogo y sus descripciones. *Esto no descarga datos comerciales, solo te ayuda a elegir el código correcto.*
```bash
indec-descargar -b 1201 -y 2026
```

**2. Descargar datos:**
Una vez que identificaste tus códigos de 8 dígitos, procede con la descarga. 
*(Nota: Por defecto, la descarga agrupa los totales anuales. Si necesitas el detalle mensual, usa `-p month`)*:
```bash
# Descarga de totales anuales (por defecto)
indec-descargar --codes 12011000 --years 2025 2026 --type import --outdir outputs

# Descarga de detalle mensual
indec-descargar --codes 12011000 --years 2025 2026 --type import --period month --outdir outputs
```

**Argumentos disponibles:**
* `-s, --search`: (Opcional) Busca descripciones de códigos NCM a partir de un prefijo.
* `-c, --codes`: (Requerido para descarga) Códigos arancelarios NCM a 8 dígitos separados por espacios.
* `-y, --years`: (Requerido) Años fiscales a consultar.
* `-t, --type`: (Opcional) `import` o `export`. (Por defecto: `import`).
* `-p, --period`: (Opcional) Granularidad temporal de los datos. Opciones: `yearly` (totales anuales, por defecto) o `month` (mensual).
* `-o, --outdir`: (Opcional) Carpeta de destino. (Por defecto: directorio actual).

### Opción B: Jupyter Notebooks / Python Scripts
Ideal para integrar la exploración y la descarga directamente en tus flujos de análisis de datos.

**1. Explorar códigos:**
```python
import pandas as pd
from indec_comex.core import search_ncm_codes

# Buscar NCMs que empiecen con "1201" para el año 2026
df_codigos = search_ncm_codes("1201", 2026)

# Esto anula temporalmente los límites de visualización de Pandas
with pd.option_context(
    "display.max_rows", None,  
    "display.max_columns", None,  
    "display.max_colwidth", None,  
):
    display(df_codigos)
```

**2. Ejecutar descarga:**
```python
import os
from datetime import datetime
from indec_comex.core import automate_indec_comex

# Usamos el código de 8 dígitos encontrado en el paso anterior
codigos = ["12011000"]
timestamp = datetime.now().strftime("%Y-%m-%d")

# Preparar directorio y nombre de archivo
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)
filepath = os.path.join(output_dir, f"indec_{'-'.join(codigos)}_{timestamp}.csv")

# Ejecutar descarga (period="yearly" consolida totales; usa period="month" para desglosar por mes)
df = automate_indec_comex(
    hs_codes=codigos,
    years=[2026],
    commerce_type="import",
    period="yearly", 
    output_filename=filepath
)

# Previsualizar datos
if df is not None:
    display(df)
```

## Estructura de salida (Outputs)
Los archivos se guardarán por defecto en el directorio asignado (ej. `outputs/`) con una nomenclatura estándar que facilita identificar de qué trata cada archivo sin abrirlo:

`indec_[anual/mensual]_[codigos-consultados]_[fecha-de-descarga].csv`
