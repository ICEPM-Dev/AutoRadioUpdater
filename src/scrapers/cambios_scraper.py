import re
from typing import List, Dict
from datetime import datetime
from .base_scraper import BaseScraper


class CambiosProfundosScraper(BaseScraper):
    """Scraper for Cambios Profundos - Devocionales en Audio"""
    
    def get_episodes(self) -> List[Dict]:
        """Get episodes from Cambios Profundos website with smart detection"""
        episodes = []
        
        try:
            import requests
            import re
            from datetime import datetime, timedelta
            
            # Method 1: Try to find today's devotional using API endpoints
            today_episode = self._try_api_method()
            if today_episode:
                episodes.append(today_episode)
            
            # Method 2: Try date-based URL construction
            if not episodes:
                date_episode = self._try_date_pattern()
                if date_episode:
                    episodes.append(date_episode)
            
            # Method 3: Try to find audio in the page
            if not episodes:
                page_episode = self._try_page_scraping()
                if page_episode:
                    episodes.append(page_episode)
            
            # Method 4: Create a simulated episode with recent date
            if not episodes:
                simulated_episode = self._create_simulated_episode()
                episodes.append(simulated_episode)
            
        except Exception as e:
            print(f"Error getting Cambios Profundos episodes: {e}")
            # Fallback to simulated episode
            episodes = [self._create_simulated_episode()]
        
        return episodes
    
    def _try_api_method(self) -> Dict:
        """Try to find audio through WordPress API"""
        try:
            import requests
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            # Try to find media files uploaded recently
            media_url = 'https://cambiosprofundos.com/wp-json/wp/v2/media?per_page=20&order=desc&search=devocional'
            response = requests.get(media_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                media_files = response.json()
                for media in media_files:
                    if media.get('mime_type', '').startswith('audio/'):
                        title = media.get('title', {}).get('rendered', 'Devocional')
                        source_url = media.get('source_url', '')
                        
                        if source_url:
                            return {
                                "titulo": title,
                                "audio_url": source_url,
                                "nombre_programa": self.program_name
                            }
        except:
            pass
        
        return None
    
    def _try_date_pattern(self) -> Dict:
        """Try to construct audio URL using date patterns"""
        try:
            import requests
            from datetime import datetime, timedelta
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            base_url = 'https://cambiosprofundos.com'
            
            # Try different patterns for recent dates
            for i in range(7):
                date = datetime.now() - timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                year_month = date.strftime('%Y/%m')
                
                patterns = [
                    f'{base_url}/wp-content/uploads/{year_month}/devocional-{date_str}.mp3',
                    f'{base_url}/wp-content/uploads/{year_month}/cambios-{date_str}.mp3',
                    f'{base_url}/wp-content/uploads/audio/devocional-{date_str}.mp3',
                ]
                
                for url in patterns:
                    try:
                        response = requests.head(url, timeout=5)
                        if response.status_code == 200:
                            return {
                                "titulo": f"Devocional del día {date_str}",
                                "audio_url": url,
                                "nombre_programa": self.program_name
                            }
                    except:
                        continue
        except:
            pass
        
        return None
    
    def _try_page_scraping(self) -> Dict:
        """Try to find audio in the page content"""
        try:
            soup = self.get_page_content(self.base_url)
            if soup:
                import re
                
                # Look for MP3 URLs in scripts and content
                page_text = str(soup)
                mp3_matches = re.findall(r'https?://[^\s\"\'<>]*\.mp3', page_text)
                
                for mp3_url in mp3_matches:
                    # Verify it exists
                    try:
                        import requests
                        response = requests.head(mp3_url, timeout=5)
                        if response.status_code == 200:
                            return {
                                "titulo": "Devocional de Cambios Profundos",
                                "audio_url": mp3_url,
                                "nombre_programa": self.program_name
                            }
                    except:
                        continue
        except:
            pass
        
        return None
    
    def _create_simulated_episode(self) -> Dict:
        """Create a simulated episode for today with fallback audio"""
        from datetime import datetime
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Use a known working audio file as fallback
        # Try to find any devotional content online
        fallback_urls = [
            # Try some common devotional audio sources
            "https://www.biblegateway.com/audio/passage/daily/?version=NVI",
            "https://www.esv.org/resources/audio/qau/",
            # Create a local audio file instead
        ]
        
        # For now, create a placeholder that will generate a local file
        return {
            "titulo": f"Devocional del día {today}",
            "audio_url": "generate_local_audio",
            "nombre_programa": self.program_name,
            "simulated": True,
            "date": today
        }
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Extract audio URL from episode data"""
        # If we already have the direct audio URL
        if "audio_url" in episode_data:
            # If it's a simulated episode, try to verify or create a working alternative
            if episode_data.get("simulated"):
                print(f"Creando audio local para: {episode_data['titulo']}")
                
                # Try to find any working MP3 on the site
                real_audio = self._find_any_working_audio()
                if real_audio:
                    return real_audio
                else:
                    # Return special marker to generate local audio
                    return "generate_local_audio"
            
            return episode_data["audio_url"]
        
        # If this is a warning episode, return None
        if "warning" in episode_data:
            print(f"No se puede descargar audio automáticamente de {episode_data['titulo']}")
            return None
        
        return None
    
    def _find_any_working_audio(self) -> str:
        """Try to find any working audio on the site"""
        try:
            import requests
            import re
            from datetime import datetime
            
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            # Try some common patterns
            today = datetime.now()
            patterns = [
                f"https://cambiosprofundos.com/wp-content/uploads/{today.strftime('%Y/%m')}/devocional.mp3",
                f"https://cambiosprofundos.com/wp-content/uploads/audio/devocional.mp3",
                f"https://cambiosprofundos.com/devocional.mp3",
            ]
            
            for url in patterns:
                try:
                    response = requests.head(url, timeout=5)
                    if response.status_code == 200:
                        return url
                except:
                    continue
        
        except:
            pass
        
        return None