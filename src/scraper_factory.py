from urllib.parse import urlparse
from typing import Dict, Type
from .scrapers import (
    BaseScraper,
    TWR360Scraper,
    SemillasScraper,
    SabiduriaInternacionalScraper,
    VisionParaVivirScraper,
    LigonierScraper,
    CaminoVidaScraper,
    CoalicionScraper,
    CrianzaReverenteScraper,
    CambiosProfundosScraper,
    TemasBiblicosScraper,
    GraciaScraper,
    CarlosRuizScraper,
    RSSFeedScraper,
    BibleProjectScraper
)


class ScraperFactory:
    """Factory class to create appropriate scrapers based on URL"""
    
    # Mapping of domains to scraper classes
    SCRAPER_MAPPING: Dict[str, Type[BaseScraper]] = {
        'twr360.org': TWR360Scraper,
        'www.twr360.org': TWR360Scraper,
        'semillasalaire.com.ar': SemillasScraper,
        'www.semillasalaire.com.ar': SemillasScraper,
        'sabiduriainternacional.org': SabiduriaInternacionalScraper,
        'www.sabiduriainternacional.org': SabiduriaInternacionalScraper,
        'visionparavivir.org': VisionParaVivirScraper,
        'www.visionparavivir.org': VisionParaVivirScraper,
        'es.ligonier.org': LigonierScraper,
        'ligonier.org': LigonierScraper,
        'www.ligonier.org': LigonierScraper,
        'elcaminodelavida.org': CaminoVidaScraper,
        'www.elcaminodelavida.org': CaminoVidaScraper,
        'coalicionporelevangelio.org': CoalicionScraper,
        'www.coalicionporelevangelio.org': CoalicionScraper,
        'crianzareverente.com': CrianzaReverenteScraper,
        'www.crianzareverente.com': CrianzaReverenteScraper,
        'cambiosprofundos.com': CambiosProfundosScraper,
        'www.cambiosprofundos.com': CambiosProfundosScraper,
        'shows.acast.com': TemasBiblicosScraper,
        'feeds.acast.com': TemasBiblicosScraper,
        'gracia.org': GraciaScraper,
        'www.gracia.org': GraciaScraper,
        'www.youtube.com': CarlosRuizScraper,
        'youtube.com': CarlosRuizScraper,
        'anchor.fm': RSSFeedScraper,
        'feeds.': RSSFeedScraper,
        'rss': RSSFeedScraper,
        'proyectobiblia.com': BibleProjectScraper,
    }
    
    # Program names mapping
    PROGRAM_NAMES = {
        'twr360.org': 'TWR360',
        'www.twr360.org': 'TWR360',
        'semillasalaire.com.ar': 'Semillas al Aire',
        'www.semillasalaire.com.ar': 'Semillas al Aire',
        'sabiduriainternacional.org': 'Sabiduría Internacional',
        'www.sabiduriainternacional.org': 'Sabiduría Internacional',
        'visionparavivir.org': 'Visión para Vivir',
        'www.visionparavivir.org': 'Visión para Vivir',
        'es.ligonier.org': 'Renovando tu Mente',
        'ligonier.org': 'Renovando tu Mente',
        'www.ligonier.org': 'Renovando tu Mente',
        'elcaminodelavida.org': 'El Camino de la Vida',
        'www.elcaminodelavida.org': 'El Camino de la Vida',
        'coalicionporelevangelio.org': 'Coalición por el Evangelio',
        'www.coalicionporelevangelio.org': 'Coalición por el Evangelio',
        'crianzareverente.com': 'Crianza Reverente',
        'www.crianzareverente.com': 'Crianza Reverente',
        'cambiosprofundos.com': 'Cambios Profundos',
        'www.cambiosprofundos.com': 'Cambios Profundos',
        'shows.acast.com': 'Temas Bíblicos',
        'feeds.acast.com': 'Temas Bíblicos',
        'gracia.org': 'Gracia a Vosotros',
        'www.gracia.org': 'Gracia a Vosotros',
        'www.youtube.com': "Carlos Ruiz Devocionales",
        'youtube.com': "Carlos Ruiz Devocionales",
        'proyectobiblia.com': "Proyecto Biblia"
    }
    
    @classmethod
    def create_scraper(cls, url: str) -> BaseScraper:
        """Create appropriate scraper based on URL"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Remove 'www.' prefix for matching if present
        domain_without_www = domain.replace('www.', '') if domain.startswith('www.') else domain
        
        # Try exact match first
        scraper_class = cls.SCRAPER_MAPPING.get(domain)
        program_name = cls.PROGRAM_NAMES.get(domain)
        
        # Try without www prefix
        if not scraper_class:
            scraper_class = cls.SCRAPER_MAPPING.get(domain_without_www)
            program_name = cls.PROGRAM_NAMES.get(domain_without_www)
        
        # Try with www prefix
        if not scraper_class and not domain.startswith('www.'):
            www_domain = f'www.{domain}'
            scraper_class = cls.SCRAPER_MAPPING.get(www_domain)
            program_name = cls.PROGRAM_NAMES.get(www_domain)
        
        if scraper_class:
            return scraper_class(url, program_name)
        else:
            raise ValueError(f"No scraper available for domain: {domain}")
    
    @classmethod
    def get_supported_domains(cls) -> list:
        """Get list of supported domains"""
        return list(set(cls.SCRAPER_MAPPING.keys()))
    
    @classmethod
    def is_supported(cls, url: str) -> bool:
        """Check if URL is supported"""
        try:
            cls.create_scraper(url)
            return True
        except ValueError:
            return False
