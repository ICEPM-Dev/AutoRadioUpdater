import re
from typing import List, Dict
from .base_scraper import BaseScraper


class CrianzaReverenteScraper(BaseScraper):
    """Scraper para Crianza Reverente - Bypass Cloudflare usando RSS/APIs"""
    
    def __init__(self, base_url: str, program_name: str = None):
        super().__init__(base_url, program_name)
        # URLs alternativas que NO tienen protección Cloudflare
        self.rss_feeds = [
            "https://feeds.buzzsprout.com/419753.rss",  # RSS principal de Buzzsprout
            "https://www.buzzsprout.com/419753.rss",
            "https://feeds.simplecast.com/crianzareverente",  # Alternativa Simplecast
        ]
    
    def get_episodes(self) -> List[Dict]:
        """Get episodes usando RSS feed en lugar del sitio web"""
        episodes = []
        
        print(f"\n🔍 Buscando episodios de Crianza Reverente...")
        print(f"   ⚠ Sitio web protegido por Cloudflare, usando RSS feeds...")
        
        # Method 1: Try RSS feeds (most reliable)
        rss_episodes = self._get_episodes_from_rss()
        if rss_episodes:
            print(f"   ✓ {len(rss_episodes)} episodios encontrados en RSS")
            return rss_episodes[:5]
        
        # Method 2: Try Apple Podcasts API (public)
        apple_episodes = self._get_episodes_from_apple_podcasts()
        if apple_episodes:
            print(f"   ✓ {len(apple_episodes)} episodios encontrados en Apple Podcasts")
            return apple_episodes[:5]
        
        # Method 3: Try Spotify API (if available)
        spotify_episodes = self._get_episodes_from_spotify()
        if spotify_episodes:
            print(f"   ✓ {len(spotify_episodes)} episodios encontrados en Spotify")
            return spotify_episodes[:5]
        
        print(f"   ✗ No se pudieron obtener episodios")
        return episodes
    
    def _get_episodes_from_rss(self) -> List[Dict]:
        """Get episodes from RSS feeds"""
        episodes = []
        
        try:
            import feedparser
            
            for rss_url in self.rss_feeds:
                try:
                    print(f"   🔄 Intentando RSS: {rss_url}")
                    feed = feedparser.parse(rss_url)
                    
                    if not feed.entries:
                        continue
                    
                    print(f"      ✓ Encontradas {len(feed.entries)} entradas")
                    
                    for entry in feed.entries[:5]:
                        title = entry.title if hasattr(entry, 'title') else "Crianza Reverente Podcast"
                        
                        # Look for audio enclosure
                        audio_url = None
                        if hasattr(entry, 'enclosures') and entry.enclosures:
                            for enclosure in entry.enclosures:
                                if hasattr(enclosure, 'type') and 'audio' in enclosure.type:
                                    audio_url = enclosure.href
                                    break
                        
                        # Also check for links in entry
                        if not audio_url and hasattr(entry, 'links'):
                            for link in entry.links:
                                if link.get('type', '').startswith('audio/'):
                                    audio_url = link.get('href')
                                    break
                        
                        if audio_url:
                            episodes.append({
                                "titulo": title,
                                "audio_url": audio_url,
                                "nombre_programa": self.program_name
                            })
                            print(f"      - {title[:50]}...")
                    
                    if episodes:
                        return episodes
                        
                except Exception as e:
                    print(f"      ✗ Error con {rss_url}: {e}")
                    continue
                    
        except ImportError:
            print("   ✗ feedparser no está instalado (pip install feedparser)")
        except Exception as e:
            print(f"   ✗ Error en RSS: {e}")
        
        return episodes
    
    def _get_episodes_from_apple_podcasts(self) -> List[Dict]:
        """Get episodes from Apple Podcasts lookup API"""
        episodes = []
        
        try:
            import requests
            import json
            
            # Buscar el podcast en iTunes Search API
            search_url = "https://itunes.apple.com/search"
            params = {
                'term': 'Crianza Reverente',
                'media': 'podcast',
                'limit': 1
            }
            
            print(f"   🔄 Buscando en Apple Podcasts...")
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('resultCount', 0) > 0:
                    podcast = data['results'][0]
                    feed_url = podcast.get('feedUrl')
                    
                    if feed_url:
                        print(f"      ✓ Feed encontrado: {feed_url}")
                        
                        # Parse the feed
                        import feedparser
                        feed = feedparser.parse(feed_url)
                        
                        for entry in feed.entries[:5]:
                            title = entry.title if hasattr(entry, 'title') else "Episodio"
                            
                            audio_url = None
                            if hasattr(entry, 'enclosures') and entry.enclosures:
                                for enclosure in entry.enclosures:
                                    if hasattr(enclosure, 'type') and 'audio' in enclosure.type:
                                        audio_url = enclosure.href
                                        break
                            
                            if audio_url:
                                episodes.append({
                                    "titulo": title,
                                    "audio_url": audio_url,
                                    "nombre_programa": self.program_name
                                })
                        
                        return episodes
                        
        except Exception as e:
            print(f"      ✗ Error con Apple Podcasts: {e}")
        
        return episodes
    
    def _get_episodes_from_spotify(self) -> List[Dict]:
        """Get episodes from Spotify (if accessible without auth)"""
        # Spotify requiere autenticación, pero podemos intentar buscar info pública
        # Por ahora, retornar vacío ya que necesitaría credenciales
        return []
    
    def _try_direct_cloudfront_access(self) -> List[Dict]:
        """
        Intentar construir URLs de CloudFront basándose en patrones conocidos.
        Los archivos de CloudFront generalmente NO tienen protección de Cloudflare.
        """
        episodes = []
        
        try:
            import requests
            from datetime import datetime, timedelta
            
            print(f"   🔄 Intentando acceso directo a CloudFront...")
            
            # Patrón observado: https://d3ctxlq1ktw2nl.cloudfront.net/staging/YYYY-M-D/ID-44100-2-HASH.m4a
            # Intentar con fechas recientes
            
            for days_ago in range(7):
                date = datetime.now() - timedelta(days=days_ago)
                year = date.year
                month = date.month
                day = date.day
                
                # Intentar diferentes IDs (los IDs parecen ser secuenciales)
                # Basado en tus ejemplos: 410598607, 410194025
                # Podríamos intentar IDs recientes
                
                # Por ahora, esto es especulativo sin más información
                # Se necesitaría más análisis de patrones
                pass
                
        except Exception as e:
            print(f"      ✗ Error: {e}")
        
        return episodes
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Extract audio URL from episode data"""
        # Si ya tenemos la URL directa del audio
        if "audio_url" in episode_data:
            audio_url = episode_data["audio_url"]
            
            # Verificar que sea una URL válida de CloudFront o Buzzsprout
            if 'cloudfront.net' in audio_url or 'buzzsprout.com' in audio_url:
                print(f"   ✓ URL de audio directa: {audio_url[:60]}...")
                return audio_url
        
        # Si no tenemos URL directa, no podemos acceder al sitio por Cloudflare
        print(f"   ✗ No se pudo obtener URL de audio (Cloudflare bloqueando acceso)")
        return None


# Alternativa: Scraper que usa cloudscraper para bypass Cloudflare
class CrianzaReverenteCloudscraperScraper(BaseScraper):
    """
    Scraper alternativo usando cloudscraper library para bypass Cloudflare.
    Requiere: pip install cloudscraper
    """
    
    def __init__(self, base_url: str, program_name: str = None):
        super().__init__(base_url, program_name)
        try:
            import cloudscraper
            self.scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                }
            )
            self.has_cloudscraper = True
        except ImportError:
            print("⚠ cloudscraper no está instalado. Instalar con: pip install cloudscraper")
            self.has_cloudscraper = False
    
    def get_episodes(self) -> List[Dict]:
        """Get episodes usando cloudscraper para bypass Cloudflare"""
        if not self.has_cloudscraper:
            print("   ✗ Usando fallback a RSS por falta de cloudscraper")
            fallback = CrianzaReverenteScraper(self.base_url, self.program_name)
            return fallback.get_episodes()
        
        episodes = []
        
        try:
            print(f"\n🔍 Accediendo a {self.base_url} con cloudscraper...")
            response = self.scraper.get(self.base_url, timeout=30)
            
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                print(f"   ✓ Página obtenida exitosamente")
                
                # Buscar elementos de podcast
                # Dependiendo de la estructura del sitio
                podcast_items = soup.find_all('article', class_=re.compile(r'podcast|post'))
                
                for item in podcast_items[:5]:
                    title_elem = item.find(['h1', 'h2', 'h3', 'h4'])
                    title = title_elem.text.strip() if title_elem else "Episodio"
                    
                    # Buscar audio element o enlace
                    audio_elem = item.find('audio')
                    if audio_elem:
                        src = audio_elem.get('src') or (audio_elem.find('source') and audio_elem.find('source').get('src'))
                        if src:
                            episodes.append({
                                "titulo": title,
                                "audio_url": src,
                                "nombre_programa": self.program_name
                            })
                
                if episodes:
                    print(f"   ✓ {len(episodes)} episodios encontrados")
                    return episodes
                    
            else:
                print(f"   ✗ Error HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Error con cloudscraper: {e}")
        
        # Fallback a RSS
        print("   🔄 Intentando fallback a RSS...")
        fallback = CrianzaReverenteScraper(self.base_url, self.program_name)
        return fallback.get_episodes()
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Extract audio URL from episode data"""
        return episode_data.get("audio_url")