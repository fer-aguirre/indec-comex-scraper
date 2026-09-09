import argparse
import os
from datetime import datetime
from .core import automate_indec_comex

def main():
    parser = argparse.ArgumentParser(description="Descarga datos comerciales del INDEC de Argentina.")
    
    parser.add_argument('-c', '--codes', nargs='+', required=True, 
                        help='Lista de códigos NCM a 8 dígitos separados por espacios (Ej: 38249989 38249941)')
    
    parser.add_argument('-y', '--years', nargs='+', type=int, required=True, 
                        help='Años a consultar separados por espacios (Ej: 2025 2026)')
    
    parser.add_argument('-t', '--type', default='import', choices=['import', 'export'], 
                        help='Tipo de comercio: import o export (Por defecto: import)')
                        
    # NEW OPTIONAL ARGUMENT
    parser.add_argument('-o', '--outdir', default='.', 
                        help='Directorio donde se guardará el archivo (opcional. Por defecto: directorio actual)')

    args = parser.parse_args()

    # 1. Format the file name dynamically
    codigos_unidos = "-".join(args.codes)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    nombre_archivo = f"indec_{codigos_unidos}_{timestamp}.csv"
    
    # 2. Ensure the target directory exists (creates 'outputs/' if it doesn't)
    os.makedirs(args.outdir, exist_ok=True)
    
    # 3. Safely join the directory and the filename (e.g., outputs/indec_...csv)
    nombre_archivo_dinamico = os.path.join(args.outdir, nombre_archivo)

    # 4. Execute the main function
    automate_indec_comex(
        hs_codes=args.codes, 
        years=args.years, 
        commerce_type=args.type, 
        output_filename=nombre_archivo_dinamico
    )
    print(f"\nPreparando exportación hacia: {nombre_archivo_dinamico}")

if __name__ == '__main__':
    main()