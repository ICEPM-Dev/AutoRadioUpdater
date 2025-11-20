import re
import requests
from typing import List, Dict
from datetime import datetime, timedelta
from .base_scraper import BaseScraper


class EnContactoScraper(BaseScraper):
    """Scraper para En Contacto Global - detecta automáticamente el episodio más reciente"""
    
    def get_episodes(self) -> List[Dict]:
        """Busca el episodio más reciente probando fechas inteligentemente"""
        print(f"\n🔍 Detectando episodio más reciente de En Contacto...")
        
        today = datetime.now()
        
        # Probar los últimos 10 días para encontrar el más reciente disponible
        for days_back in range(10):
            date = today - timedelta(days=days_back)
            date_str = date.strftime("%Y_%m_%d")
            date_display = date.strftime('%d/%m/%Y')
            
            print(f"  🔄 Probando {date_display}...", end=" ")
            
            # El código parece ser un contador incremental en hex
            # Estrategia: probar rangos amplios de códigos para esta fecha
            episode_found = self._try_find_episode_for_date(date_str, date_display)
            
            if episode_found:
                return [episode_found]
            else:
                print("✗")
        
        print(f"  ⚠ No se encontraron episodios en los últimos 10 días")
        return []
    
    def _try_find_episode_for_date(self, date_str: str, date_display: str) -> Dict:
        """
        Intenta encontrar el episodio para una fecha específica probando múltiples códigos.
        Usa búsqueda binaria inteligente en rangos hex.
        """
        # Rango aproximado de códigos hex (basado en patrón observado)
        # 8E100 = 581888 decimal
        # Incremento aproximado: ~1 por día
        
        # Calcular código base aproximado
        reference_date = datetime(2025, 11, 19)
        reference_hex = 0x8E10E  # 581902 decimal
        
        target_date = datetime.strptime(date_str, "%Y_%m_%d")
        days_diff = (target_date - reference_date).days
        
        estimated_code = reference_hex + days_diff
        
        # Probar en un rango de ±5 días del estimado
        for offset in range(-5, 6):
            code = estimated_code + offset
            hex_code = f"{code:X}"  # Convertir a hex
            
            audio_url = f"https://intouch.azureedge.net/spanish/pgm/ec_pgm_{date_str}_{hex_code}.mp3"
            
            try:
                response = requests.head(audio_url, timeout=3)
                if response.status_code == 200:
                    print(f"✓ (#{hex_code})")
                    return {
                        "titulo": f"En Contacto - {date_display}",
                        "audio_url": audio_url,
                        "fecha": date_display,
                        "codigo": hex_code,
                        "nombre_programa": self.program_name
                    }
            except:
                continue
        
        return None
    
    def get_audio_url(self, episode_data: Dict) -> str:
        """Retorna la URL de audio ya encontrada"""
        return episode_data.get("audio_url")