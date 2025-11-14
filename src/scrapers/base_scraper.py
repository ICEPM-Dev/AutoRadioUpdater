from abc import ABC, abstractmethod
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


class BaseScraper(ABC):
    """Base class for radio program scrapers"""
    
    def __init__(self, base_url: str, program_name: str = None):
        self.base_url = base_url
        self.program_name = program_name or "Programa de Radio"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8,en-US;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        })
    
    def get_page_content(self, url: str) -> BeautifulSoup:
        """Get and parse page content"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            print(f"Error al acceder a la página {url}: {e}")
            return None
    
    @abstractmethod
    def get_episodes(self) -> List[Dict]:
        """Get list of episodes from the radio program website"""
        pass
    
    @abstractmethod
    def get_audio_url(self, episode_data: Dict) -> str:
        """Extract audio URL from episode data"""
        pass
    
    def normalize_url(self, url: str) -> str:
        """Normalize relative URLs to absolute URLs"""
        if url.startswith('http'):
            return url
        elif url.startswith('//'):
            return f"https:{url}"
        elif url.startswith('/'):
            return f"{self.base_url.rstrip('/')}{url}"
        else:
            return f"{self.base_url.rstrip('/')}/{url}"
