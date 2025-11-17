import re
import subprocess
import json
from typing import List, Dict, Optional
from .base_scraper import BaseScraper


class YouTubeScraper(BaseScraper):
    """Base scraper for YouTube channels/playlists"""
    
    def __init__(self, base_url: str, program_name: str, max_duration_seconds: int = None):
        super().__init__(base_url, program_name)
        self.max_duration_seconds = max_duration_seconds
    
    def get_episodes(self) -> List[Dict]:
        """Get videos from YouTube channel or playlist"""
        print(f"   🎥 Obteniendo videos de YouTube...")
        
        videos = self._get_videos_with_ytdlp()
        
        if self.max_duration_seconds:
            # Filtrar por duración
            filtered = []
            for video in videos:
                duration = video.get('duration_seconds', 0)
                if duration > 0 and duration <= self.max_duration_seconds:
                    filtered.append(video)
            
            print(f"   ✓ {len(videos)} videos encontrados, {len(filtered)} filtrados por duración (≤{self.max_duration_seconds}s)")
            return filtered
        
        return videos
    
    def _get_videos_with_ytdlp(self) -> List[Dict]:
        """Use yt-dlp to get video list with metadata"""
        try:
            # Usar yt-dlp para obtener la lista de videos con metadatos
            cmd = [
                'yt-dlp',
                '--dump-json',
                '--flat-playlist',  # No descarga, solo lista
                '--playlist-end', '20',  # Limitar a los 20 más recientes
                '--no-warnings',
                self.base_url
            ]
            
            print(f"   🔄 Ejecutando yt-dlp...")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                print(f"   ✗ Error con yt-dlp: {result.stderr[:200]}")
                return []
            
            # Parsear cada línea como JSON (yt-dlp devuelve un JSON por línea)
            videos = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                try:
                    video_data = json.loads(line)
                    
                    # Extraer información relevante
                    video_id = video_data.get('id')
                    title = video_data.get('title', 'Sin título')
                    duration = int(video_data.get('duration', 0) or 0)  # Convertir a int
                    
                    if video_id:
                        video_url = f"https://www.youtube.com/watch?v={video_id}"
                        
                        videos.append({
                            "titulo": title,
                            "audio_url": video_url,  # yt-dlp lo manejará
                            "nombre_programa": self.program_name,
                            "duration_seconds": duration
                        })
                
                except json.JSONDecodeError:
                    continue
            
            return videos
            
        except subprocess.TimeoutExpired:
            print(f"   ✗ Timeout al ejecutar yt-dlp")
            return []
        except FileNotFoundError:
            print(f"   ✗ yt-dlp no está instalado")
            return []
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return []
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Return YouTube URL for yt-dlp to handle"""
        audio_url = episode_data.get("audio_url")
        
        if audio_url:
            duration = int(episode_data.get("duration_seconds", 0))
            minutes = duration // 60
            seconds = duration % 60
            print(f"📺 YouTube: {audio_url} ({minutes}:{seconds:02d})")
            return audio_url
        
        return None