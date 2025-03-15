import re

import requests
from bs4 import BeautifulSoup

from src.descargarAudio import descargar_audio


def obtener_y_descargar_audio(programa):
    try:
        response = requests.get(programa["escuchar_link"], timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error al acceder a la página de escuchar ({programa['titulo']}): {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    for script in soup.find_all("script"):
        if script.string:
            match = re.search(r"src:\s*'(https?://[^']+\.mp3\?site=[^']+)'", script.string)
            if match:
                audio_url = match.group(1)
                descargar_audio(audio_url, programa["nombre_programa"], programa["titulo"])
                return

    print(f"No se encontró enlace de audio para {programa['titulo']}")
