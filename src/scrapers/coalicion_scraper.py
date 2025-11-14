import re
from typing import List, Dict
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper


class CoalicionScraper(BaseScraper):
    """Scraper for Coalición por el Evangelio - Podcasts"""
    
    def __init__(self, base_url: str, program_name: str = None):
        super().__init__(base_url, program_name)
        # Add additional headers for Coalición to avoid 520 error
        self.session.headers.update({
            'Referer': 'https://www.coalicionporelevangelio.org/',
            'DNT': '1',
            'Sec-GPC': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        })
    
    def get_episodes(self) -> List[Dict]:
        """Get episodes from Coalición por el Evangelio website"""
        episodes = []
        
        # Try RSS feed first
        rss_url = "https://www.coalicionporelevangelio.org/podcasts/mujeres/feed/"
        try:
            import feedparser
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries[:5]:  # Get first 5 episodes
                title = entry.title if hasattr(entry, 'title') else "Podcast Mujeres"
                
                # Look for audio enclosure in RSS
                audio_url = None
                if hasattr(entry, 'enclosures') and entry.enclosures:
                    for enclosure in entry.enclosures:
                        if enclosure.type.startswith('audio/'):
                            audio_url = enclosure.href
                            break
                
                if audio_url:
                    episodes.append({
                        "titulo": title,
                        "audio_url": audio_url,
                        "nombre_programa": self.program_name
                    })
                else:
                    # If no audio in RSS, try to get from link
                    if hasattr(entry, 'link'):
                        episodes.append({
                            "titulo": title,
                            "escuchar_link": entry.link,
                            "nombre_programa": self.program_name
                        })
            
            if episodes:
                return episodes
                
        except ImportError:
            pass
        except Exception as e:
            print(f"Error parsing RSS feed: {e}")
        
        # Fallback: Parse HTML
        soup = self.get_page_content(self.base_url)
        if not soup:
            return []
        
        # Look for the episodes wrapper
        episodes_wrapper = soup.find('div', class_='episodes_wrapper')
        
        if episodes_wrapper:
            # Find all episode divs with class single_episode
            episode_divs = episodes_wrapper.find_all('div', class_='single_episode')
            
            for episode_div in episode_divs:
                # Get title from the episode
                title_element = episode_div.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                title = title_element.text.strip() if title_element else "Podcast Mujeres"
                
                # Look for any audio link
                audio_link = episode_div.find('a', href=re.compile(r'\.mp3', re.I))
                if audio_link:
                    href = audio_link.get('href')
                    if href:
                        episodes.append({
                            "titulo": title,
                            "audio_url": href,
                            "nombre_programa": self.program_name
                        })
                else:
                    # Look for the episode page link
                    episode_link = episode_div.find('a', href=True)
                    if episode_link:
                        href = episode_link.get('href')
                        if href:
                            episodes.append({
                                "titulo": title,
                                "escuchar_link": self.normalize_url(href),
                                "nombre_programa": self.program_name
                            })
                
                # Limit to first 5 episodes
                if len(episodes) >= 5:
                    break
                
                # Look for podcast links or play buttons
                podcast_link = section.find('a', href=re.compile(r'\.(mp3|wav|m4a)'))
                if not podcast_link:
                    podcast_link = section.find('a', string=re.compile(r'(escuchar|play|podcast|descargar|download)', re.I))
                
                if title and podcast_link and not any(ep["titulo"] == title for ep in episodes):
                    href = podcast_link.get('href', '')
                    if '.mp3' in href or '.wav' in href or '.m4a' in href:
                        episodes.append({
                            "titulo": title,
                            "audio_url": self.normalize_url(href),
                            "nombre_programa": self.program_name
                        })
                    else:
                        episodes.append({
                            "titulo": title,
                            "escuchar_link": self.normalize_url(href),
                            "nombre_programa": self.program_name
                        })
        
        return episodes
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Extract audio URL from episode data"""
        # If we already have the direct audio URL
        if "audio_url" in episode_data:
            return episode_data["audio_url"]
        
        # If we need to visit the episode page
        if "escuchar_link" in episode_data:
            # Create a new session with proper headers
            import requests
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            })
            
            # First visit the main page to establish session
            main_url = "https://www.coalicionporelevangelio.org/podcasts/mujeres/"
            try:
                session.get(main_url, timeout=10)
            except:
                pass
            
            # Now visit the episode page
            response = session.get(episode_data["escuchar_link"], timeout=30)
            if response.status_code == 200:
                # Look for MP3 URLs in the response
                mp3_matches = re.findall(r'https?://[^\s"\'<>]*\.mp3', response.text)
                for mp3_url in mp3_matches:
                    if 'media.blubrry.com' in mp3_url or 'thegospelcoalition.org' in mp3_url:
                        return mp3_url
                
                # Also check data-src attributes
                data_src_matches = re.findall(r'data-src="([^"]*\.mp3)"', response.text)
                for mp3_url in data_src_matches:
                    if 'media.blubrry.com' in mp3_url or 'thegospelcoalition.org' in mp3_url:
                        return mp3_url
        
        return None