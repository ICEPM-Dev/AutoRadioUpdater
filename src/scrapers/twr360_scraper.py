import re
from typing import List, Dict
from .base_scraper import BaseScraper


class TWR360Scraper(BaseScraper):
    """Scraper for TWR360 radio programs"""
    
    def get_episodes(self) -> List[Dict]:
        """Get episodes from TWR360 website"""
        soup = self.get_page_content(self.base_url)
        if not soup:
            return []
        
        episodes = []
        
        # Look for h1 tags with links to episodes
        h1_tags = soup.find_all("h1")
        for h1_tag in h1_tags:
            link_tag = h1_tag.find("a", href=True)
            if link_tag:
                title = link_tag.text.strip()
                episode_link = self.normalize_url(link_tag['href'])
                
                if title and '/programs/view/id,' in episode_link:
                    episodes.append({
                        "titulo": title,
                        "escuchar_link": episode_link,
                        "nombre_programa": self.program_name
                    })
        
        return episodes
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Extract audio URL from TWR360 episode page"""
        episode_url = episode_data["escuchar_link"]
        
        # First, get the episode page to find the "Escuchar" link
        soup = self.get_page_content(episode_url)
        if not soup:
            return None
        
        # Look for "Escuchar" link that leads to the audio page
        escuchar_links = soup.find_all('a', string=re.compile(r'Escuchar', re.I))
        audio_page_url = None
        
        for link in escuchar_links:
            href = link.get('href')
            if href and 'action,audio' in href:
                # For TWR360, we need to use the base domain, not the full ministry URL
                if href.startswith('/'):
                    audio_page_url = f"https://www.twr360.org{href}"
                else:
                    audio_page_url = self.normalize_url(href)
                break
        
        # If we found the audio page URL, go there to get the audio element
        if audio_page_url:
            audio_soup = self.get_page_content(audio_page_url)
            if audio_soup:
                # Look for audio element with src attribute
                audio_element = audio_soup.find('audio')
                if audio_element:
                    src = audio_element.get('src')
                    if src and '.mp3' in src:
                        return src
                    
                    # Check for source elements within audio
                    source = audio_element.find('source')
                    if source and source.get('src'):
                        src = source.get('src')
                        if '.mp3' in src:
                            return src
                
                # Look in script tags for audio URLs on the audio page
                for script in audio_soup.find_all("script"):
                    if script.string and '.mp3' in script.string:
                        # Look for the specific TWR360 pattern: src: 'URL'
                        src_match = re.search(r"src:\s*['\"]([^'\"]*\.mp3[^'\"]*)['\"]", script.string)
                        if src_match:
                            return src_match.group(1)
                        
                        # Fallback: Look for any MP3 URLs in scripts
                        mp3_match = re.search(r"['\"]https?://[^'\"]*\.mp3[^'\"]*['\"]", script.string)
                        if mp3_match:
                            return mp3_match.group(0).strip('\'"')
        
        # Fallback: Try to construct the audio URL directly from episode ID
        episode_id_match = re.search(r'/id,(\d+)/', episode_url)
        if episode_id_match:
            episode_id = episode_id_match.group(1)
            # Try the action,audio URL directly
            direct_audio_url = f"{episode_url.split('/programs/view')[0]}/programs/view/id,{episode_id}/action,audio/lang,2"
            audio_soup = self.get_page_content(direct_audio_url)
            if audio_soup:
                audio_element = audio_soup.find('audio')
                if audio_element and audio_element.get('src'):
                    src = audio_element.get('src')
                    if '.mp3' in src:
                        return src
        
        return None
