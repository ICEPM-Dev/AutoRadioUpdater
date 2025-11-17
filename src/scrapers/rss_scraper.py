import requests
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class RSSFeedScraper(BaseScraper):
    """Scraper genérico para RSS feeds (Anchor, Podbean, etc.)"""
    
    def __init__(self, url=None, program_name=None):
        super().__init__(url or "", program_name)
        self.program_name = program_name or "Podcast RSS"
        
    def get_episodes(self, url=None, max_episodes=5):
        """Obtiene episodios desde un RSS feed"""
        
        print(f"\n🔍 Obteniendo episodios desde RSS feed...")
        
        episodes = []
        
        try:
            response = requests.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            # Parsear como XML
            soup = BeautifulSoup(response.content, 'xml')
            
            # Buscar todos los items
            items = soup.find_all('item')
            
            print(f"✓ Encontrados {len(items)} episodios en el feed")
            
            for item in items[:max_episodes]:
                # Obtener título
                title_tag = item.find('title')
                title = title_tag.get_text(strip=True) if title_tag else "Episodio"
                
                # Buscar URL del audio en enclosure
                enclosure = item.find('enclosure')
                
                audio_url = None
                if enclosure:
                    audio_url = enclosure.get('url')
                
                # Si no hay enclosure, buscar en otros tags
                if not audio_url:
                    # Buscar en link
                    link_tag = item.find('link')
                    if link_tag:
                        link_text = link_tag.get_text(strip=True)
                        if '.mp3' in link_text or '.m4a' in link_text:
                            audio_url = link_text
                
                if audio_url:
                    episodes.append({
                        "titulo": title,
                        "audio_url": audio_url,
                        "nombre_programa": self.program_name
                    })
                    
                    print(f"  📝 {title}")
                else:
                    print(f"  ⚠ Sin audio: {title}")
        
        except Exception as e:
            print(f"✗ Error: {e}")
        
        return episodes
    
    def get_audio_url(self, episode_data):
        """Ya tenemos la URL del audio desde el RSS"""
        return episode_data.get("audio_url")