import time
from pathlib import Path

import requests

from src.limpiarNombreArchivo import limpiar_nombre_archivo


def descargar_audio(audio_url, nombre_programa, titulo):
    carpeta_programa = Path("programas") / nombre_programa
    carpeta_programa.mkdir(parents=True, exist_ok=True)

    ruta_archivo = carpeta_programa / f"{limpiar_nombre_archivo(titulo)}.mp3"

    if ruta_archivo.exists():
        print(f"El archivo ya existe: {ruta_archivo}. Se omite la descarga.")
        return

    for intento in range(3):
        try:
            print(f"Descargando audio desde: {audio_url}")
            response = requests.get(audio_url, stream=True, timeout=30)

            if response.status_code == 200:
                with ruta_archivo.open("wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)

                print(f"Audio guardado en: {ruta_archivo}")
                return

            print(f"Error al descargar el audio: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}. Reintentando...")
            time.sleep(5)

    print("Se alcanzó el número máximo de intentos. No se pudo descargar el audio.")
