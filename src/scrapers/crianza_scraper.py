import re
from typing import List, Dict
from .base_scraper import BaseScraper


class CrianzaReverenteScraper(BaseScraper):
    """Scraper for Crianza Reverente"""
    
    def __init__(self, base_url: str, program_name: str = None):
        super().__init__(base_url, program_name)
        # Add additional headers for Crianza Reverente to avoid 403
        self.session.headers.update({
            'Referer': 'https://crianzareverente.com/',
            'DNT': '1',
            'Sec-GPC': '1',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        })
    
    def get_episodes(self) -> List[Dict]:
        """Get episodes from Crianza Reverente website"""
        soup = self.get_page_content(self.base_url)
        if not soup:
            return []
        
        episodes = []
        
        # Look for the pagination container with episodes
        pagination_container = soup.find('div', class_='et_pb_ajax_pagination_container')
        
        if pagination_container:
            # Find all article elements (podcast episodes)
            articles = pagination_container.find_all('article', class_=re.compile(r'type-podcast'))
        else:
            # Fallback: look for articles directly
            articles = soup.find_all('article', class_=re.compile(r'type-podcast'))
        
        for article in articles:
            # Get title from the article
            title_element = article.find(['h1', 'h2', 'h3', 'h4'])
            title = title_element.text.strip() if title_element else None
            
            # Look for audio element with source
            audio_element = article.find('audio')
            if audio_element:
                source = audio_element.find('source')
                if source:
                    src = source.get('src')
                    # Handle both .mp3 and .m4a files
                    if src and ('.mp3' in src or '.m4a' in src or '.wav' in src):
                        if title:
                            episodes.append({
                                "titulo": title,
                                "audio_url": self.normalize_url(src),
                                "nombre_programa": self.program_name
                            })
        
        # If no episodes found, try alternative structure
        if not episodes:
            # Look for podcast or episode sections
            episode_sections = soup.find_all(['div', 'article', 'section'], class_=re.compile(r'(episode|podcast|post|crianza)', re.I))
            
            for section in episode_sections:
                title_element = section.find(['h1', 'h2', 'h3', 'h4'])
                title = title_element.text.strip() if title_element else None
                
                # Look for audio elements
                audio_element = section.find('audio')
                if audio_element:
                    src = audio_element.get('src')
                    if not src:
                        source = audio_element.find('source')
                        if source:
                            src = source.get('src')
                    
                    if src and title:
                        episodes.append({
                            "titulo": title,
                            "audio_url": self.normalize_url(src),
                            "nombre_programa": self.program_name
                        })
                
                # Look for direct audio links
                if not audio_element:
                    audio_link = section.find('a', href=re.compile(r'\.(mp3|wav|m4a)'))
                    if audio_link and title:
                        episodes.append({
                            "titulo": title,
                            "audio_url": self.normalize_url(audio_link['href']),
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
            soup = self.get_page_content(episode_data["escuchar_link"])
            if soup:
                # Look for audio elements
                audio = soup.find('audio')
                if audio:
                    src = audio.get('src')
                    if not src:
                        source = audio.find('source')
                        if source:
                            src = source.get('src')
                    if src:
                        return self.normalize_url(src)
                
                # Look for direct audio links
                audio_link = soup.find('a', href=re.compile(r'\.(mp3|wav|m4a)'))
                if audio_link:
                    return self.normalize_url(audio_link['href'])
        
        return None