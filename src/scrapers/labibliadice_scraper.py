import re
from typing import List, Dict
from .base_scraper import BaseScraper


class LaBibliaDiceScraper(BaseScraper):
    """Scraper for La Biblia Dice - Una Pausa en tu Vida"""
    
    def get_episodes(self) -> List[Dict]:
        """Get episodes from La Biblia Dice website"""
        soup = self.get_page_content(self.base_url)
        if not soup:
            return []
        
        episodes = []
        
        # Look for pause/episode sections
        pause_sections = soup.find_all(['div', 'section', 'article'], class_=re.compile(r'(pausa|episode|programa)', re.I))
        
        for section in pause_sections:
            title_element = section.find(['h1', 'h2', 'h3', 'h4'])
            title = title_element.text.strip() if title_element else None
            
            # Look for audio elements
            audio_element = section.find('audio')
            if audio_element:
                src = audio_element.get('src') or (audio_element.find('source') and audio_element.find('source').get('src'))
                if src and title:
                    episodes.append({
                        "titulo": title,
                        "audio_url": self.normalize_url(src),
                        "nombre_programa": self.program_name
                    })
            
            # Look for audio links
            audio_link = section.find('a', href=re.compile(r'\.(mp3|wav|m4a)'))
            if audio_link and title and not any(ep["titulo"] == title for ep in episodes):
                episodes.append({
                    "titulo": title,
                    "audio_url": self.normalize_url(audio_link['href']),
                    "nombre_programa": self.program_name
                })
            
            # Look for listen/play links
            listen_link = section.find('a', string=re.compile(r'(escuchar|reproducir|play)', re.I))
            if listen_link and title and not any(ep["titulo"] == title for ep in episodes):
                episodes.append({
                    "titulo": title,
                    "escuchar_link": self.normalize_url(listen_link['href']),
                    "nombre_programa": self.program_name
                })
        
        # Look for current pause or today's episode
        if not episodes:
            current_section = soup.find(['div', 'section'], string=re.compile(r'(actual|hoy|today|current)', re.I))
            if current_section:
                parent = current_section.find_parent()
                if parent:
                    audio = parent.find('audio') or parent.find('a', href=re.compile(r'\.(mp3|wav|m4a)'))
                    if audio:
                        src = audio.get('src') or audio.get('href')
                        if src:
                            episodes.append({
                                "titulo": "Una Pausa en tu Vida - Actual",
                                "audio_url": self.normalize_url(src),
                                "nombre_programa": self.program_name
                            })
        
        # Fallback: look for any audio content
        if not episodes:
            audio_elements = soup.find_all(['audio', 'source'])
            for i, audio in enumerate(audio_elements):
                src = audio.get('src')
                if src and ('.mp3' in src or '.wav' in src or '.m4a' in src):
                    episodes.append({
                        "titulo": f"Una Pausa en tu Vida {i+1}",
                        "audio_url": self.normalize_url(src),
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
                    src = audio.get('src') or (audio.find('source') and audio.find('source').get('src'))
                    if src:
                        return self.normalize_url(src)
                
                # Look for direct audio links
                audio_link = soup.find('a', href=re.compile(r'\.(mp3|wav|m4a)'))
                if audio_link:
                    return self.normalize_url(audio_link['href'])
        
        return None
