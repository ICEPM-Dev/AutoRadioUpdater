import requests
from bs4 import BeautifulSoup
import re
from .base_scraper import BaseScraper

class BibleProjectScraper(BaseScraper):
    """Scraper para Bible Project Español"""
    
    def __init__(self, url=None, program_name=None):
        super().__init__(url or "https://proyectobiblia.com/podcasts/bibleproject-espanol/", program_name)
        self.program_name = program_name or "Bible Project Español"
        
    def get_episodes(self, url=None, max_episodes=5):
        """Busca episodios en la página de podcasts"""
        
        print(f"\n🔍 Buscando episodios de Bible Project...")
        
        episodes = []
        
        try:
            response = requests.get(self.base_url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar todos los enlaces a episodios
            # Los episodios tienen URLs como /podcast/titulo-del-episodio/
            episode_links = soup.find_all('a', href=re.compile(r'/podcast/[^/]+/'))
            
            print(f"✓ Encontrados {len(episode_links)} enlaces a episodios")
            
            # Eliminar duplicados
            seen_urls = set()
            
            for link in episode_links:
                href = link.get('href')
                
                if not href or href in seen_urls:
                    continue
                
                seen_urls.add(href)
                
                # Normalizar URL
                if not href.startswith('http'):
                    href = 'https://proyectobiblia.com' + href
                
                # Obtener título
                title = link.get_text(strip=True)
                
                # Si el título está vacío, buscar en elementos cercanos
                if not title or len(title) < 3:
                    parent = link.find_parent(['div', 'article', 'section'])
                    if parent:
                        title_elem = parent.find(['h2', 'h3', 'h4', 'h5'])
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                
                if not title:
                    # Extraer del slug de la URL
                    slug = href.split('/')[-2]
                    title = slug.replace('-', ' ').title()
                
                episodes.append({
                    "titulo": title,
                    "escuchar_link": href,
                    "nombre_programa": self.program_name
                })
                
                print(f"  📝 {title}")
                
                if len(episodes) >= max_episodes:
                    break
        
        except Exception as e:
            print(f"✗ Error: {e}")
        
        return episodes
    
    def get_audio_url(self, episode_data):
        """Busca el link de descarga del MP3 en la página del episodio"""
        
        episode_url = episode_data.get("escuchar_link")
        if not episode_url:
            return None
        
        print(f"\n🔍 Buscando audio en: {episode_url}")
        
        try:
            response = requests.get(episode_url, timeout=30)
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = response.text
            
            # Método 1: Buscar enlaces de Simplecast directamente
            # Pattern: https://afp-*.simplecastaudio.com/.../*.mp3
            simplecast_pattern = r'https://[^"\s\'<>]*simplecastaudio\.com[^"\s\'<>]*\.mp3[^"\s\'<>]*'
            matches = re.findall(simplecast_pattern, page_text)
            
            if matches:
                # Tomar el primer match (suele ser el correcto)
                audio_url = matches[0]
                # Limpiar si tiene comillas o caracteres extra
                audio_url = audio_url.split('"')[0].split("'")[0].split('<')[0]
                print(f"✓ Audio encontrado (Simplecast): {audio_url[:80]}...")
                return audio_url
            
            # Método 2: Buscar en elementos <audio>
            audio_tag = soup.find('audio')
            if audio_tag:
                src = audio_tag.get('src')
                if not src:
                    source_tag = audio_tag.find('source')
                    if source_tag:
                        src = source_tag.get('src')
                
                if src and '.mp3' in src:
                    print(f"✓ Audio encontrado (audio tag): {src}")
                    return src
            
            # Método 3: Buscar enlaces con download attribute
            download_links = soup.find_all('a', download=True)
            for link in download_links:
                href = link.get('href')
                if href and '.mp3' in href:
                    print(f"✓ Audio encontrado (download link): {href}")
                    return href
            
            # Método 4: Buscar cualquier MP3 en la página
            mp3_pattern = r'https://[^"\s\'<>]+\.mp3[^"\s\'<>]*'
            mp3_matches = re.findall(mp3_pattern, page_text)
            
            for match in mp3_matches:
                # Limpiar
                match = match.split('"')[0].split("'")[0].split('<')[0]
                print(f"✓ Audio encontrado (MP3 en texto): {match[:80]}...")
                return match
            
            # Método 5: Buscar en scripts/iframes de Simplecast
            iframes = soup.find_all('iframe')
            for iframe in iframes:
                src = iframe.get('src', '')
                if 'simplecast' in src:
                    # Intentar extraer el ID del episodio
                    episode_id = re.search(r'episodes/([a-f0-9-]+)', src)
                    if episode_id:
                        print(f"  ℹ️ Encontrado iframe de Simplecast, pero necesita procesar...")
            
            print("✗ No se encontró URL de audio")
        
        except Exception as e:
            print(f"✗ Error: {e}")
        
        return None