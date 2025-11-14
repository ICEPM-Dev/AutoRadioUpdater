import os
from dotenv import load_dotenv

from src.borrarArchivosViejos import borrar_archivos_viejos
from src.programa_manager import ProgramaManager
from src.config_manager import ConfigManager


def main():
    load_dotenv()
    
    # Initialize managers
    config_manager = ConfigManager()
    
    # Get download directory from config or environment
    directorio = os.getenv("DIRECTORIO") or config_manager.get_download_directory()
    programa_manager = ProgramaManager(directorio_base=directorio)
    
    # Clean up old files if enabled
    if config_manager.should_cleanup_old_files():
        cleanup_days = config_manager.get_cleanup_days()
        borrar_archivos_viejos(directorio, cleanup_days)
    
    # Get enabled programs from configuration
    enabled_programs = config_manager.get_enabled_programs()
    
    if not enabled_programs:
        print("No hay programas habilitados en la configuración.")
        print("Usando URLs del archivo .env si están disponibles...")
        
        # Fallback to environment variable if no config programs
        programas_urls_env = os.getenv("PROGRAMAS_URL")
        if programas_urls_env:
            programas_urls = programas_urls_env.split(';')
            for url in programas_urls:
                url = url.strip()
                if url and programa_manager.is_supported(url):
                    print(f"\nProcesando: {url}")
                    programas = programa_manager.obtener_enlaces_programas(url)
                    
                    # Limit episodes per program
                    max_episodes = config_manager.get_max_episodes_per_program()
                    programas = programas[:max_episodes]
                    
                    for programa in programas:
                        programa_manager.obtener_y_descargar_audio(programa)
                else:
                    print(f"URL no soportada o vacía: {url}")
        else:
            print("No se encontraron URLs en el archivo .env")
    else:
        # Process configured programs
        for program_config in enabled_programs:
            url = program_config["url"]
            name = program_config["name"]
            
            print(f"\nProcesando programa: {name}")
            print(f"URL: {url}")
            
            if programa_manager.is_supported(url):
                # Pass the program name from config to override default
                programas = programa_manager.obtener_enlaces_programas(url, program_name=name)
                
                # Limit episodes per program
                max_episodes = config_manager.get_max_episodes_per_program()
                programas = programas[:max_episodes]
                
                for programa in programas:
                    programa_manager.obtener_y_descargar_audio(programa)
            else:
                print(f"URL no soportada para {name}: {url}")
    
    print("\n¡Proceso completado!")
    print(f"Dominios soportados: {', '.join(programa_manager.get_supported_domains())}")


if __name__ == '__main__':
    main()
