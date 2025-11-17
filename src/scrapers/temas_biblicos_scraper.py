import re
from typing import List, Dict
from .base_scraper import BaseScraper


class TemasBiblicosScraper(BaseScraper):
    """Scraper para Temas Bíblicos desde Acast"""
    
    def get_episodes(self) -> List[Dict]:
        """Obtiene el episodio más reciente"""
        soup = self.get_page_content("https://shows.acast.com/temas-biblicos/episodes")
        if not soup:
            return []
        
        # Buscar primer link de episodio
        link = soup.find('a', href=re.compile(r'/temas-biblicos/episodes/'))
        if link:
            title = link.find('h2')
            return [{
                "titulo": title.text.strip() if title else "Temas Bíblicos",
                "escuchar_link": f"https://shows.acast.com{link['href']}",
                "nombre_programa": self.program_name
            }]
        return []
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Extrae URL de audio desde la página del episodio"""
        soup = self.get_page_content(episode_data.get("escuchar_link"))
        if not soup:
            return None
        
        # Buscar elemento audio
        audio = soup.find('audio')
        if audio and audio.get('src'):
            return audio.get('src')
        
        # Buscar en el HTML
        match = re.search(r'https://[^"\s]*\.acast\.com/[^"\s]*\.mp3[^"\s]*', str(soup))
        return match.group(0) if match else None