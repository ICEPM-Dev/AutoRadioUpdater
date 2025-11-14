import re
import json
from typing import List, Dict
from .base_scraper import BaseScraper


class AcastScraper(BaseScraper):
    """Scraper for Acast podcast platform"""
    
    def get_episodes(self) -> List[Dict]:
        """Get episodes from Acast podcast - get today's episode"""
        episodes = []
        
        # Extract show ID from URL and get today's episode
        show_id = self._extract_show_id(self.base_url)
        if show_id:
            today_episode = self._get_today_episode(show_id)
            if today_episode:
                episodes.append(today_episode)
        
        return episodes
    
    def _get_single_episode(self, episode_url: str) -> Dict:
        """Get a single episode from Acast"""
        soup = self.get_page_content(episode_url)
        if not soup:
            return None
        
        # Extract episode information
        title = None
        audio_url = None
        
        # Look for title in various places
        title_element = soup.find('h1') or soup.find('title')
        if title_element:
            title = title_element.text.strip()
        
        # Look for og:audio meta tag first
        og_audio = soup.find('meta', property='og:audio')
        if og_audio:
            audio_url = og_audio.get('content')
        
        # Look for JSON-LD structured data
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    # Check if it's a podcast episode
                    if data.get('@type') == 'PodcastEpisode':
                        if not title and data.get('name'):
                            title = data['name']
                        
                        # Look for audio URL
                        if data.get('associatedMedia'):
                            media = data['associatedMedia']
                            if isinstance(media, dict) and media.get('contentUrl'):
                                audio_url = media['contentUrl']
                            elif isinstance(media, list) and len(media) > 0:
                                audio_url = media[0].get('contentUrl')
            except (json.JSONDecodeError, KeyError):
                continue
        
        # Look for audio elements in the page
        if not audio_url:
            audio_element = soup.find('audio')
            if audio_element:
                audio_url = audio_element.get('src')
                if not audio_url:
                    source = audio_element.find('source')
                    if source:
                        audio_url = source.get('src')
        
        # Look for download links or play buttons
        if not audio_url:
            # Look for links that might contain audio URLs
            audio_links = soup.find_all('a', href=re.compile(r'\.(mp3|wav|m4a)'))
            if audio_links:
                audio_url = audio_links[0]['href']
        
        # Look in script tags for audio URLs
        if not audio_url:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    # Look for audio URLs in JavaScript
                    audio_match = re.search(r'["\']https?://[^"\']*\.(mp3|wav|m4a)[^"\']*["\']', script.string)
                    if audio_match:
                        audio_url = audio_match.group(0).strip('"\'')
                        break
                    
                    # Look for Acast-specific audio URLs
                    acast_match = re.search(r'["\']https?://[^"\']*acast[^"\']*\.mp3[^"\']*["\']', script.string)
                    if acast_match:
                        audio_url = acast_match.group(0).strip('"\'')
                        break
        
        if title and audio_url:
            return {
                "titulo": title,
                "audio_url": self.normalize_url(audio_url),
                "nombre_programa": self.program_name
            }
        elif title:
            # If we have title but no direct audio URL, return with episode link
            return {
                "titulo": title,
                "escuchar_link": episode_url,
                "nombre_programa": self.program_name
            }
        
        return None
    
    def _extract_show_id(self, url: str) -> str:
        """Extract show ID from Acast URL"""
        # First try to get the actual show name from the episode page
        soup = self.get_page_content(url)
        if soup:
            # Look for canonical URL or actual show link
            canonical = soup.find('link', rel='canonical')
            if canonical:
                canonical_url = canonical.get('href', '')
                match = re.search(r'shows\.acast\.com/([^/]+)/', canonical_url)
                if match:
                    return match.group(1)
            
            # Look for show link in the page
            show_links = soup.find_all('a', href=re.compile(r'shows\.acast\.com/([^/]+)/'))
            for link in show_links:
                href = link.get('href', '')
                match = re.search(r'shows\.acast\.com/([^/]+)/', href)
                if match and match.group(1) != 'www':
                    return match.group(1)
        
        # Fallback: extract from original URL
        match = re.search(r'shows\.acast\.com/([^/]+)/', url)
        if match:
            return match.group(1)
        return None
    
    def _get_today_episode(self, show_id: str) -> Dict:
        """Get today's episode from the show"""
        from datetime import datetime
        
        # Get the show page to find episodes
        show_url = f"https://shows.acast.com/{show_id}"
        soup = self.get_page_content(show_url)
        if not soup:
            return None
        
        # Look for episode list items
        episode_items = soup.find_all('a', href=re.compile(f'/{show_id}/episodes/'))
        
        for item in episode_items:
            href = item['href']
            # Make sure it's a full URL
            if href.startswith('/'):
                episode_url = f"https://shows.acast.com{href}"
            else:
                episode_url = href
            
            episode = self._get_single_episode_with_date_check(episode_url)
            if episode and self._is_today_episode(episode_url):
                return episode
        
        return None
    
    def _get_single_episode_with_date_check(self, episode_url: str) -> Dict:
        """Get episode with date information"""
        soup = self.get_page_content(episode_url)
        if not soup:
            return None
        
        # Extract episode information (reuse existing logic)
        title = None
        audio_url = None
        
        # Look for title
        title_element = soup.find('h1') or soup.find('title')
        if title_element:
            title = title_element.text.strip()
        
        # Look for date in the episode
        date_element = soup.find('time')
        episode_date = None
        if date_element:
            date_text = date_element.text.strip()
            episode_date = self._parse_date(date_text)
        
        # Look for audio URL (reuse existing logic)
        og_audio = soup.find('meta', property='og:audio')
        if og_audio:
            audio_url = og_audio.get('content')
        
        if not audio_url:
            audio_element = soup.find('audio')
            if audio_element:
                audio_url = audio_element.get('src')
                if not audio_url:
                    source = audio_element.find('source')
                    if source:
                        audio_url = source.get('src')
        
        if title and audio_url:
            result = {
                "titulo": title,
                "audio_url": self.normalize_url(audio_url),
                "nombre_programa": self.program_name
            }
            if episode_date:
                result["episode_date"] = episode_date
            return result
        
        return None
    
    def _parse_date(self, date_text: str) -> str:
        """Parse date from Spanish date text"""
        # Example: "viernes, 14 de noviembre de 2025"
        import re
        from datetime import datetime
        
        # Remove day of week
        date_clean = re.sub(r'^[a-záéíóúñ]+\s*,?\s*', '', date_text.strip(), flags=re.I)
        
        # Map Spanish months to numbers
        month_map = {
            'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
            'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
            'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
        }
        
        # Match pattern: "14 de noviembre de 2025"
        match = re.search(r'(\d+)\s+de\s+([a-záéíóúñ]+)\s+de\s+(\d+)', date_clean, re.I)
        if match:
            day, month_name, year = match.groups()
            month = month_map.get(month_name.lower())
            if month:
                return f"{year}-{month}-{day.zfill(2)}"
        
        return None
    
    def _is_today_episode(self, episode_url: str) -> bool:
        """Check if episode is from today"""
        soup = self.get_page_content(episode_url)
        if not soup:
            return False
        
        date_element = soup.find('time')
        if date_element:
            date_text = date_element.text.strip()
            episode_date = self._parse_date(date_text)
            
            if episode_date:
                from datetime import datetime
                today = datetime.now().strftime('%Y-%m-%d')
                return episode_date == today
        
        return False
    
    def _get_show_episodes(self) -> List[Dict]:
        """Get all episodes from an Acast show"""
        soup = self.get_page_content(self.base_url)
        if not soup:
            return []
        
        episodes = []
        
        # Look for episode links
        episode_links = soup.find_all('a', href=re.compile(r'/episodes/'))
        
        for link in episode_links[:10]:  # Limit to 10 most recent episodes
            episode_url = self.normalize_url(link['href'])
            episode = self._get_single_episode(episode_url)
            if episode:
                episodes.append(episode)
        
        # If no episode links found, look for embedded episode data
        if not episodes:
            # Look for JSON data that might contain episodes
            json_scripts = soup.find_all('script', type='application/ld+json')
            for script in json_scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and data.get('@type') == 'PodcastSeries':
                        # This might contain episode information
                        pass
                except json.JSONDecodeError:
                    continue
        
        return episodes
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Extract audio URL from episode data"""
        # If we already have the direct audio URL
        if "audio_url" in episode_data:
            return episode_data["audio_url"]
        
        # If we need to visit the episode page
        if "escuchar_link" in episode_data:
            episode = self._get_single_episode(episode_data["escuchar_link"])
            if episode and "audio_url" in episode:
                return episode["audio_url"]
        
        return None
