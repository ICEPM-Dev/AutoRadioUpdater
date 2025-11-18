import requests
from datetime import datetime, timedelta
from .base_scraper import BaseScraper

class EnContactoScraper(BaseScraper):
    """Scraper para En Contacto Global - construcción directa de URLs"""
    
    def __init__(self, url=None, program_name=None):
        super().__init__(url or "https://www.encontactoglobal.org/escuche", program_name)
        self.program_name = program_name or "En Contacto Global"
        
    def get_episodes(self, url=None, max_episodes=5):
        """Construye URLs de episodios recientes basándose en fechas"""
        
        print(f"\n🔍 Construyendo episodios de En Contacto...")
        
        # Pattern: https://intouch.azureedge.net/spanish/pgm/ec_pgm_YYYY_MM_DD_XXXXX.mp3
        # Ejemplo: ec_pgm_2025_11_17_28610.mp3
        
        episodes = []
        today = datetime.now()
        
        print(f"  📅 Buscando episodios desde {today.strftime('%Y-%m-%d')}...")
        
        # Intentar los últimos 10 días (suelen publicar diariamente)
        for days_back in range(10):
            date = today - timedelta(days=days_back)
            
            # Formato de fecha: YYYY_MM_DD
            date_str = date.strftime("%Y_%m_%d")
            
            # El último número (28610) parece ser incremental
            # Intentar varios números alrededor de un base estimado
            
            # Calcular número aproximado basado en la fecha
            # Si ec_pgm_2025_11_17 = 28610
            reference_date = datetime(2025, 11, 17)
            reference_num = 28610
            
            days_diff = (date - reference_date).days
            estimated_num = reference_num + days_diff
            
            # Probar números alrededor del estimado
            for offset in range(-2, 3):  # Probar ±2
                episode_num = estimated_num + offset
                
                # Construir URL del audio
                audio_url = f"https://intouch.azureedge.net/spanish/pgm/ec_pgm_{date_str}_{episode_num}.mp3"
                
                # Verificar si existe
                try:
                    response = requests.head(audio_url, timeout=5, allow_redirects=True)
                    if response.status_code == 200:
                        title = f"En Contacto - {date.strftime('%d/%m/%Y')}"
                        
                        episodes.append({
                            "titulo": title,
                            "audio_url": audio_url,
                            "nombre_programa": self.program_name
                        })
                        
                        print(f"  ✓ {title} (#{episode_num})")
                        
                        if len(episodes) >= max_episodes:
                            return episodes
                        
                        break  # Encontró este día, pasar al siguiente
                except:
                    pass
        
        if not episodes:
            print(f"  ⚠ No se encontraron episodios en los últimos 10 días")
            print(f"  💡 Episodio más reciente conocido: 2025_11_17 (#28610)")
        
        return episodes
    
    def get_audio_url(self, episode_data):
        """Ya tenemos la URL del audio construida"""
        return episode_data.get("audio_url")