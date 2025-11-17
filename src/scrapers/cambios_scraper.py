import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict
from .base_scraper import BaseScraper


class CambiosProfundosScraper(BaseScraper):
    """Scraper para Cambios Profundos usando YouTube"""
    
    def __init__(self, url=None, program_name=None):
        super().__init__(url or "https://cambiosprofundos.com/devocionales-en-audio/", program_name)
        self.program_name = program_name or "Cambios Profundos"
        # Playlist de YouTube que mencionan en la página
        self.youtube_playlist_id = "PL0uPKz84O97MwC5LMBwdvMH67Xw60eD4R"
    
    def get_episodes(self, url=None, max_episodes=5) -> List[Dict]:
        """Obtiene el episodio del día actual desde la playlist de YouTube"""
        print(f"\n🔍 Buscando episodio del día en YouTube...")
        from datetime import datetime
        
        episodes = []
        
        try:
            # Calcular día del año (1-365/366)
            hoy = datetime.now()
            dia_del_anio = hoy.timetuple().tm_yday
            
            print(f"  📅 Día del año: {dia_del_anio}")
            print(f"  🔗 Accediendo al índice {dia_del_anio} de la playlist...")
            
            # Método 1: Intentar obtener el video desde la playlist
            video_id = self._get_video_from_playlist_index(dia_del_anio)
            
            if video_id:
                video_url_final = f"https://www.youtube.com/watch?v={video_id}"
                titulo = f"Un año de cambios: Día {dia_del_anio}"
                
                episodes.append({
                    "titulo": titulo,
                    "escuchar_link": video_url_final,
                    "video_id": video_id,
                    "nombre_programa": self.program_name
                })
                
                print(f"  ✓ Encontrado: {titulo}")
                print(f"  ✓ Video ID: {video_id}")
                print(f"  ✓ URL: {video_url_final}")
            else:
                print(f"  ✗ No se pudo obtener el video del día {dia_del_anio}")
                
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
        
        return episodes
    
    def _get_video_from_playlist_index(self, index: int) -> str:
        """Obtiene el video_id desde un índice específico de la playlist usando el truco de índice directo"""
        try:
            # SOLUCIÓN: Usar el parámetro &index= para ir directamente al video
            # YouTube redirigirá al video correcto
            direct_url = f"https://www.youtube.com/watch?v=dummyID&list={self.youtube_playlist_id}&index={index}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            }
            
            print(f"    Accediendo directamente al índice {index}...")
            response = requests.get(direct_url, headers=headers, timeout=30, allow_redirects=True)
            
            if response.status_code != 200:
                print(f"    Error: HTTP {response.status_code}")
                return None
            
            # La URL final contiene el video_id correcto
            final_url = response.url
            print(f"    URL final: {final_url[:80]}...")
            
            # Extraer video_id de la URL final
            video_match = re.search(r'[?&]v=([a-zA-Z0-9_-]{11})', final_url)
            if video_match:
                video_id = video_match.group(1)
                print(f"    Video ID extraído de URL: {video_id}")
                return video_id
            
            # Si no está en la URL, buscar en el contenido de la página
            page_text = response.text
            
            # Buscar el videoId actual en el HTML
            # Patrón 1: En la metadata
            video_pattern = r'"videoId":"([a-zA-Z0-9_-]{11})"'
            match = re.search(video_pattern, page_text)
            if match:
                video_id = match.group(1)
                print(f"    Video ID extraído del HTML: {video_id}")
                
                # Verificar que sea el video correcto verificando el título
                title_match = re.search(r'"title":"([^"]*?(?:Día|Day)\s*' + str(index) + r'[^"]*?)"', page_text, re.IGNORECASE)
                if title_match:
                    print(f"    ✓ Título verificado: {title_match.group(1)}")
                    return video_id
                else:
                    print(f"    Título encontrado, asumiendo correcto")
                    return video_id
            
            # Patrón 2: videoDetails
            video_details_match = re.search(r'"videoDetails":\s*\{[^}]*"videoId":\s*"([a-zA-Z0-9_-]{11})"', page_text)
            if video_details_match:
                video_id = video_details_match.group(1)
                print(f"    Video ID de videoDetails: {video_id}")
                return video_id
            
            print(f"    ✗ No se pudo extraer el video_id del índice {index}")
            return None
            
        except Exception as e:
            print(f"    ✗ Error obteniendo video de playlist: {e}")
            return None
    
    def _extract_video_ids_from_yt_data(self, data: dict) -> List[str]:
        """Extrae video IDs de la estructura de datos de YouTube"""
        video_ids = []
        
        try:
            # Navegar por la estructura de datos de YouTube
            contents = data.get('contents', {}).get('twoColumnBrowseResultsRenderer', {}).get('tabs', [])
            
            for tab in contents:
                tab_renderer = tab.get('tabRenderer', {})
                content = tab_renderer.get('content', {})
                section_list = content.get('sectionListRenderer', {})
                section_contents = section_list.get('contents', [])
                
                for section in section_contents:
                    item_section = section.get('itemSectionRenderer', {})
                    playlist_contents = item_section.get('contents', [])
                    
                    for playlist_item in playlist_contents:
                        playlist_renderer = playlist_item.get('playlistVideoListRenderer', {})
                        videos = playlist_renderer.get('contents', [])
                        
                        for video in videos:
                            video_renderer = video.get('playlistVideoRenderer', {})
                            video_id = video_renderer.get('videoId')
                            if video_id:
                                video_ids.append(video_id)
        except:
            pass
        
        return video_ids
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """
        Retorna la URL de YouTube para que descargarAudio.py la maneje con yt-dlp
        """
        video_url = episode_data.get("escuchar_link")
        
        if video_url:
            # Verificar que el video_id no sea "placeholder"
            video_id = episode_data.get("video_id")
            if video_id and video_id == "placeholder":
                print(f"⚠ ADVERTENCIA: El video_id es 'placeholder', esto indica un error")
                return None
            
            print(f"\n📺 Video de YouTube: {video_url}")
            return video_url
        
        return None