import re
import requests
from datetime import datetime, timedelta
from typing import List, Dict
from .base_scraper import BaseScraper

class SemillasScraper(BaseScraper):
    """Scraper for Semillas al Aire radio program"""
    
    def get_episodes(self) -> List[Dict]:
        """Get episodes from Semillas al Aire website"""
        
        # Estrategia 1: Scrapear la página principal
        print(f"   🔍 Buscando en la página principal...")
        soup = self.get_page_content(self.base_url)
        
        if soup:
            episodes = self._extract_from_page(soup)
            if episodes:
                # Verificar que el URL sea válido (no sea 'today.mp3')
                valid_episodes = [ep for ep in episodes if 'today.mp3' not in ep['audio_url']]
                if valid_episodes:
                    print(f"   ✓ Encontrado en página principal")
                    return valid_episodes
                else:
                    print(f"   ⚠ URL encontrado no es válido (today.mp3)")
        
        # Estrategia 2: Buscar en programas anteriores
        print(f"   🔍 Buscando en programas anteriores...")
        anterior_url = "https://www.semillasalaire.com.ar/programas-anteriores/"
        soup_anterior = self.get_page_content(anterior_url)
        
        if soup_anterior:
            episodes = self._extract_from_page(soup_anterior)
            if episodes:
                # Filtrar 'today.mp3' también aquí
                valid_episodes = [ep for ep in episodes if 'today.mp3' not in ep['audio_url']]
                if valid_episodes:
                    print(f"   ✓ Encontrado en programas anteriores")
                    return valid_episodes
        
        # Estrategia 3: Construir URLs por fecha
        print(f"   🔄 Construyendo URLs por fecha...")
        return self._build_urls_by_date()
    
    def _extract_from_page(self, soup) -> List[Dict]:
        """Intenta extraer episodios de la página"""
        episodes = []
        
        # Método 1: audio con data-audiopath
        audio_elements = soup.find_all('audio', attrs={'data-audiopath': True})
        for audio in audio_elements:
            src = audio.get('data-audiopath')
            if src and '.mp3' in src:
                url = self.normalize_url(src)
                
                # Extraer fecha del nombre del archivo si es posible
                date_match = re.search(r'(\d{4}[-_]?\d{2}[-_]?\d{2})', src)
                titulo = f"Programa {date_match.group(1)}" if date_match else "Programa del Día"
                
                episodes.append({
                    "titulo": titulo,
                    "audio_url": url,
                    "nombre_programa": self.program_name
                })
        
        # Método 2: cualquier elemento con data-audiopath
        if not episodes:
            elements = soup.find_all(attrs={'data-audiopath': True})
            for elem in elements:
                src = elem.get('data-audiopath')
                if src and '.mp3' in src:
                    url = self.normalize_url(src)
                    
                    date_match = re.search(r'(\d{4}[-_]?\d{2}[-_]?\d{2})', src)
                    titulo = f"Programa {date_match.group(1)}" if date_match else "Programa del Día"
                    
                    episodes.append({
                        "titulo": titulo,
                        "audio_url": url,
                        "nombre_programa": self.program_name
                    })
        
        # Método 3: tags de audio normales
        if not episodes:
            audio_tags = soup.find_all('audio')
            for audio in audio_tags:
                src = audio.get('src')
                if src and '.mp3' in src:
                    url = self.normalize_url(src)
                    
                    date_match = re.search(r'(\d{4}[-_]?\d{2}[-_]?\d{2})', src)
                    titulo = f"Programa {date_match.group(1)}" if date_match else "Programa del Día"
                    
                    episodes.append({
                        "titulo": titulo,
                        "audio_url": url,
                        "nombre_programa": self.program_name
                    })
        
        # Método 4: buscar URLs de MP3 en el HTML completo
        if not episodes:
            mp3_pattern = r'https?://[^\s"\'<>]+\.mp3'
            mp3_urls = re.findall(mp3_pattern, str(soup))
            
            # Filtrar URLs válidas (que contengan semillasalaire)
            valid_urls = [url for url in mp3_urls if 'semillasalaire' in url.lower()]
            
            if valid_urls:
                # Ordenar para obtener la más reciente (por fecha en el nombre)
                valid_urls.sort(reverse=True)
                
                # Tomar hasta 5 episodios únicos
                seen = set()
                for url in valid_urls:
                    if url not in seen and len(episodes) < 5:
                        seen.add(url)
                        
                        date_match = re.search(r'(\d{4}[-_]?\d{2}[-_]?\d{2})', url)
                        titulo = f"Programa {date_match.group(1)}" if date_match else "Programa"
                        
                        episodes.append({
                            "titulo": titulo,
                            "audio_url": url,
                            "nombre_programa": self.program_name
                        })
        
        # Método 5: buscar links a archivos MP3
        if not episodes:
            links = soup.find_all('a', href=re.compile(r'\.mp3'))
            for link in links:
                href = link.get('href')
                if href and '.mp3' in href:
                    url = self.normalize_url(href)
                    
                    # Obtener texto del link o del padre
                    title_text = link.get_text(strip=True)
                    if not title_text:
                        parent = link.find_parent(['div', 'span', 'p'])
                        if parent:
                            title_text = parent.get_text(strip=True)
                    
                    titulo = title_text[:50] if title_text else "Programa"
                    
                    episodes.append({
                        "titulo": titulo,
                        "audio_url": url,
                        "nombre_programa": self.program_name
                    })
        
        if episodes:
            print(f"   ✓ Encontrados {len(episodes)} episodios en la página")
        
        return episodes
    
    def _build_urls_by_date(self) -> List[Dict]:
        """Construye URLs basándose en fechas recientes"""
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        episodes = []
        today = datetime.now()
        
        # Probar diferentes formatos de fecha comunes
        date_formats = [
            lambda d: d.strftime('%Y-%m-%d'),           # 2024-11-26
            lambda d: d.strftime('%Y%m%d'),             # 20241126
            lambda d: d.strftime('%d-%m-%Y'),           # 26-11-2024
            lambda d: d.strftime('%d%m%Y'),             # 26112024
            lambda d: d.strftime('%Y_%m_%d'),           # 2024_11_26
            lambda d: d.strftime('%d_%m_%Y'),           # 26_11_2024
        ]
        
        # Patrones de URL comunes
        url_patterns = [
            'https://www.semillasalaire.com.ar/wp-content/uploads/programas/{date}.mp3',
            'https://www.semillasalaire.com.ar/wp-content/uploads/programas/programa-{date}.mp3',
            'https://www.semillasalaire.com.ar/wp-content/uploads/programas/semillas-{date}.mp3',
            'https://www.semillasalaire.com.ar/wp-content/uploads/{date}.mp3',
        ]
        
        # Probar últimos 7 días
        for days_back in range(7):
            date = today - timedelta(days=days_back)
            
            # Probar cada formato de fecha
            for date_format in date_formats:
                date_str = date_format(date)
                
                # Probar cada patrón de URL
                for pattern in url_patterns:
                    url = pattern.format(date=date_str)
                    
                    try:
                        response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
                        
                        if response.status_code == 200:
                            print(f"   ✓ Encontrado: {date.strftime('%d/%m/%Y')}")
                            episodes.append({
                                "titulo": f"Programa {date.strftime('%d/%m/%Y')}",
                                "audio_url": url,
                                "nombre_programa": self.program_name
                            })
                            return episodes  # Retornar el primero encontrado
                            
                    except Exception:
                        pass
        
        print(f"   ✗ No se encontraron episodios recientes")
        return episodes
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Extract audio URL - for this scraper, it's already in the episode data"""
        return episode_data.get("audio_url")