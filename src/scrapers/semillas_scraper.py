import re
from typing import List, Dict
from .base_scraper import BaseScraper


class SemillasScraper(BaseScraper):
    """Scraper for Semillas al Aire radio program"""
    
    def get_episodes(self) -> List[Dict]:
        """Get episodes from Semillas al Aire website"""
        soup = self.get_page_content(self.base_url)
        if not soup:
            return []
        
        episodes = []
        
        # Look for the specific audio element with class "sonaar_media_element"
        audio_element = soup.find('audio', class_='sonaar_media_element')
        if audio_element:
            # The audio URL is in the data-audiopath attribute
            src = audio_element.get('data-audiopath') or audio_element.get('src')
            if src and '.mp3' in src:
                episodes.append({
                    "titulo": "Programa del Día",
                    "audio_url": self.normalize_url(src),
                    "nombre_programa": self.program_name
                })
        
        # Fallback: Look for elements with data-audiopath attribute
        if not episodes:
            elements_with_audio = soup.find_all(attrs={'data-audiopath': True})
            for elem in elements_with_audio:
                src = elem.get('data-audiopath')
                if src and '.mp3' in src:
                    episodes.append({
                        "titulo": "Programa del Día",
                        "audio_url": self.normalize_url(src),
                        "nombre_programa": self.program_name
                    })
                    break
        
        # Last fallback: Look for any audio elements with src
        if not episodes:
            audio_elements = soup.find_all('audio')
            for audio in audio_elements:
                src = audio.get('src')
                if src and '.mp3' in src:
                    episodes.append({
                        "titulo": "Programa del Día",
                        "audio_url": self.normalize_url(src),
                        "nombre_programa": self.program_name
                    })
                    break
        
        return episodes
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Extract audio URL - for this scraper, it's already in the episode data"""
        return episode_data.get("audio_url")
