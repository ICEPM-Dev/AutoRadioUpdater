from typing import List, Dict
from .youtube_scraper import YouTubeScraper


class CarlosRuizScraper(YouTubeScraper):
    """Scraper para Carlos Ruiz Devocionales - Solo videos cortos (≤3 min)"""
    
    def __init__(self, base_url: str, program_name: str):
        # Inicializar con límite de 3 minutos (180 segundos)
        super().__init__(base_url, program_name, max_duration_seconds=180)
    
    def get_episodes(self) -> List[Dict]:
        """Get short devotional videos (≤3 minutes)"""
        print(f"   🎥 Buscando devocionales cortos (≤3 min) en YouTube...")
        
        # Obtener videos filtrados por duración
        videos = super().get_episodes()
        
        if not videos:
            return []
        
        # Información adicional sobre el filtrado
        print(f"   ℹ️  Videos devocionales encontrados:")
        for i, video in enumerate(videos[:5], 1):  # Mostrar primeros 5
            duration = int(video.get('duration_seconds', 0))
            minutes = duration // 60
            seconds = duration % 60
            title_short = video['titulo'][:50]
            print(f"      {i}. {title_short}... ({minutes}:{seconds:02d})")
        
        if len(videos) > 5:
            print(f"      ... y {len(videos) - 5} más")
        
        return videos