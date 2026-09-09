# INDEC Comex Scraper 🇦🇷

Un paquete de Python y herramienta de línea de comandos (CLI) diseñado para descargar, limpiar y exportar datos de comercio exterior (importaciones y exportaciones) desde la API pública del INDEC de Argentina. 

Al especificar posiciones arancelarias (códigos NCM a 8 dígitos) y años fiscales, la herramienta extrae los volúmenes y valores (USD CIF / Peso Neto) desagregados por país y por periodo mensual, generando un archivo CSV listo para su análisis.

## Características
- **Ventajas sobre la web oficial:** Permite obtener en una sola descarga las operaciones con todos los países, eliminando la necesidad de buscar y descargar la información año por año manualmente.
- **Datos enriquecidos:** Recupera información exclusiva de la API que no se visualiza en las tablas del sitio web del INDEC, como la descripción oficial de cada partida NCM y el código ISO2 del país.
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

```bash
indec-descargar --codes 38249989 38249941 --years 2025 2026 --type import --outdir outputs
```

**Argumentos disponibles:**
* `-c, --codes`: (Requerido) Códigos arancelarios NCM a 8 dígitos separados por espacios.
* `-y, --years`: (Requerido) Años fiscales a consultar.
* `-t, --type`: (Opcional) `import` o `export`. (Por defecto: `import`).
* `-o, --outdir`: (Opcional) Carpeta de destino. (Por defecto: directorio actual).

### Opción B: Jupyter Notebooks / Python Scripts
Ideal para integrar la descarga directamente en tus flujos de análisis de datos.

```python
import os
from datetime import datetime
from indec_comex.core import automate_indec_comex

codigos = ["03048100"]
timestamp = datetime.now().strftime("%Y-%m-%d")

# Preparar directorio y nombre de archivo
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)
filepath = os.path.join(output_dir, f"indec_{'-'.join(codigos)}_{timestamp}.csv")

# Ejecutar descarga
df = automate_indec_comex(
    hs_codes=codigos,
    years=[2026],
    commerce_type="import",
    output_filename=filepath
)

# Previsualizar datos
df.head(5)
```

## Estructura de salida (Outputs)
Los archivos se guardarán por defecto en el directorio asignado (ej. `outputs/`) con una nomenclatura estándar que facilita identificar de qué trata cada archivo sin abrirlo:

`indec_[codigos-consultados]_[fecha-de-descarga].csv`
