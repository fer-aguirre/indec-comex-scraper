import argparse
import os
import pandas as pd
from datetime import datetime
from .core import automate_indec_comex, search_ncm_codes

def main():
    parser = argparse.ArgumentParser(description="Descarga y explora datos comerciales del INDEC de Argentina.")
    
    # NUEVO ARGUMENTO: Búsqueda
    parser.add_argument('-b', '--buscar', type=str, 
                        help='Busca descripciones de códigos NCM a partir de un prefijo (Ej: 93). No descarga datos.')
    
    # El argumento -c ya no es required=True por defecto, lo validaremos manualmente
    parser.add_argument('-c', '--codes', nargs='+', 
                        help='Lista de códigos NCM a 8 dígitos (Ej: 38249989). Requerido para descargas.')
    
    parser.add_argument('-y', '--years', nargs='+', type=int, required=True, 
                        help='Años a consultar separados por espacios (Ej: 2025 2026). Requerido siempre.')
    
    parser.add_argument('-t', '--type', default='import', choices=['import', 'export'], 
                        help='Tipo de comercio: import o export (Por defecto: import)')
                        
    parser.add_argument('-o', '--outdir', default='.', 
                        help='Directorio donde se guardará el archivo (opcional. Por defecto: directorio actual)')

    args = parser.parse_args()

    # Configuración de Pandas para que las tablas en la terminal se vean bien
    pd.set_option('display.max_colwidth', 75)
    pd.set_option('display.expand_frame_repr', False)

    # =========================================================
    # MODO 1: BÚSQUEDA (El usuario usó la bandera -b)
    # =========================================================
    if args.buscar:
        # Usamos el primer año proporcionado para la búsqueda
        df_search = search_ncm_codes(term=args.buscar, year=args.years[0])
        
        if df_search is not None and not df_search.empty:
            print("\n" + df_search.to_markdown(tablefmt="psql", index=False))
        return  # Terminamos el programa aquí sin descargar nada

    # =========================================================
    # MODO 2: DESCARGA (Validamos que existan códigos)
    # =========================================================
    if not args.codes:
        parser.error("El argumento -c/--codes es obligatorio para descargar datos. Úsalo o incluye -b/--buscar para ver el catálogo de códigos.")

    codigos_unidos = "-".join(args.codes)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    nombre_archivo = f"indec_{codigos_unidos}_{timestamp}.csv"
    
    os.makedirs(args.outdir, exist_ok=True)
    nombre_archivo_dinamico = os.path.join(args.outdir, nombre_archivo)

    print(f"\nPreparando exportación hacia: {nombre_archivo_dinamico}")
    print("-" * 50)

    df = automate_indec_comex(
        hs_codes=args.codes, 
        years=args.years, 
        commerce_type=args.type, 
        output_filename=nombre_archivo_dinamico
    )

    if df is not None and not df.empty:
        print("\nVista previa de los primeros 5 registros:")
        print(df.head(5).to_markdown(tablefmt="psql"))
        print("\n")

if __name__ == '__main__':
    main()