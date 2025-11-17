import requests
from typing import List, Dict
from datetime import datetime, timedelta
from .base_scraper import BaseScraper


class VisionParaVivirScraper(BaseScraper):
    """Scraper para Visión para Vivir - busca episodio más reciente"""
    
    def get_episodes(self) -> List[Dict]:
        """Busca el episodio más reciente de los últimos 10 días"""
        for days_ago in range(10):
            date = datetime.now() - timedelta(days=days_ago)
            url = f'https://insightforliving.swncdn.com/International/VPV/NA/Media/MP3/VPV{date.strftime("%Y-%m-%d")}-Podcast.mp3'
            
            try:
                if requests.head(url, timeout=10).status_code == 200:
                    return [{
                        "titulo": f"Visión para Vivir - {date.strftime('%d/%m/%Y')}",
                        "audio_url": url,
                        "nombre_programa": self.program_name
                    }]
            except:
                continue
        return []
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Retorna la URL de audio que ya tenemos"""
        return episode_data.get("audio_url")