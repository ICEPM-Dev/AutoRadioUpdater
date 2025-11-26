import requests
import re
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class CaminoVidaScraper(BaseScraper):
    """
    Scraper para El Camino de la Vida - Reflexión para Hoy
    Extrae el episodio más reciente desde el embed de Subsplash en la página principal
    """
    
    def __init__(self, url=None, program_name=None):
        super().__init__(url or "https://www.elcaminodelavida.org/", program_name)
        self.program_name = program_name or "El Camino de la Vida"
    
    def get_episodes(self, url=None, max_episodes=5):
        """Obtiene el episodio más reciente desde la página principal"""
        print(f"\n🔍 Obteniendo episodio más reciente desde la página principal...")
        
        try:
            # Acceder a la página principal
            response = requests.get(
                "https://www.elcaminodelavida.org/",
                timeout=15,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            if response.status_code != 200:
                print(f"   ✗ Error HTTP {response.status_code}")
                return self._fallback_search(max_episodes)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Buscar el iframe de Subsplash con *recent
            iframe = soup.find('iframe', src=re.compile(r'subsplash\.com/\+011d/embed/mi/\*recent'))
            
            if not iframe:
                print(f"   ⚠ No se encontró el embed de Subsplash")
                return self._fallback_search(max_episodes)
            
            iframe_src = iframe.get('src')
            print(f"   ✓ Encontrado embed de Subsplash")
            
            # Acceder al contenido del iframe
            iframe_response = requests.get(
                iframe_src,
                timeout=15,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            
            if iframe_response.status_code != 200:
                print(f"   ⚠ No se pudo acceder al iframe")
                return self._fallback_search(max_episodes)
            
            # Buscar URLs de MP3 en el contenido del iframe
            mp3_pattern = r'https://[^\s"\'<>]+\.mp3'
            mp3_urls = re.findall(mp3_pattern, iframe_response.text)
            
            if mp3_urls:
                # Filtrar solo URLs de medios.elcaminodelavida.org
                valid_urls = [url for url in mp3_urls if 'elcaminodelavida' in url or 'subsplash' in url]
                
                if valid_urls:
                    print(f"   ✓ Encontrado audio: {valid_urls[0][:80]}...")
                    
                    # Extraer número de episodio del URL
                    rph_match = re.search(r'RPH(\d+)', valid_urls[0])
                    episode_num = rph_match.group(1) if rph_match else "reciente"
                    
                    return [{
                        "titulo": f"Reflexión para Hoy - RPH {episode_num}",
                        "audio_url": valid_urls[0],
                        "nombre_programa": self.program_name
                    }]
            
            print(f"   ⚠ No se encontró audio en el iframe")
            return self._fallback_search(max_episodes)
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return self._fallback_search(max_episodes)
    
    def _fallback_search(self, max_episodes):
        """
        Método de respaldo: Buscar directamente por construcción de URLs
        """
        print(f"   🔄 Usando búsqueda directa como respaldo...")
        
        from datetime import datetime
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.elcaminodelavida.org/'
        }
        
        # Probar múltiples meses
        current_month = datetime.now().month
        next_month = (current_month % 12) + 1
        prev_month = current_month - 1 if current_month > 1 else 12
        
        months_to_try = [
            str(next_month).zfill(2),
            str(current_month).zfill(2),
            str(prev_month).zfill(2),
        ]
        
        print(f"  📅 Buscando en meses: {', '.join(months_to_try)}")
        
        highest_episode = 0
        best_month = None
        start_episode = 4600
        
        # Buscar el episodio más alto
        for month in months_to_try:
            for i in range(100):
                episode_num = start_episode - i
                url_mp3 = f"https://medios.elcaminodelavida.org/audio/WEB-RPH/WEB-RPH{month}/RPH{episode_num}-WEB.mp3"
                
                try:
                    response = requests.head(url_mp3, headers=headers, timeout=10, allow_redirects=True)
                    
                    if response.status_code == 200:
                        if episode_num > highest_episode:
                            highest_episode = episode_num
                            best_month = month
                        break
                        
                except Exception:
                    pass
        
        if highest_episode > 0:
            print(f"  ✓ Episodio más reciente: RPH {highest_episode} (mes {best_month})")
            
            episodes = []
            for i in range(max_episodes * 2):
                episode_num = highest_episode - i
                url_mp3 = f"https://medios.elcaminodelavida.org/audio/WEB-RPH/WEB-RPH{best_month}/RPH{episode_num}-WEB.mp3"
                
                try:
                    response = requests.head(url_mp3, headers=headers, timeout=5, allow_redirects=True)
                    
                    if response.status_code == 200:
                        episodes.append({
                            "titulo": f"Reflexión para Hoy - RPH {episode_num}",
                            "audio_url": url_mp3,
                            "nombre_programa": self.program_name
                        })
                        
                        if len(episodes) >= max_episodes:
                            break
                            
                except Exception:
                    pass
            
            return episodes
        
        print(f"  ✗ No se encontraron episodios")
        return []
    
    def get_audio_url(self, episode_data):
        """Retorna la URL de audio directamente"""
        return episode_data.get("audio_url")