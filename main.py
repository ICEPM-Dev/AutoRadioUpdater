import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from src.borrarArchivosViejos import borrar_archivos_viejos
from src.programa_manager import ProgramaManager
from src.config_manager import ConfigManager
from src.limpiarNombreArchivo import limpiar_nombre_archivo


def get_resource_path(relative_path):
    """Obtiene la ruta correcta de recursos tanto en desarrollo como en ejecutable"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def verificar_descargas(directorio, programas_config, programa_manager, config_manager):
    """Verifica descargas y reintenta episodios faltantes en carpetas vacías"""
    print(f"\n{'='*60}")
    print("Verificando descargas...")
    print(f"{'='*60}")

    base_dir = Path(directorio)
    if not base_dir.exists():
        print(f"El directorio {directorio} no existe.")
        return

    programas_con_archivos = 0
    programas_vacios = 0
    programas_faltantes = 0

    config_por_carpeta = {}
    for prog in programas_config:
        nombre_limpio = limpiar_nombre_archivo(prog["name"])
        config_por_carpeta[nombre_limpio] = prog

    for carpeta in base_dir.iterdir():
        if not carpeta.is_dir():
            continue

        archivos_mp3 = list(carpeta.glob("*.mp3"))
        if archivos_mp3:
            programas_con_archivos += 1
            nombre_original = config_por_carpeta.get(carpeta.name, {}).get("name", carpeta.name)
            print(f"{nombre_original}: {len(archivos_mp3)} archivo(s)")
        else:
            programas_vacios += 1
            prog_config = config_por_carpeta.get(carpeta.name)
            if prog_config:
                print(f"Carpeta vacía: {prog_config['name']} — reintentando descarga...")
                _reintentar_descarga(prog_config, programa_manager, config_manager)
            else:
                print(f"Carpeta vacía desconocida: {carpeta.name}")

    for nombre_limpio, prog_config in config_por_carpeta.items():
        carpeta = base_dir / nombre_limpio
        if not carpeta.exists():
            programas_faltantes += 1
            print(f"carpeta no encontrada: {prog_config['name']} — descargando...")
            _reintentar_descarga(prog_config, programa_manager, config_manager)

    total_esperados = len(programas_config)
    print(f"\nResumen: {programas_con_archivos}/{total_esperados} programas con descargas, "
          f"{programas_vacios} carpetas vacías reintentadas, {programas_faltantes} carpetas faltantes reintentadas")


def _reintentar_descarga(prog_config, programa_manager, config_manager):
    """Reintenta descargar episodios para un programa que quedó vacío o no existe"""
    url = prog_config["url"]
    name = prog_config["name"]
    max_episodes = prog_config.get('max_episodes', config_manager.get_max_episodes_per_program())

    if not programa_manager.is_supported(url):
        print(f"URL no soportada: {url}")
        return

    programas = programa_manager.obtener_enlaces_programas(url, program_name=name)
    if not programas:
        print(f"No se encontraron episodios nuevos para '{name}'")
        return

    programas = programas[:max_episodes]
    for programa in programas:
        programa_manager.obtener_y_descargar_audio(programa)


def main():
    load_dotenv()

    config_manager = ConfigManager()

    directorio = os.getenv("DIRECTORIO") or config_manager.get_download_directory()
    programa_manager = ProgramaManager(directorio_base=directorio)

    enabled_programs = config_manager.get_enabled_programs()

    if not enabled_programs:
        print("No hay programas habilitados en la configuración.")
        print("Usando URLs del archivo .env si están disponibles...")

        programas_urls_env = os.getenv("PROGRAMAS_URL")
        if programas_urls_env:
            programas_urls = programas_urls_env.split(';')
            for url in programas_urls:
                url = url.strip()
                if url and programa_manager.is_supported(url):
                    print(f"\nProcesando: {url}")
                    programas = programa_manager.obtener_enlaces_programas(url)

                    max_episodes = config_manager.get_max_episodes_per_program()
                    programas = programas[:max_episodes]

                    for programa in programas:
                        programa_manager.obtener_y_descargar_audio(programa)
                else:
                    print(f"URL no soportada o vacía: {url}")

        if config_manager.should_cleanup_old_files():
            cleanup_days = config_manager.get_cleanup_days()
            print(f"\n{'='*60}")
            print(f"Limpiando archivos antiguos (≥{cleanup_days} días)")
            print(f"{'='*60}")
            removed = borrar_archivos_viejos(directorio, cleanup_days)
            if removed and removed > 0:
                print(f"Archivos eliminados: {removed}")
    else:
        print(f"Procesando {len(enabled_programs)} programa(s) habilitado(s)\n")

        for program_config in enabled_programs:
            url = program_config["url"]
            name = program_config["name"]

            max_episodes = program_config.get('max_episodes', config_manager.get_max_episodes_per_program())
            cleanup_days = program_config.get('cleanup_days', config_manager.get_cleanup_days())

            print(f"\n{'='*60}")
            print(f"Procesando programa: {name}")
            print(f"URL: {url}")
            print(f"Max episodios: {max_episodes}")
            print(f"Limpieza después de: {cleanup_days} días")
            print(f"{'='*60}")

            if programa_manager.is_supported(url):
                programas = programa_manager.obtener_enlaces_programas(url, program_name=name)

                programas = programas[:max_episodes]

                for programa in programas:
                    programa_manager.obtener_y_descargar_audio(programa)

                if config_manager.should_cleanup_old_files():
                    nombre_carpeta = limpiar_nombre_archivo(name)
                    program_dir = Path(directorio) / nombre_carpeta

                    if program_dir.exists():
                        print(f"\nLimpiando archivos de '{name}' (≥{cleanup_days} días)...")
                        removed = borrar_archivos_viejos(str(program_dir), cleanup_days)
                        if removed and removed > 0:
                            print(f"Archivos eliminados: {removed}")
                        elif removed == 0:
                            print(f"No hay archivos para eliminar")
                    else:
                        print(f"Carpeta no existe aún: {program_dir}")
            else:
                print(f"URL no soportada para {name}: {url}")

    verificar_descargas(directorio, enabled_programs, programa_manager, config_manager)

    print("\n" + "="*60)
    print("¡Proceso completado!")
    print(f"Directorio: {directorio}")
    print(f"Dominios soportados: {len(programa_manager.get_supported_domains())}")
    print("="*60)


if __name__ == '__main__':
    main()