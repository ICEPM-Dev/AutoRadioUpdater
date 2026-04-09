import re
from typing import List, Dict
from .base_scraper import BaseScraper

# Feed RSS del podcast en rss.com
# El slug se obtiene de los links de episodios: rss.com/podcasts/sabiduria-para-el-corazon/...
RSS_FEED_URL = "https://media.rss.com/sabiduria-para-el-corazon/feed.xml"


class SabiduriaInternacionalScraper(BaseScraper):
    """Scraper for Sabiduría Internacional - Sabiduría para el Corazón
    
    El reproductor en la web es del servicio rss.com y carga el audio
    dinámicamente via JavaScript. No hay `podcastPlayerData` ni ningún
    <audio> tag en el HTML estático.
    
    Solución: leer el feed RSS directamente desde media.rss.com,
    que contiene las URLs de MP3 en los tags <enclosure>.
    """

    def __init__(self, base_url: str, program_name: str = None):
        super().__init__(base_url, program_name)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        })

    def get_episodes(self) -> List[Dict]:
        """Obtiene episodios desde el feed RSS de rss.com.
        
        El HTML de la página no contiene el audio — el reproductor es
        JavaScript dinámico de rss.com. El feed RSS sí tiene las URLs
        de los MP3 en los tags <enclosure>.
        """
        episodes = []

        try:
            import requests
            import xml.etree.ElementTree as ET

            response = requests.get(
                RSS_FEED_URL,
                headers=self.session.headers,
                timeout=30,
                allow_redirects=True,
            )

            if response.status_code != 200:
                print(f"[SabiduriaInternacional] Error fetching RSS: HTTP {response.status_code}")
                return episodes

            root = ET.fromstring(response.content)
            channel = root.find('channel')
            if channel is None:
                print("[SabiduriaInternacional] No se encontró <channel> en el RSS")
                return episodes

            items = channel.findall('item')

            for item in items[:5]:  # Limitar a los 5 más recientes
                title_el = item.find('title')
                title = title_el.text.strip() if title_el is not None else self.program_name

                # El MP3 viene en <enclosure url="..." type="audio/mpeg" />
                enclosure = item.find('enclosure')
                audio_url = None
                if enclosure is not None:
                    audio_url = enclosure.get('url')

                # Fallback: buscar en link del item
                link_el = item.find('link')
                episode_link = link_el.text.strip() if link_el is not None else None

                if audio_url:
                    if audio_url.startswith('//'):
                        audio_url = 'https:' + audio_url

                    episodes.append({
                        "titulo": title,
                        "audio_url": audio_url,
                        "escuchar_link": episode_link or audio_url,
                        "nombre_programa": self.program_name,
                    })
                else:
                    print(f"[SabiduriaInternacional] No se encontró enclosure para: {title}")

        except Exception as e:
            print(f"[SabiduriaInternacional] Error obteniendo episodios via RSS: {e}")

        return episodes

    def get_audio_url(self, episode_data: Dict) -> str:
        """Retorna la URL de audio ya extraída del RSS."""
        if "audio_url" in episode_data and episode_data["audio_url"]:
            return episode_data["audio_url"]
        return None