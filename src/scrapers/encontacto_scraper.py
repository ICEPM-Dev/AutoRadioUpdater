import requests
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class EnContactoScraper(BaseScraper):
    """
    Scraper para En Contacto Global (Dr. Charles Stanley)
    Usa el RSS feed de Omny para obtener los episodios más recientes
    """
    
    def __init__(self, base_url, nombre_programa="En Contacto"):
        super().__init__(base_url, nombre_programa)
        self.rss_url = "https://www.omnycontent.com/d/playlist/7237c071-cd56-4495-998a-b23d00f69e8d/1cb79382-cef3-4954-9d99-b26701579b3b/c69d90a4-30b9-49b8-b6b2-b26701579b6e/podcast.rss"
    
    def get_episodes(self):
        """Obtiene episodios desde el RSS feed de Omny"""
        print(f"\n🔍 Obteniendo episodios desde RSS de Omny...")
        
        try:
            response = requests.get(
                self.rss_url,
                timeout=15,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            if response.status_code != 200:
                print(f"   ✗ Error HTTP {response.status_code}")
                return []
            
            # Parsear el RSS
            soup = BeautifulSoup(response.content, 'xml')
            
            # Buscar todos los items (episodios)
            items = soup.find_all('item')
            
            if not items:
                print(f"   ✗ No se encontraron episodios en el RSS")
                return []
            
            print(f"   ✓ Encontrados {len(items)} episodios en el RSS")
            
            episodes = []
            for item in items[:10]:  # Limitar a 10 más recientes
                # Extraer información del episodio
                title = item.find('title')
                enclosure = item.find('enclosure')
                pub_date = item.find('pubDate')
                
                if title and enclosure:
                    audio_url = enclosure.get('url')
                    episode_title = title.text.strip()
                    
                    episodes.append({
                        'titulo': episode_title,
                        'audio_url': audio_url,
                        'fecha': pub_date.text.strip() if pub_date else '',
                        'nombre_programa': self.program_name
                    })
            
            return episodes
            
        except Exception as e:
            print(f"   ✗ Error obteniendo RSS: {e}")
            return []
    
    def get_audio_url(self, episode_data):
        """Retorna la URL de audio directamente desde el RSS"""
        return episode_data.get('audio_url')