import re
import random
from typing import List, Dict
from .base_scraper import BaseScraper


class CoalicionScraper(BaseScraper):
    """Scraper for Coalición por el Evangelio - Podcasts"""
    
    def get_episodes(self) -> List[Dict]:
        """Get episodes from Coalición por el Evangelio RSS feed or page source"""
        
        # Detectar si es "Un Sermón Para Tu Semana"
        is_sermon_podcast = 'un-sermon-para-tu-semana' in self.base_url.lower()
        
        if is_sermon_podcast:
            print(f"   🎲 Modo aleatorio activado para sermones")
        
        # Estrategia 1: Intentar obtener desde el RSS feed
        rss_url = self._get_rss_url()
        
        if rss_url:
            print(f"   Intentando RSS feed: {rss_url}")
            
            try:
                response = self.session.get(rss_url, timeout=30)
                if response.status_code == 200:
                    episodes = self._parse_rss(response.text)
                    if episodes:
                        print(f"   ✓ Obtenidos {len(episodes)} episodios desde RSS")
                        
                        # Si es sermones, seleccionar uno aleatorio
                        if is_sermon_podcast and len(episodes) > 1:
                            selected = random.choice(episodes)
                            print(f"   🎲 Seleccionado aleatoriamente: {selected['titulo'][:60]}...")
                            return [selected]
                        
                        return episodes
            except Exception as e:
                print(f"   ⚠️  Error con RSS feed: {e}")
        
        # Estrategia 2: Buscar enlaces de MP3 directamente en el HTML
        print(f"   Intentando buscar MP3s directamente en la página...")
        
        try:
            response = self.session.get(self.base_url, timeout=30)
            html_content = response.text
            
            # Buscar todos los MP3 en la página
            mp3_patterns = [
                r'https://media\.blubrry\.com/[^"\'<>\s]+\.mp3',
                r'https://media\.thegospelcoalition\.org/wp-content/uploads/sites/\d+/\d+/\d+/\d+/[^"\'<>\s]+\.mp3',
            ]
            
            found_mp3s = set()
            for pattern in mp3_patterns:
                matches = re.findall(pattern, html_content)
                found_mp3s.update(matches)
            
            if found_mp3s:
                print(f"   ✓ Encontrados {len(found_mp3s)} archivos MP3 en la página")
                
                episodes = []
                for i, mp3_url in enumerate(list(found_mp3s)[:20], 1):  # Limitar a 20
                    # Extraer título del nombre del archivo
                    filename = mp3_url.split('/')[-1].replace('.mp3', '')
                    title = filename.replace('-', ' ').replace('_', ' ').title()
                    
                    episodes.append({
                        "titulo": f"{title[:60]}",
                        "audio_url": mp3_url,
                        "nombre_programa": self.program_name
                    })
                
                # Si es sermones, seleccionar uno aleatorio
                if is_sermon_podcast and len(episodes) > 1:
                    selected = random.choice(episodes)
                    print(f"   🎲 Seleccionado aleatoriamente: {selected['titulo'][:60]}...")
                    return [selected]
                
                return episodes
        except Exception as e:
            print(f"   ✗ Error buscando MP3s: {e}")
        
        # Estrategia 3: Buscar enlaces a episodios individuales
        soup = self.get_page_content(self.base_url)
        if not soup:
            return []
        
        episodes = []
        
        # Buscar TODOS los enlaces que contengan el patrón del podcast
        podcast_slug = self.base_url.rstrip('/').split('/')[-1]
        all_links = soup.find_all('a', href=re.compile(f'/podcasts/{podcast_slug}/[^/]+/$'))
        
        seen_urls = set()
        for link in all_links:
            href = link.get('href')
            
            if not href or href in seen_urls:
                continue
            
            # Evitar el enlace base
            if href.endswith(f'/podcasts/{podcast_slug}/'):
                continue
            
            seen_urls.add(href)
            
            # Normalizar URL
            if not href.startswith('http'):
                href = f"https://www.coalicionporelevangelio.org{href}"
            
            # Intentar obtener título
            title = link.get_text(strip=True)
            
            if not title or len(title) < 5:
                parent = link.find_parent(['div', 'article', 'header'])
                if parent:
                    heading = parent.find(['h1', 'h2', 'h3', 'h4', 'h5'])
                    if heading:
                        title = heading.get_text(strip=True)
            
            if not title or len(title) < 5:
                slug = href.split('/')[-2]
                title = slug.replace('-', ' ').title()
            
            episodes.append({
                "titulo": title,
                "escuchar_link": href,
                "nombre_programa": self.program_name
            })
            
            if len(episodes) >= 20:  # Limitar a 20
                break
        
        if episodes:
            print(f"   ✓ Encontrados {len(episodes)} enlaces a episodios")
            
            # Si es sermones, seleccionar uno aleatorio
            if is_sermon_podcast and len(episodes) > 1:
                selected = random.choice(episodes)
                print(f"   🎲 Seleccionado aleatoriamente: {selected['titulo'][:60]}...")
                return [selected]
        
        return episodes
    
    def _get_rss_url(self) -> str:
        """Determina la URL del RSS feed según el podcast"""
        if 'mujeres' in self.base_url.lower():
            return "https://www.coalicionporelevangelio.org/media/Mujeres_Podcast"
        elif 'un-sermon-para-tu-semana' in self.base_url.lower():
            return "https://www.coalicionporelevangelio.org/podcasts/un-sermon-para-tu-semana-podcast/feed/?feed=podcast"
        elif 'textos-fuera-de-contexto' in self.base_url.lower():
            return "https://feeds.simplecast.com/DEFv_nWf"
        elif 'para-ser-sinceras' in self.base_url.lower():
            return "https://feeds.simplecast.com/MXdXjs_d"
        elif 'piensa' in self.base_url.lower():
            return "https://www.coalicionporelevangelio.org/podcasts/piensa/feed/?feed=podcast"
        # Agregar más feeds según necesites
        return None
    
    def _parse_rss(self, rss_content: str) -> List[Dict]:
        """Parse RSS feed to get episodes"""
        from xml.etree import ElementTree as ET
        
        try:
            root = ET.fromstring(rss_content)
            episodes = []
            
            # Find all items in the feed
            for item in root.findall('.//item')[:30]:  # Limitar a 30 más recientes
                title_elem = item.find('title')
                enclosure = item.find('enclosure')
                
                if title_elem is not None and enclosure is not None:
                    title = title_elem.text
                    audio_url = enclosure.get('url')
                    
                    if audio_url and '.mp3' in audio_url.lower():
                        episodes.append({
                            "titulo": title,
                            "audio_url": audio_url,
                            "nombre_programa": self.program_name
                        })
            
            return episodes
        except Exception as e:
            print(f"   ✗ Error parseando RSS: {e}")
            return []
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Extract audio URL from episode data"""
        # Si ya tenemos la URL del audio, devolverla
        if "audio_url" in episode_data:
            return episode_data["audio_url"]
        
        # Si necesitamos visitar la página del episodio
        if "escuchar_link" in episode_data:
            try:
                response = self.session.get(episode_data["escuchar_link"], timeout=30)
                response.raise_for_status()
                html_content = response.text
            except Exception as e:
                print(f"   ✗ Error al obtener la página del episodio: {e}")
                return None
            
            # Buscar el MP3 con múltiples patrones
            patterns = [
                # Pattern 1: plyr_download con href
                r'class="[^"]*plyr_download[^"]*"[^>]+href="([^"]+\.mp3[^"]*)"',
                # Pattern 2: href con plyr_download
                r'href="([^"]+\.mp3[^"]*)"[^>]+class="[^"]*plyr_download[^"]*"',
                # Pattern 3: Blubrry directo
                r'https://media\.blubrry\.com/[^"\'<>\s]+\.mp3',
                # Pattern 4: TGC media directo
                r'https://media\.thegospelcoalition\.org/wp-content/uploads/sites/\d+/\d+/\d+/\d+/[^"\'<>\s]+\.mp3',
                # Pattern 5: Cualquier MP3 de TGC o Blubrry
                r'https://[^"\'<>\s]*(?:blubrry|thegospelcoalition)\.(?:com|org)[^"\'<>\s]+\.mp3',
                # Pattern 6: Download attribute
                r'<a[^>]+download[^>]*href="([^"]+\.mp3[^"]*)"',
                # Pattern 7: data-plyr download
                r'data-plyr="download"[^>]*href="([^"]+\.mp3[^"]*)"',
            ]
            
            for i, pattern in enumerate(patterns, 1):
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    url = match.group(1) if match.lastindex else match.group(0)
                    print(f"   ✓ Audio encontrado con pattern {i}: {url[:80]}...")
                    return url
            
            print(f"   ✗ No se encontró MP3 en la página del episodio")
        
        return None