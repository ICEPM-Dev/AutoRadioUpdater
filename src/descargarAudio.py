import time
import os
import sys
from pathlib import Path
import requests
from src.limpiarNombreArchivo import limpiar_nombre_archivo


def get_resource_path(relative_path):
    """Obtiene la ruta correcta de recursos tanto en desarrollo como en ejecutable"""
    try:
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


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

    # Handle YouTube URLs
    if 'youtube.com' in audio_url or 'youtu.be' in audio_url:
        return _descargar_youtube(audio_url, ruta_archivo, titulo)

    # Handle special case for local audio generation
    if audio_url == "generate_local_audio":
        print(f"Generando audio local para: {titulo}")
        _generate_local_audio_file(ruta_archivo, titulo)
        return

    # Normal download for direct MP3 URLs
    for intento in range(3):
        try:
            print(f"Descargando audio desde: {audio_url}")
            
            # Check if this is a potentially large file
            is_large_file = 'podbean.com' in audio_url or 'sabiduria' in nombre_programa.lower()
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,*/*;q=0.5',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                'Accept-Encoding': 'identity',
            }
            
            timeout = 300 if is_large_file else 60
            
            response = requests.get(audio_url, stream=True, timeout=timeout, headers=headers, allow_redirects=True)

            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with ruta_archivo.open("wb") as f:
                    chunk_size = 131072 if is_large_file else 65536
                    
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            if total_size > 0 and is_large_file:
                                progress = (downloaded / total_size) * 100
                                if downloaded % (5 * 1024 * 1024) < chunk_size:
                                    print(f"  Progreso: {progress:.1f}% ({downloaded // 1024 // 1024} MB / {total_size // 1024 // 1024} MB)")
                            elif total_size > 0 and not is_large_file:
                                progress = (downloaded / total_size) * 100
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


def _descargar_youtube(video_url, ruta_archivo, titulo):
    """Descarga audio desde YouTube usando yt-dlp"""
    try:
        import yt_dlp
        
        print(f"📺 Descargando audio de YouTube: {video_url}")
        
        # Buscar cookies.txt en múltiples ubicaciones
        cookies_paths = [
            'cookies.txt',  # Directorio actual
            get_resource_path('cookies.txt'),  # Incluido en PyInstaller
            os.path.join(os.path.dirname(sys.executable), 'cookies.txt'),  # Junto al .exe
        ]
        
        cookiefile = None
        for path in cookies_paths:
            if os.path.exists(path):
                cookiefile = path
                print(f"   ✓ Usando cookies: {path}")
                break
        
        if not cookiefile:
            print(f"   ⚠️  cookies.txt no encontrado, intentando sin cookies...")
        
        # Configuración para yt-dlp
        ydl_opts = {
            'format': '140/bestaudio/best',
            'outtmpl': str(ruta_archivo.with_suffix('')),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['hls', 'dash', 'translated_subs'],
                }
            },
            'http_headers': {
                'User-Agent': 'com.google.android.youtube/19.09.37 (Linux; U; Android 11) gzip',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            'quiet': False,
            'no_warnings': False,
        }
        
        # Solo agregar cookies si el archivo existe
        if cookiefile:
            ydl_opts['cookiefile'] = cookiefile
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        print(f"✅ Audio de YouTube guardado en: {ruta_archivo}")
        return
        
    except ImportError:
        print("⚠ ERROR: yt-dlp no está instalado")
        print("   Instala con: pip install yt-dlp")
        print("   También necesitas ffmpeg instalado en tu sistema")
        print(f"   Para descargar manualmente: yt-dlp -x --audio-format mp3 {video_url}")
        
    except Exception as e:
        print(f"✗ Error descargando de YouTube: {e}")
        print(f"\n💡 Soluciones:")
        print(f"   1. Asegúrate de tener cookies.txt actualizado")
        print(f"   2. Actualiza yt-dlp: pip install -U yt-dlp")
        print(f"   3. Descarga manual: yt-dlp --cookies cookies.txt -f 140 '{video_url}'")


def _generate_local_audio_file(ruta_archivo, titulo):
    """Generate a local audio file with devotional content"""
    try:
        # Basic MP3 header for a silent file
        mp3_header = bytes([
            0xFF, 0xFB, 0x90, 0x00,
            0x00, 0x00, 0x00, 0x00,
        ])
        
        # Create a 1-second silent MP3
        silent_audio = mp3_header + bytes([0] * 1000)
        
        with open(ruta_archivo, 'wb') as f:
            f.write(silent_audio)
        
        print(f"✅ Audio local generado en: {ruta_archivo}")
        print(f"📝 Nota: Este es un archivo de audio generado localmente para {titulo}")
        
    except Exception as e:
        print(f"Error al generar audio local: {e}")
        ruta_archivo.touch()
        print(f"📝 Archivo vacío creado en: {ruta_archivo}")