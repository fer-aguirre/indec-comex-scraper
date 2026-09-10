import argparse
import os
import pandas as pd
from datetime import datetime
from indec_comex.core import automate_indec_comex, search_ncm_codes

def main():
    parser = argparse.ArgumentParser(description="Descarga y explora datos comerciales del INDEC de Argentina.")
    
    parser.add_argument('-s', '--search', type=str, 
                        help='Busca descripciones de códigos NCM a partir de un prefijo (Ej: 1201). No descarga datos.')
    
    parser.add_argument('-c', '--codes', nargs='+', 
                        help='Lista de códigos NCM a 8 dígitos (Ej: 12011000). Requerido para descargas.')
    
    parser.add_argument('-y', '--years', nargs='+', type=int, required=True, 
                        help='Años a consultar separados por espacios (Ej: 2025 2026). Requerido siempre.')
    
    parser.add_argument('-t', '--type', default='import', choices=['import', 'export'], 
                        help='Tipo de comercio: import o export (Por defecto: import)')
                        
    parser.add_argument('-p', '--period', default='yearly', choices=['month', 'yearly'],
                        help="Granularidad temporal: 'yearly' para totales anuales (por defecto), 'month' para datos mensuales.")
                        
    parser.add_argument('-o', '--outdir', default='.', 
                        help='Directorio donde se guardará el archivo (Opcional. Por defecto: directorio actual)')

    args = parser.parse_args()

    pd.set_option('display.max_colwidth', 75)
    pd.set_option('display.expand_frame_repr', False)

    # --- MODO BÚSQUEDA ---
    if args.search:
        df_search = search_ncm_codes(term=args.search, year=args.years[0])
        if df_search is not None and not df_search.empty:
            print("\n" + df_search.to_markdown(tablefmt="psql", index=False))
        return

    # --- MODO DESCARGA ---
    if not args.codes:
        parser.error("El argumento -c/--codes es obligatorio para descargar datos. Úsalo, o incluye -s/--search para explorar el catálogo de códigos.")

    # 1. Definir el nombre del periodo para el archivo
    periodo_nombre = "anual" if args.period == 'yearly' else "mensual"
    
    codigos_unidos = "-".join(args.codes)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    # 2. Agregar el periodo al nombre del archivo
    nombre_archivo = f"indec_{periodo_nombre}_{codigos_unidos}_{timestamp}.csv"
    
    os.makedirs(args.outdir, exist_ok=True)
    nombre_archivo_dinamico = os.path.join(args.outdir, nombre_archivo)

    df = automate_indec_comex(
        hs_codes=args.codes, 
        years=args.years, 
        commerce_type=args.type, 
        output_filename=nombre_archivo_dinamico,
        period=args.period
    )

    if df is not None and not df.empty:
        print("\nVista previa de los primeros 5 registros:")
        print(df.head(5).to_markdown(tablefmt="psql"))
        print("\n")

if __name__ == '__main__':
    main()
