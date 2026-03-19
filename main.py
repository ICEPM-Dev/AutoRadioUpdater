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
        # PyInstaller crea una carpeta temporal y almacena la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def main():
    load_dotenv()
    
    # Initialize managers
    config_manager = ConfigManager()
    
    # Get download directory from config or environment
    directorio = os.getenv("DIRECTORIO") or config_manager.get_download_directory()
    programa_manager = ProgramaManager(directorio_base=directorio)
    
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
                    
                    # Limit episodes per program (usar default global)
                    max_episodes = config_manager.get_max_episodes_per_program()
                    programas = programas[:max_episodes]
                    
                    for programa in programas:
                        programa_manager.obtener_y_descargar_audio(programa)
                else:
                    print(f"URL no soportada o vacía: {url}")
        else:
            print("No se encontraron URLs en el archivo .env")
        
        # Clean up old files if enabled (usar default global)
        if config_manager.should_cleanup_old_files():
            cleanup_days = config_manager.get_cleanup_days()
            print(f"\n{'='*60}")
            print(f"🧹 Limpiando archivos antiguos (≥{cleanup_days} días)")
            print(f"{'='*60}")
            removed = borrar_archivos_viejos(directorio, cleanup_days)
            if removed and removed > 0:
                print(f"✅ Archivos eliminados: {removed}")
    else:
        # Process configured programs
        print(f"Procesando {len(enabled_programs)} programa(s) habilitado(s)\n")
        
        for program_config in enabled_programs:
            url = program_config["url"]
            name = program_config["name"]
            
            # Obtener configuración específica del programa o usar valores por defecto
            max_episodes = program_config.get('max_episodes', config_manager.get_max_episodes_per_program())
            cleanup_days = program_config.get('cleanup_days', config_manager.get_cleanup_days())
            
            print(f"\n{'='*60}")
            print(f"Procesando programa: {name}")
            print(f"URL: {url}")
            print(f"Max episodios: {max_episodes}")
            print(f"Limpieza después de: {cleanup_days} días")
            print(f"{'='*60}")
            
            if programa_manager.is_supported(url):
                # Pass the program name from config to override default
                programas = programa_manager.obtener_enlaces_programas(url, program_name=name)
                
                # Limit episodes using program-specific configuration
                programas = programas[:max_episodes]
                
                for programa in programas:
                    programa_manager.obtener_y_descargar_audio(programa)
                
                # Clean up old files with program-specific days
                if config_manager.should_cleanup_old_files():
                    # IMPORTANTE: Usar el nombre limpio del programa (igual que en descargarAudio.py)
                    nombre_carpeta = limpiar_nombre_archivo(name)
                    program_dir = Path(directorio) / nombre_carpeta
                    
                    if program_dir.exists():
                        print(f"\n🧹 Limpiando archivos de '{name}' (≥{cleanup_days} días)...")
                        removed = borrar_archivos_viejos(str(program_dir), cleanup_days)
                        if removed and removed > 0:
                            print(f"  ✅ Archivos eliminados: {removed}")
                        elif removed == 0:
                            print(f"  ℹ️  No hay archivos para eliminar")
                    else:
                        print(f"  ℹ️  Carpeta no existe aún: {program_dir}")
            else:
                print(f"❌ URL no soportada para {name}: {url}")
    
    print("\n" + "="*60)
    print("✅ ¡Proceso completado!")
    print(f"📁 Directorio: {directorio}")
    print(f"🌐 Dominios soportados: {len(programa_manager.get_supported_domains())}")
    print("="*60)


if __name__ == '__main__':
    main()