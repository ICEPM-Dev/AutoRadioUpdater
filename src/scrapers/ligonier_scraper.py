import re
from typing import List, Dict
from .base_scraper import BaseScraper


class LigonierScraper(BaseScraper):
    """Scraper for Ligonier Ministries - Renovando tu Mente"""
    
    def __init__(self, base_url: str, program_name: str = None):
        super().__init__(base_url, program_name)
        # Add additional headers for Ligonier to avoid 403
        self.session.headers.update({
            'Referer': 'https://es.ligonier.org/',
            'DNT': '1',
            'Sec-GPC': '1',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        })
    
    def get_episodes(self) -> List[Dict]:
        """Get episodes from Ligonier website"""
        episodes = []
        
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Simple request to get the page
            response = requests.get(self.base_url, 
                                  headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                                  timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for the Content main and portfolio columns as you mentioned
                content_main = soup.find('div', id='Content', role='main')
                
                if content_main:
                    # Look for portfolio columns
                    portfolio_columns = content_main.find_all('div', class_='column_portfolio')
                    
                    for column in portfolio_columns:
                        # Look for portfolio items (episodes)
                        portfolio_items = column.find_all('li', class_='portfolio-item')
                        
                        for item in portfolio_items[:5]:  # Limit to first 5 episodes
                            # Get title from the item
                            title_element = item.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                            title = title_element.text.strip() if title_element else "Renovando tu Mente"
                            
                            # Look for episode link
                            episode_link = item.find('a', href=True)
                            if episode_link:
                                href = episode_link.get('href')
                                if href and '/rtm/' in href:  # Only include RTM episode links
                                    episodes.append({
                                        "titulo": title,
                                        "escuchar_link": self.normalize_url(href),
                                        "nombre_programa": self.program_name
                                    })
                                    
                                    # Limit to first 5 episodes
                                    if len(episodes) >= 5:
                                        break
                        
                        if len(episodes) >= 5:
                            break
                        
        except Exception as e:
            print(f"Error getting Ligonier episodes: {e}")
        
        # Fallback: Look for episode sections if portfolio not found
        if not episodes:
            episode_sections = soup.find_all(['div', 'article', 'section'], class_=re.compile(r'(episode|programa|archive)', re.I))
            
            for section in episode_sections:
                title_element = section.find(['h1', 'h2', 'h3', 'h4'])
                title = title_element.text.strip() if title_element else None
                
                # Look for audio links or play buttons
                audio_link = section.find('a', href=re.compile(r'\.(mp3|wav|m4a)'))
                if not audio_link:
                    audio_link = section.find('a', string=re.compile(r'(escuchar|play|audio)', re.I))
                
                if title and audio_link:
                    episodes.append({
                        "titulo": title,
                        "escuchar_link": self.normalize_url(audio_link['href']),
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
            # Use direct request to get full page content with JavaScript
            try:
                import requests
                # Use specific headers to get full content
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
                    'Referer': 'https://es.ligonier.org/',
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache',
                }
                response = requests.get(episode_data["escuchar_link"], 
                                      headers=headers,
                                      timeout=30)
                
                if response.status_code == 200:
                    # First try direct text search for podtrac URLs
                    if 'dts.podtrac.com' in response.text:
                        start = response.text.find('//dts.podtrac.com')
                        if start != -1:
                            # Find end of URL
                            end_chars = ['"', "'", ' ', ')', '}', ']', '\n', '\r']
                            end = len(response.text)
                            
                            for char in end_chars:
                                pos = response.text.find(char, start)
                                if pos != -1 and pos < end:
                                    end = pos
                            
                            url = response.text[start:end]
                            if url.startswith('//'):
                                url = 'https:' + url
                            return url
                    
                    # Fallback to BeautifulSoup parsing
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                else:
                    return None
            except:
                return None
            
            if soup:
                # Look for audio elements with specific attributes
                audio_elements = soup.find_all('audio', attrs={'controls': True})
                for audio in audio_elements:
                    source = audio.find('source')
                    if source:
                        src = source.get('src')
                        if src and '.mp3' in src:
                            # Fix protocol-relative URLs
                            if src.startswith('//'):
                                src = 'https:' + src
                            return self.normalize_url(src)
                    src = audio.get('src')
                    if src and '.mp3' in src:
                        if src.startswith('//'):
                            src = 'https:' + src
                        return self.normalize_url(src)
                
                # Look for any audio elements
                audio = soup.find('audio')
                if audio:
                    source = audio.find('source')
                    if source:
                        src = source.get('src')
                        if src:
                            if src.startswith('//'):
                                src = 'https:' + src
                            return self.normalize_url(src)
                    src = audio.get('src')
                    if src:
                        if src.startswith('//'):
                            src = 'https:' + src
                        return self.normalize_url(src)
                
                # Look for download links
                download_links = soup.find_all('a', href=re.compile(r'\.mp3', re.I))
                for link in download_links:
                    href = link.get('href')
                    if href:
                        if href.startswith('//'):
                            href = 'https:' + href
                        return self.normalize_url(href)
                
                # Look for embedded players and audio URLs in page content
                page_text = str(soup)
                
                # Method 1: Look for podtrac URLs directly in page text
                if 'dts.podtrac.com' in page_text:
                    start = page_text.find('//dts.podtrac.com')
                    if start != -1:
                        # Find end of URL
                        end_chars = ['"', "'", ' ', ')', '}', ']', '\n', '\r']
                        end = len(page_text)
                        
                        for char in end_chars:
                            pos = page_text.find(char, start)
                            if pos != -1 and pos < end:
                                end = pos
                        
                        url = page_text[start:end]
                        if url.startswith('//'):
                            url = 'https:' + url
                        return url
                
                # Method 2: Look in scripts with regex
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        # Look for podtrac/libsyn URLs
                        patterns = [
                            r'//dts\.podtrac\.com/redirect\.mp3/[^"\'\\s]*\.mp3',
                            r'traffic\.libsyn\.com/[^"\'\\s]*\.mp3'
                        ]
                        
                        for pattern in patterns:
                            match = re.search(pattern, script.string)
                            if match:
                                url = match.group(0)
                                if url.startswith('//'):
                                    url = 'https:' + url
                                return url
        
        return None
