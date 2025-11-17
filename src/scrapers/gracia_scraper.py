import requests
from typing import List, Dict
from datetime import datetime, timedelta
from .base_scraper import BaseScraper


class GraciaScraper(BaseScraper):
    """Scraper simplificado para Gracia a Vosotros - construye URL directamente"""
    
    def get_episodes(self) -> List[Dict]:
        """Obtiene el episodio más reciente construyendo la URL directamente"""
        episodes = []
        
        # El patrón de URL es: https://cdn.gty.org/gracia/podcast/YYYYMMDD.mp3
        # Intentar los últimos 7 días
        for days_ago in range(7):
            date = datetime.now() - timedelta(days=days_ago)
            date_str = date.strftime('%Y%m%d')  # Formato: 20251114
            audio_url = f"https://cdn.gty.org/gracia/podcast/{date_str}.mp3"
            
            try:
                response = requests.head(audio_url, timeout=10)
                if response.status_code == 200:
                    episodes.append({
                        "titulo": f"Gracia a Vosotros - {date.strftime('%d/%m/%Y')}",
                        "audio_url": audio_url,
                        "nombre_programa": self.program_name
                    })
                    print(f"✓ Episodio encontrado: {date.strftime('%d/%m/%Y')}")
                    break
            except:
                continue
        
        return episodes[:1]  # Solo el más reciente
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Retorna la URL de audio que ya tenemos"""
        return episode_data.get("audio_url")