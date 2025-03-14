import re

import requests
from bs4 import BeautifulSoup

from src.descargarAudio import descargar_audio


def obtener_y_descargar_audio(programa):
    response = requests.get(programa["escuchar_link"], timeout=30)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')

        audio_url = None
        for script in scripts:
            if script.string and 'sources: [' in script.string:
                match = re.search(r"src:\s*'(https?://[^']+\.mp3\?site=[^']+)'", script.string)
                if match:
                    audio_url = match.group(1)
                    break

        if audio_url:
            nombre_programa = programa["nombre_programa"]
            titulo_programa = programa["titulo"]
            descargar_audio(audio_url, nombre_programa, titulo_programa)
        else:
            print(f"No se encontró enlace de audio para {programa['titulo']}")
    else:
        print(f"Error al acceder a la página de escuchar: {response.status_code}")
