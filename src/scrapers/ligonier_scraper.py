import re
from typing import List, Dict
from .base_scraper import BaseScraper

# RSS feed URL para Renovando Tu Mente
RTM_RSS_URL = "https://renovandotumente.ligonier.org/rss"


class LigonierScraper(BaseScraper):
    """Scraper for Ligonier Ministries - Renovando tu Mente
    
    Usa el feed RSS en lugar de HTML scraping porque el reproductor de audio
    en la página se carga dinámicamente via JavaScript y no está en el HTML.
    El feed RSS contiene las URLs directas de los MP3 (via Libsyn).
    """

    def __init__(self, base_url: str, program_name: str = None):
        super().__init__(base_url, program_name)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
        })

    def get_episodes(self) -> List[Dict]:
        """Obtiene episodios desde el feed RSS de Ligonier (Libsyn).
        
        El HTML de cada episodio no contiene el audio directamente —
        el reproductor es JavaScript dinámico. El RSS sí tiene las URLs
        de los MP3 en los tags <enclosure>.
        """
        episodes = []

        try:
            import requests
            import xml.etree.ElementTree as ET

            response = requests.get(
                RTM_RSS_URL,
                headers=self.session.headers,
                timeout=30,
                allow_redirects=True,
            )

            if response.status_code != 200:
                print(f"Error fetching RSS: HTTP {response.status_code}")
                return episodes

            root = ET.fromstring(response.content)
            channel = root.find('channel')
            if channel is None:
                print("No se encontró <channel> en el RSS")
                return episodes

            items = channel.findall('item')

            for item in items[:5]:  # Limitar a los 5 más recientes
                title_el = item.find('title')
                title = title_el.text.strip() if title_el is not None else self.program_name

                # El MP3 viene en el tag <enclosure url="..." type="audio/mpeg" />
                enclosure = item.find('enclosure')
                audio_url = None
                if enclosure is not None:
                    audio_url = enclosure.get('url')

                # Fallback: buscar en <link> o en la descripción
                if not audio_url:
                    link_el = item.find('link')
                    episode_link = link_el.text.strip() if link_el is not None else None
                else:
                    link_el = item.find('link')
                    episode_link = link_el.text.strip() if link_el is not None else None

                if audio_url:
                    # Normalizar URL (fix protocol-relative)
                    if audio_url.startswith('//'):
                        audio_url = 'https:' + audio_url

                    episodes.append({
                        "titulo": title,
                        "audio_url": audio_url,
                        "escuchar_link": episode_link or audio_url,
                        "nombre_programa": self.program_name,
                    })
                else:
                    print(f"No se encontró enclosure MP3 para: {title}")

        except Exception as e:
            print(f"Error obteniendo episodios de Ligonier via RSS: {e}")

        return episodes

    def get_audio_url(self, episode_data: Dict) -> str:
        """Retorna la URL de audio ya extraída del RSS.
        
        Como get_episodes() ya extrae el MP3 directamente del feed RSS,
        no necesitamos visitar páginas adicionales.
        """
        # Si ya tenemos la URL de audio del RSS, la retornamos directamente
        if "audio_url" in episode_data and episode_data["audio_url"]:
            return episode_data["audio_url"]

        # Fallback por si se instanció con datos de otro origen
        if "escuchar_link" in episode_data:
            print(f"[Ligonier] audio_url no encontrada para '{episode_data.get('titulo')}', "
                  f"considera re-ejecutar get_episodes() para obtenerla del RSS.")

        return None