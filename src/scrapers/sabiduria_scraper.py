import re
from typing import List, Dict
from .base_scraper import BaseScraper


class SabiduriaInternacionalScraper(BaseScraper):
    """Scraper for Sabiduría Internacional radio program"""
    
    def __init__(self, base_url: str, program_name: str = None):
        super().__init__(base_url, program_name)
        # Use specific headers for Sabiduría Internacional to get full content
        self.specific_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
    
    def get_episodes(self) -> List[Dict]:
        """Get episodes from Sabiduría Internacional website (optimized)"""
        episodes = []
        
        try:
            # Use direct request to get full page content with scripts
            import requests
            response = requests.get(self.base_url, 
                                  headers=self.specific_headers,
                                  timeout=30)
            
            if response.status_code == 200:
                # Extract JSON data directly from response text
                json_match = re.search(r'var podcastPlayerData = ({.*?});', response.text, re.DOTALL)
                if json_match:
                    try:
                        import json
                        json_str = json_match.group(1)
                        data = json.loads(json_str)
                        
                        # Find podcast episodes
                        for key, value in data.items():
                            if key.startswith('pp-podcast'):
                                for episode_key, episode_data in value.items():
                                    if episode_key.startswith('ppe-'):
                                        title = episode_data.get('title', 'Programa del Día')
                                        audio_url = episode_data.get('src', '')
                                        
                                        if audio_url and 'podbean.com' in audio_url:
                                            episodes.append({
                                                "titulo": title,
                                                "audio_url": self.normalize_url(audio_url),
                                                "nombre_programa": self.program_name,
                                                "large_file": True  # Mark as potentially large file
                                            })
                                            
                                            # Get only the first episode to avoid long downloads
                                            if len(episodes) >= 1:
                                                break
                                if len(episodes) >= 1:
                                    break
                                if len(episodes) >= 1:
                                    break
                            if len(episodes) >= 1:
                                break
                            
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON: {e}")
                        
        except Exception as e:
            print(f"Error getting Sabiduría Internacional episodes: {e}")
        
        return episodes
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Extract audio URL from episode data"""
        # If we already have the direct audio URL
        if "audio_url" in episode_data:
            return episode_data["audio_url"]
        
        # If we need to visit the episode page
        if "escuchar_link" in episode_data:
            soup = self.get_page_content(episode_data["escuchar_link"])
            if soup:
                # Look for audio elements
                audio = soup.find('audio')
                if audio:
                    src = audio.get('src') or (audio.find('source') and audio.find('source').get('src'))
                    if src:
                        return self.normalize_url(src)
                
                # Look for direct audio links
                audio_link = soup.find('a', href=re.compile(r'\.(mp3|wav|m4a)'))
                if audio_link:
                    return self.normalize_url(audio_link['href'])
        
        return None
