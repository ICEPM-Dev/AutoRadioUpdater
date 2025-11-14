from typing import List, Dict
from .scraper_factory import ScraperFactory
from .descargarAudio import descargar_audio


class ProgramaManager:
    """Generic manager for radio programs"""
    
    def __init__(self, directorio_base=None):
        self.factory = ScraperFactory()
        self.directorio_base = directorio_base
    
    def obtener_enlaces_programas(self, url: str, program_name: str = None) -> List[Dict]:
        """Get program episodes from any supported radio website"""
        try:
            scraper = self.factory.create_scraper(url)
            
            # Override the program name if provided (for multiple programs from same domain)
            if program_name:
                scraper.program_name = program_name
            
            episodes = scraper.get_episodes()
            
            # Update episode data with the correct program name and original URL
            for episode in episodes:
                episode["nombre_programa"] = scraper.program_name
                episode["original_url"] = url  # Store original URL for proper scraper creation
            
            print(f"Encontrados {len(episodes)} episodios en {scraper.program_name}")
            return episodes
        except ValueError as e:
            print(f"Error: {e}")
            return []
        except Exception as e:
            print(f"Error inesperado al procesar {url}: {e}")
            return []
    
    def obtener_y_descargar_audio(self, programa: Dict):
        """Get and download audio from program episode"""
        try:
            # If we already have the audio URL, use it directly
            if "audio_url" in programa:
                audio_url = programa["audio_url"]
            else:
                # Otherwise, we need to extract it using the appropriate scraper
                # We need to determine which scraper to use based on the episode data
                if "escuchar_link" in programa:
                    # Create scraper based on the original URL to ensure correct scraper type
                    original_url = programa.get("original_url")
                    if not original_url:
                        # Fallback: try to determine original URL from program name
                        if "Visión para Vivir" in programa.get("nombre_programa", ""):
                            original_url = "https://visionparavivir.org/escuche/programa-actual/"
                        elif "Coalición" in programa.get("nombre_programa", ""):
                            original_url = "https://www.coalicionporelevangelio.org/podcasts/mujeres/"
                        elif "Ligonier" in programa.get("nombre_programa", ""):
                            original_url = "https://es.ligonier.org/renovandotumente/archivo/"
                        elif "Camino" in programa.get("nombre_programa", ""):
                            original_url = "https://www.elcaminodelavida.org/reflexion-para-hoy/"
                        else:
                            original_url = programa["escuchar_link"]  # Last resort
                    
                    scraper = self.factory.create_scraper(original_url)
                    
                    # Override program name to maintain consistency
                    if "nombre_programa" in programa:
                        scraper.program_name = programa["nombre_programa"]
                    
                    audio_url = scraper.get_audio_url(programa)
                else:
                    print(f"No se puede obtener el audio para {programa['titulo']}")
                    return
            
            if audio_url:
                descargar_audio(audio_url, programa["nombre_programa"], programa["titulo"], self.directorio_base)
            else:
                print(f"No se encontró enlace de audio para {programa['titulo']}")
                
        except Exception as e:
            print(f"Error al procesar {programa['titulo']}: {e}")
    
    def get_supported_domains(self) -> List[str]:
        """Get list of supported domains"""
        return self.factory.get_supported_domains()
    
    def is_supported(self, url: str) -> bool:
        """Check if URL is supported"""
        return self.factory.is_supported(url)
