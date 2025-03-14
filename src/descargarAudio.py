import os
import time

import requests

from src.limpiarNombreArchivo import limpiar_nombre_archivo


def descargar_audio(audio_url, nombre_programa, titulo):
    carpeta_programa = os.path.join('programas', nombre_programa)
    os.makedirs(carpeta_programa, exist_ok=True)

    titulo_limpio = limpiar_nombre_archivo(titulo)

    ruta_archivo = os.path.join(carpeta_programa, f"{titulo_limpio}.mp3")

    intentos = 0
    max_intentos = 3
    while intentos < max_intentos:
        try:
            print(f"Descargando audio desde: {audio_url}")
            response = requests.get(audio_url, stream=True, timeout=30)
            if response.status_code == 200:
                with open(ruta_archivo, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"Audio guardado en: {ruta_archivo}")
                break
            else:
                print(f"Error al descargar el audio: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}. Reintentando...")
            intentos += 1
            if intentos >= max_intentos:
                print("Se alcanzó el número máximo de intentos. No se pudo descargar el audio.")
            time.sleep(5)
