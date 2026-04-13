import argparse
import os
import mlx_whisper
from tqdm import tqdm
from datetime import timedelta

def format_timestamp(seconds: float) -> str:
    """Convierte segundos a un formato de tiempo limpio como HH:MM:SS"""
    td = timedelta(seconds=seconds)
    # Formatear timedelta manejando decimales para presentación limpia
    time_str = str(td).split('.')[0]
    return f"[{time_str}]"


def main():
    parser = argparse.ArgumentParser(description='Transcripción de video/audio de larga duración optimizada para Mac M4')
    parser.add_argument('file_path', help='Ruta absoluta o relativa al archivo de video/audio a transcribir')
    parser.add_argument('--model', default='mlx-community/whisper-large-v3-mlx', help='Modelo MLX a usar (default: whisper-large-v3)')
    parser.add_argument('--language', default=None, help='Forzar un idioma de entrada (ej: "es" o "en"). Si no se provee, Whisper lo auto-detecta.')
    
    args = parser.parse_args()

    if not os.path.isfile(args.file_path):
        print(f"Error: El archivo especificado '{args.file_path}' no existe.")
        return

    print(f"Iniciando procesamiento de archivo: {args.file_path}")
    print(f"Cargando el modelo de mayor precisión optimizado para Apple Silicon: {args.model}")
    print("Nota: Si es la primera vez que se usa, descargará el modelo automáticamente...\n")

    transcribe_args = {
        "path_or_hf_repo": args.model
    }
    
    if args.language:
        transcribe_args["language"] = args.language
        
    print("Transcribiendo contenido. Por favor espera (videos largos pueden tomar algunos minutos)...")
    
    try:
        # mlx_whisper usa Ffmpeg nativamente para procesar el video y obtener el audio automáticamente
        result = mlx_whisper.transcribe(args.file_path, **transcribe_args)
    except Exception as e:
        print(f"\nOcurrió un error crítico durante la transcripción.")
        print(f"Por favor asegúrese de tener instalado FFmpeg en el sistema (puede usar 'brew install ffmpeg').\nDetalles del error: {e}")
        return

    # Extraer los segmentos de tiempo y texto
    segments = result.get('segments', [])
    if not segments:
        print("No se lograron extraer segmentos hablados. Asegúrese de que el video contenga una pista de audio válida.")
        return

    # Preparar el archivo de escritura (en la misma ruta desde donde se lanzó el comando)
    base_name = os.path.splitext(os.path.basename(args.file_path))[0]
    output_md = f"{base_name}_transcripcion.md"
    
    print(f"\nDocumentando resultados en: {output_md}")
    
    with open(output_md, "w", encoding="utf-8") as md_file:
        md_file.write(f"# Transcripción de Video\n\n")
        md_file.write(f"**Archivo de origen:** `{os.path.basename(args.file_path)}`\n")
        md_file.write(f"**Modelo Whisper usado:** `{args.model.split('/')[-1]}`\n\n")
        md_file.write("---\n\n")
        
        for segment in segments:
            # Recuperar start time y limpiar el fragmento de texto
            start_time = segment.get('start', 0.0)
            text = segment.get('text', '').strip()
            
            ts_start = format_timestamp(start_time)
            # Escribir en Markdown como viñetas o bloques
            md_file.write(f"**{ts_start}** {text}\n\n")

    print(f"\n✅ ¡Proceso finalizado con éxito!")
    print(f"El análisis temporizado está disponible en el archivo '{output_md}' en este mismo directorio.")

if __name__ == "__main__":
    main()
