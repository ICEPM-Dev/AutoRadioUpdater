import re
import json
from typing import List, Dict
from datetime import datetime
from .base_scraper import BaseScraper


class VisionParaVivirScraper(BaseScraper):
    """Scraper mejorado para Visión para Vivir radio program"""
    
    def get_episodes(self) -> List[Dict]:
        """Get episodes from Visión para Vivir website"""
        episodes = []
        
        try:
            # Method 1: Try RSS feed (most reliable)
            rss_episodes = self._get_episodes_from_rss()
            if rss_episodes:
                return rss_episodes[:1]  # Limit to 5 most recent
            
            # Method 2: Try direct page scraping
            page_episodes = self._get_episodes_from_page()
            if page_episodes:
                return page_episodes[:1]
            
            # Method 3: Try constructing today's URL
            today_episode = self._try_todays_episode()
            if today_episode:
                episodes.append(today_episode)
                
        except Exception as e:
            print(f"Error getting Visión para Vivir episodes: {e}")
        
        return episodes
    
    def _get_episodes_from_rss(self) -> List[Dict]:
        """Get episodes from RSS feed"""
        episodes = []
        
        try:
            import feedparser
            
            rss_url = "https://visionparavivir.org/feed/"
            print(f"Intentando RSS: {rss_url}")
            
            feed = feedparser.parse(rss_url)
            
            if not feed.entries:
                print("No se encontraron entradas en el RSS")
                return episodes
            
            print(f"Encontradas {len(feed.entries)} entradas en RSS")
            
            for entry in feed.entries[:5]:
                title = entry.title if hasattr(entry, 'title') else "Programa del Día"
                
                # Look for audio enclosure in RSS
                audio_url = None
                if hasattr(entry, 'enclosures') and entry.enclosures:
                    for enclosure in entry.enclosures:
                        if hasattr(enclosure, 'type') and enclosure.type.startswith('audio/'):
                            audio_url = enclosure.href
                            print(f"Audio encontrado en RSS: {audio_url}")
                            break
                
                # If we have audio URL directly from RSS
                if audio_url:
                    episodes.append({
                        "titulo": title,
                        "audio_url": audio_url,
                        "nombre_programa": self.program_name
                    })
                # Otherwise, store the episode link for later processing
                elif hasattr(entry, 'link'):
                    episodes.append({
                        "titulo": title,
                        "escuchar_link": entry.link,
                        "nombre_programa": self.program_name
                    })
                    print(f"Episodio encontrado: {title} - {entry.link}")
                
        except ImportError:
            print("feedparser no está instalado. Instalar con: pip install feedparser")
        except Exception as e:
            print(f"Error parsing RSS feed: {e}")
        
        return episodes
    
    def _get_episodes_from_page(self) -> List[Dict]:
        """Get episodes from main page using Ember structure"""
        episodes = []
        
        try:
            soup = self.get_page_content(self.base_url)
            if not soup:
                return episodes
            
            # Look for ember divs with app-link-to class
            ember_links = soup.find_all('div', {
                'id': re.compile(r'ember\d+'), 
                'class': re.compile(r'app-link-to.*ember-view')
            })
            
            print(f"Encontrados {len(ember_links)} links Ember")
            
            for ember_div in ember_links:
                # Find the anchor tag inside
                link_element = ember_div.find('a', {
                    'id': re.compile(r'ember\d+'), 
                    'class': 'ember-view'
                })
                
                if link_element:
                    href = link_element.get('href')
                    if href:
                        # Construct full URL
                        if href.startswith('/'):
                            episode_url = f"https://visionparavivir.org{href}"
                        else:
                            episode_url = href
                        
                        # Extract title from nearby elements or from link text
                        title = link_element.get_text(strip=True)
                        if not title:
                            title_element = ember_div.find_parent().find(
                                ['h1', 'h2', 'h3', 'h4', 'span'], 
                                string=True
                            )
                            title = title_element.text.strip() if title_element else f"Programa {len(episodes) + 1}"
                        
                        print(f"Episodio encontrado: {title} - {episode_url}")
                        
                        episodes.append({
                            "titulo": title,
                            "escuchar_link": episode_url,
                            "nombre_programa": self.program_name
                        })
                
                # Limit to first 5
                if len(episodes) >= 5:
                    break
                    
        except Exception as e:
            print(f"Error scraping page: {e}")
        
        return episodes
    
    def _try_todays_episode(self) -> Dict:
        """Try to construct today's episode URL"""
        try:
            from datetime import datetime
            
            today = datetime.now()
            date_str = today.strftime('%Y-%m-%d')
            
            # Try constructing the MP3 URL directly
            # Pattern from your example: https://insightforliving.swncdn.com/International/VPV/NA/Media/MP3/VPV2025-11-14-Podcast.mp3
            audio_url = f'https://insightforliving.swncdn.com/International/VPV/NA/Media/MP3/VPV{date_str}-Podcast.mp3'
            
            # Verify if the URL exists
            import requests
            response = requests.head(audio_url, timeout=10)
            
            if response.status_code == 200:
                print(f"Audio de hoy encontrado: {audio_url}")
                return {
                    "titulo": f"Programa del día {today.strftime('%d/%m/%Y')}",
                    "audio_url": audio_url,
                    "nombre_programa": self.program_name
                }
                
        except Exception as e:
            print(f"No se pudo construir URL de hoy: {e}")
        
        return None
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Extract audio URL from episode data"""
        # If we already have the direct audio URL
        if "audio_url" in episode_data:
            return episode_data["audio_url"]
        
        # Visit the episode page to find download button
        if "escuchar_link" in episode_data:
            print(f"Accediendo a página de episodio: {episode_data['escuchar_link']}")
            
            soup = self.get_page_content(episode_data["escuchar_link"])
            if soup:
                # Method 1: Look for download links with specific attributes
                # <a href="..." download target="_blank">
                download_links = soup.find_all('a', {
                    'download': True,
                    'target': '_blank'
                })
                
                for link in download_links:
                    href = link.get('href')
                    if href and '.mp3' in href.lower():
                        print(f"Link de descarga encontrado: {href}")
                        return href
                
                # Method 2: Look for insightforliving MP3 URLs anywhere in the page
                page_text = str(soup)
                mp3_patterns = [
                    r'https?://insightforliving\.swncdn\.com[^"\s\']*\.mp3',
                    r'https?://[^"\s\']*swncdn\.com[^"\s\']*\.mp3',
                ]
                
                for pattern in mp3_patterns:
                    matches = re.findall(pattern, page_text)
                    if matches:
                        print(f"MP3 encontrado en página: {matches[0]}")
                        return matches[0]
                
                # Method 3: Look in script tags for audio URLs
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        mp3_match = re.search(r'https?://[^"\s\']*\.mp3', script.string)
                        if mp3_match:
                            url = mp3_match.group(0)
                            if 'insightforliving' in url or 'swncdn' in url:
                                print(f"MP3 encontrado en script: {url}")
                                return url
                
                # Method 4: Look for ember divs with download functionality
                ember_divs = soup.find_all('div', {'id': re.compile(r'ember\d+')})
                for ember_div in ember_divs:
                    download_link = ember_div.find('a', {
                        'href': re.compile(r'\.mp3'),
                        'download': True
                    })
                    if download_link:
                        href = download_link.get('href')
                        if href:
                            print(f"Link de descarga en Ember encontrado: {href}")
                            return href
                
                # Method 5: Try to extract date from page and construct URL
                audio_url = self._construct_audio_from_page(soup, episode_data["escuchar_link"])
                if audio_url:
                    return audio_url
        
        return None
    
    def _construct_audio_from_page(self, soup, episode_url: str) -> str:
        """Try to construct audio URL from page content"""
        try:
            import requests
            
            # Look for dates in various formats in the page
            page_text = str(soup)
            
            # Try to find dates in YYYY-MM-DD format
            date_matches = re.findall(r'20\d{2}-\d{1,2}-\d{1,2}', page_text)
            
            if date_matches:
                # Remove duplicates and sort by most recent
                unique_dates = sorted(set(date_matches), reverse=True)
                
                print(f"Fechas encontradas en la página: {unique_dates[:5]}")
                
                # Try the most recent dates
                for date_str in unique_dates[:5]:
                    # Construct the audio URL using the pattern
                    audio_url = f'https://insightforliving.swncdn.com/International/VPV/NA/Media/MP3/VPV{date_str}-Podcast.mp3'
                    
                    print(f"Verificando URL construida: {audio_url}")
                    
                    # Verify if the URL exists
                    try:
                        check_response = requests.head(audio_url, timeout=10)
                        if check_response.status_code == 200:
                            print(f"✓ URL válida encontrada: {audio_url}")
                            return audio_url
                        else:
                            print(f"✗ URL respondió con: {check_response.status_code}")
                    except Exception as e:
                        print(f"✗ Error al verificar URL: {e}")
                        continue
            
            # Fallback: Try today's date
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')
            audio_url = f'https://insightforliving.swncdn.com/International/VPV/NA/Media/MP3/VPV{today}-Podcast.mp3'
            
            print(f"Intentando URL de hoy: {audio_url}")
            
            try:
                check_response = requests.head(audio_url, timeout=10)
                if check_response.status_code == 200:
                    return audio_url
            except:
                pass
                
        except Exception as e:
            print(f"Error constructing audio URL: {e}")
        
        return None