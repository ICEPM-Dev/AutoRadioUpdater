import os

from dotenv import load_dotenv

from src.borrarArchivosViejos import borrar_archivos_viejos
from src.obtenerDescargarAudio import obtener_y_descargar_audio
from src.obtenerEnlacesProgramas import obtener_enlaces_programas


def main():
    load_dotenv()
    programas_urls = os.getenv("PROGRAMAS_URL").split(';')

    borrar_archivos_viejos(os.getenv("DIRECTORIO"))

    for url in programas_urls:
        programas = obtener_enlaces_programas(url)

        for programa in programas:
            obtener_y_descargar_audio(programa)


if __name__ == '__main__':
    main()
