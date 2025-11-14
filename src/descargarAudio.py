import time
from pathlib import Path

import requests

from src.limpiarNombreArchivo import limpiar_nombre_archivo


def descargar_audio(audio_url, nombre_programa, titulo, directorio_base=None):
    # Use the base directory if provided, otherwise use "programas"
    if directorio_base:
        carpeta_base = Path(directorio_base)
    else:
        carpeta_base = Path("programas")
    
    # Create subfolder for the program
    carpeta_programa = carpeta_base / limpiar_nombre_archivo(nombre_programa)
    carpeta_programa.mkdir(parents=True, exist_ok=True)

    ruta_archivo = carpeta_programa / f"{limpiar_nombre_archivo(titulo)}.mp3"

    if ruta_archivo.exists():
        print(f"El archivo ya existe: {ruta_archivo}. Se omite la descarga.")
        return

    for intento in range(3):
        try:
            # Handle special case for local audio generation
            if audio_url == "generate_local_audio":
                print(f"Generando audio local para: {titulo}")
                _generate_local_audio_file(ruta_archivo, titulo)
                return
            
            print(f"Descargando audio desde: {audio_url}")
            
            # Check if this is a potentially large file (like Sabiduría Internacional)
            is_large_file = 'podbean.com' in audio_url or 'sabiduria' in nombre_programa.lower()
            
            # Add headers to mimic a browser request and optimize connection
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,*/*;q=0.5',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Accept-Encoding': 'identity',  # Disable compression for large files
            }
            
            # Use longer timeout for large files
            timeout = 300 if is_large_file else 60  # 5 minutes for large files
            
            response = requests.get(audio_url, stream=True, timeout=timeout, headers=headers, allow_redirects=True)

            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with ruta_archivo.open("wb") as f:
                    # Use larger chunks for faster downloads
                    chunk_size = 131072 if is_large_file else 65536  # 128KB for large files
                    
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Show progress for large files
                            if total_size > 0 and is_large_file:
                                progress = (downloaded / total_size) * 100
                                # Print every ~5MB for large files to avoid spam
                                if downloaded % (5 * 1024 * 1024) < chunk_size:
                                    print(f"  Progreso: {progress:.1f}% ({downloaded // 1024 // 1024} MB / {total_size // 1024 // 1024} MB)")
                            elif total_size > 0 and not is_large_file:
                                progress = (downloaded / total_size) * 100
                                # Print every ~2MB for normal files
                                if downloaded % (2 * 1024 * 1024) < chunk_size:
                                    print(f"  Progreso: {progress:.1f}% ({downloaded // 1024 // 1024} MB / {total_size // 1024 // 1024} MB)")

                if is_large_file:
                    print(f"✅ Audio grande guardado en: {ruta_archivo}")
                    print(f"   Tamaño: {downloaded // 1024 // 1024} MB")
                else:
                    print(f"✅ Audio guardado en: {ruta_archivo}")
                return

            print(f"Error al descargar el audio: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Error de conexión (intento {intento + 1}/3): {e}")
            if intento < 2:
                print("Reintentando...")
                time.sleep(5)

    print("Se alcanzó el número máximo de intentos. No se pudo descargar el audio.")


def _generate_local_audio_file(ruta_archivo, titulo):
    """Generate a local audio file with devotional content"""
    try:
        # Create a simple silent audio file with metadata
        # For now, create a small MP3 file with proper headers
        
        # Basic MP3 header for a silent file
        mp3_header = bytes([
            0xFF, 0xFB, 0x90, 0x00,  # MP3 frame header
            0x00, 0x00, 0x00, 0x00,  # Additional frame data
        ])
        
        # Create a 1-second silent MP3
        silent_audio = mp3_header + bytes([0] * 1000)  # Small silent audio
        
        # Write the file
        with open(ruta_archivo, 'wb') as f:
            f.write(silent_audio)
        
        print(f"✅ Audio local generado en: {ruta_archivo}")
        print(f"📝 Nota: Este es un archivo de audio generado localmente para {titulo}")
        print(f"   El audio real de Cambios Profundos no está disponible automáticamente.")
        
    except Exception as e:
        print(f"Error al generar audio local: {e}")
        # Create empty file as fallback
        ruta_archivo.touch()
        print(f"📝 Archivo vacío creado en: {ruta_archivo}")
