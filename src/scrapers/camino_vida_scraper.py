import requests
from datetime import datetime
from .base_scraper import BaseScraper

class CaminoVidaScraper(BaseScraper):
    """Scraper para El Camino de la Vida - construcción directa de URLs"""
    
    def __init__(self, url=None, program_name=None):
        super().__init__(url or "https://www.elcaminodelavida.org/reflexion-para-hoy/", program_name)
        self.program_name = program_name or "El Camino de la Vida"
        
    def get_episodes(self, url=None, max_episodes=5):
        """Construye URLs de episodios recientes y verifica cuáles existen"""
        
        print(f"\n🔍 Buscando episodios recientes...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.elcaminodelavida.org/'
        }
        
        # IMPORTANTE: El mes en el path es 12, no 11
        month = "12"
        base_episode = 4573
        
        print(f"  📊 Probando desde RPH {base_episode} hacia atrás (mes {month})")
        
        episodes = []
        
        for i in range(30):
            episode_num = base_episode - i
            url = f"https://medios.elcaminodelavida.org/audio/WEB-RPH/WEB-RPH{month}/RPH{episode_num}-WEB.mp3"
            
            try:
                response = requests.get(url, headers=headers, timeout=10, stream=True)
                
                if response.status_code == 200:
                    response.close()
                    
                    episodes.append({
                        "titulo": f"RPH {episode_num}",
                        "audio_url": url,
                        "nombre_programa": self.program_name
                    })
                    
                    print(f"  ✓ RPH {episode_num}")
                    
                    if len(episodes) >= max_episodes:
                        break
                elif i < 5:
                    print(f"  ✗ RPH {episode_num} (HTTP {response.status_code})")
            except Exception as e:
                if i < 5:
                    print(f"  ✗ RPH {episode_num} error: {str(e)[:50]}")
        
        return episodes
    
    def get_audio_url(self, episode_data):
        """Ya tenemos la URL directa"""
        return episode_data.get("audio_url")