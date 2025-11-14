import re
from typing import List, Dict
from .base_scraper import BaseScraper


class CaminoVidaScraper(BaseScraper):
    """Scraper mejorado para El Camino de la Vida radio program"""
    
    def get_episodes(self) -> List[Dict]:
        """Get episodes from El Camino de la Vida website"""
        episodes = []
        
        try:
            # Method 1: Try RSS feed (most reliable)
            rss_episodes = self._get_episodes_from_rss()
            if rss_episodes:
                print(f"✓ Encontrados {len(rss_episodes)} episodios en RSS")
                return rss_episodes[:5]
            
            # Method 2: Try Ember structure on main page
            ember_episodes = self._get_episodes_from_ember()
            if ember_episodes:
                print(f"✓ Encontrados {len(ember_episodes)} episodios en estructura Ember")
                return ember_episodes[:5]
            
            # Method 3: Try constructing URLs from recent dates
            constructed_episodes = self._construct_recent_episodes()
            if constructed_episodes:
                print(f"✓ Construidos {len(constructed_episodes)} episodios recientes")
                return constructed_episodes[:5]
                
        except Exception as e:
            print(f"Error getting episodes from El Camino de la Vida: {e}")
        
        return episodes
    
    def _get_episodes_from_rss(self) -> List[Dict]:
        """Get episodes from RSS feed"""
        episodes = []
        
        try:
            import feedparser
            
            rss_url = "https://www.elcaminodelavida.org/reflexion-para-hoy/"
            print(f"Intentando RSS: {rss_url}")
            
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                print("No se encontraron entradas en el RSS")
                return episodes
            
            for entry in feed.entries[:5]:
                title = entry.title if hasattr(entry, 'title') else "Reflexión para hoy"
                
                # Try to get audio URL from enclosures
                audio_url = None
                if hasattr(entry, 'enclosures') and entry.enclosures:
                    for enclosure in entry.enclosures:
                        if hasattr(enclosure, 'type') and 'audio' in enclosure.type:
                            audio_url = enclosure.href
                            break
                
                if hasattr(entry, 'link'):
                    episode_data = {
                        "titulo": title,
                        "escuchar_link": entry.link,
                        "nombre_programa": self.program_name
                    }
                    
                    # If we have audio URL, add it
                    if audio_url:
                        episode_data["audio_url"] = audio_url
                    
                    episodes.append(episode_data)
                    print(f"  - {title}")
            
        except ImportError:
            print("feedparser no está instalado")
        except Exception as e:
            print(f"Error parsing RSS: {e}")
        
        return episodes
    
    def _get_episodes_from_ember(self) -> List[Dict]:
        """Get episodes from main page using Ember structure"""
        episodes = []
        
        try:
            soup = self.get_page_content(self.base_url)
            if not soup:
                return episodes
            
            # Look for ember divs that contain episode items
            ember_divs = soup.find_all('div', {
                'id': re.compile(r'ember\d+'), 
                'class': re.compile(r'kit-list-item.*ember-view')
            })
            
            print(f"Encontrados {len(ember_divs)} divs Ember")
            
            for ember_div in ember_divs:
                # Look for episode title
                title_element = ember_div.find(['h1', 'h2', 'h3', 'h4', 'span'], string=True)
                title = title_element.text.strip() if title_element else f"Episodio {len(episodes) + 1}"
                
                # Look for link
                link_element = ember_div.find('a', href=True)
                
                if link_element:
                    href = link_element.get('href')
                    if href:
                        episode_link = self.normalize_url(href)
                        
                        episodes.append({
                            "titulo": title,
                            "escuchar_link": episode_link,
                            "nombre_programa": self.program_name
                        })
                        print(f"  - {title}: {episode_link}")
                
                if len(episodes) >= 5:
                    break
                
        except Exception as e:
            print(f"Error scraping Ember structure: {e}")
        
        return episodes
    
    def _construct_recent_episodes(self) -> List[Dict]:
        """Construct URLs for recent episodes based on date patterns"""
        episodes = []
        
        try:
            from datetime import datetime, timedelta
            import requests
            
            # Try to construct URLs for the last 7 days
            for i in range(7):
                date = datetime.now() - timedelta(days=i)
                year = date.strftime('%Y')
                month = date.strftime('%m')
                day = date.strftime('%d')
                
                # Try different URL patterns
                url_patterns = [
                    f"https://www.elcaminodelavida.org/{year}/{month}/{day}/",
                    f"https://www.elcaminodelavida.org/reflexion/{year}/{month}/{day}/",
                ]
                
                for url in url_patterns:
                    try:
                        response = requests.head(url, timeout=5)
                        if response.status_code == 200:
                            episodes.append({
                                "titulo": f"Reflexión del {date.strftime('%d/%m/%Y')}",
                                "escuchar_link": url,
                                "nombre_programa": self.program_name
                            })
                            print(f"  - URL válida: {url}")
                            break
                    except:
                        continue
                
                if len(episodes) >= 5:
                    break
                    
        except Exception as e:
            print(f"Error constructing URLs: {e}")
        
        return episodes
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Extract audio URL from episode data with aggressive search"""
        # If we already have the direct audio URL
        if "audio_url" in episode_data:
            return episode_data["audio_url"]
        
        # Visit the episode page
        if "escuchar_link" in episode_data:
            print(f"\n🔍 Analizando episodio: {episode_data['titulo']}")
            print(f"   URL: {episode_data['escuchar_link']}")
            
            soup = self.get_page_content(episode_data["escuchar_link"])
            if soup:
                page_text = str(soup)
                
                # Method 1: Look for download button/link
                # <a href="..." download>Descargar</a>
                download_links = soup.find_all('a', {
                    'download': True
                })
                
                for link in download_links:
                    href = link.get('href')
                    if href and '.mp3' in href.lower():
                        print(f"   ✓ Botón de descarga encontrado: {href}")
                        return self.normalize_url(href)
                
                # Method 2: Direct search for medios.elcaminodelavida.org URLs in page text
                audio_patterns = [
                    r'https?://medios\.elcaminodelavida\.org/[^"\s\']*\.mp3',
                    r'https?://[^"\s\']*elcaminodelavida[^"\s\']*\.mp3',
                ]
                
                for pattern in audio_patterns:
                    matches = re.findall(pattern, page_text)
                    if matches:
                        print(f"   ✓ MP3 encontrado en página: {matches[0]}")
                        return matches[0]
                
                # Method 3: Look for audio elements
                audio_elements = soup.find_all('audio')
                for audio in audio_elements:
                    src = audio.get('src')
                    if src and '.mp3' in src:
                        print(f"   ✓ Audio element encontrado: {src}")
                        return self.normalize_url(src)
                    
                    # Check source elements
                    sources = audio.find_all('source')
                    for source in sources:
                        src = source.get('src')
                        if src and '.mp3' in src:
                            print(f"   ✓ Source element encontrado: {src}")
                            return self.normalize_url(src)
                
                # Method 4: Look for links with download-related text
                download_text_links = soup.find_all('a', href=True, string=re.compile(r'(descargar|download|mp3)', re.I))
                for link in download_text_links:
                    href = link.get('href')
                    if href and '.mp3' in href:
                        print(f"   ✓ Link de descarga por texto: {href}")
                        return self.normalize_url(href)
                
                # Method 5: Look in script tags
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        mp3_match = re.search(r'https?://[^"\']*elcaminodelavida[^"\']*\.mp3', script.string)
                        if mp3_match:
                            url = mp3_match.group(0)
                            print(f"   ✓ MP3 en script: {url}")
                            return url
                
                # Method 6: Try to construct audio URL from episode pattern
                print("   ⚠ Intentando construir URL desde patrón...")
                constructed_url = self._construct_audio_url_from_episode(episode_data["escuchar_link"])
                if constructed_url:
                    return constructed_url
        
        print("   ✗ No se pudo encontrar URL de audio")
        return None
    
    def _construct_audio_url_from_episode(self, episode_url: str) -> str:
        """Try to construct audio URL from episode URL pattern"""
        try:
            import requests
            
            # Pattern 1: Extract numeric ID
            # Example: https://www.elcaminodelavida.org/2025/04/2836/
            date_match = re.search(r'/(\d{4})/(\d{1,2})/(\d+)/', episode_url)
            
            if date_match:
                year, month, episode_id = date_match.groups()
                month_padded = month.zfill(2)
                
                print(f"   📅 Fecha extraída: {year}/{month_padded}, ID: {episode_id}")
                
                # Try different URL patterns based on working example
                patterns = [
                    # Working pattern from your code
                    f"https://medios.elcaminodelavida.org/audio/WEB-RPH/WEB-RPH{month_padded}/RPH{episode_id}-WEB.mp3",
                    # Alternative patterns
                    f"https://medios.elcaminodelavida.org/audio/WEB-RPH/WEB-RPH{month_padded}/RPH{episode_id}.mp3",
                    f"https://medios.elcaminodelavida.org/audio/{year}/{month_padded}/RPH{episode_id}-WEB.mp3",
                    f"https://medios.elcaminodelavida.org/audio/{year}/{month_padded}/RPH{episode_id}.mp3",
                    f"https://medios.elcaminodelavida.org/programas/RPH{episode_id}.mp3",
                ]
                
                for i, url in enumerate(patterns, 1):
                    print(f"   🔄 Probando patrón {i}: {url}")
                    try:
                        response = requests.head(url, timeout=10)
                        if response.status_code == 200:
                            print(f"   ✓ Patrón {i} exitoso!")
                            return url
                        else:
                            print(f"   ✗ Patrón {i} falló: HTTP {response.status_code}")
                    except Exception as e:
                        print(f"   ✗ Patrón {i} error: {str(e)[:50]}")
                        continue
                
                # Return the most likely pattern even if verification fails
                most_likely = patterns[0]
                print(f"   ⚠ Usando patrón más probable: {most_likely}")
                return most_likely
            
            # Pattern 2: Extract slug
            slug_match = re.search(r'/(\d{4})/(\d{1,2})/([^/]+)/', episode_url)
            if slug_match:
                year, month, slug = slug_match.groups()
                month_padded = month.zfill(2)
                
                print(f"   📝 Slug extraído: {slug}")
                
                slug_patterns = [
                    f"https://medios.elcaminodelavida.org/audio/WEB-RPH/WEB-RPH{month_padded}/{slug}.mp3",
                    f"https://medios.elcaminodelavida.org/audio/{year}/{month_padded}/{slug}.mp3",
                ]
                
                for url in slug_patterns:
                    print(f"   🔄 Probando slug pattern: {url}")
                    try:
                        response = requests.head(url, timeout=10)
                        if response.status_code == 200:
                            print(f"   ✓ Slug pattern exitoso!")
                            return url
                    except:
                        continue
                        
        except Exception as e:
            print(f"   ✗ Error en construcción de URL: {e}")
        
        return None