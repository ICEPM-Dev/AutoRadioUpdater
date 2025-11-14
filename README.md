# AutoRadioUpdater
Programa que automáticamente descarga episodios de múltiples programas de radio cristianos.

## Características
- **Sistema genérico**: Soporta múltiples sitios web de radio
- **Configuración flexible**: Gestiona programas mediante archivo JSON o variables de entorno
- **Scrapers especializados**: Cada sitio web tiene su propio scraper optimizado
- **Limpieza automática**: Elimina archivos antiguos automáticamente
- **CLI de gestión**: Herramienta de línea de comandos para gestionar programas

## Sitios web soportados
- **TWR360** (twr360.org) - 13 programas diferentes incluyendo:
  - Abre la Biblia, Fundamentos del Discipulado
  - A Través de la Biblia, Aviva Nuestros Corazones
  - Correr para Ganar, El Amor que Vale, Gracia a Vosotros
  - Jungla Semántica, La Verdad en el Tubo de Ensayo
  - Momento Decisivo, Pedrito el Pulpo, Tierra Firme
  - Luis Palau Responde
- **Semillas al Aire** (semillasalaire.com.ar)
- **Sabiduría Internacional** (sabiduriainternacional.org)
- **Visión para Vivir** (visionparavivir.org)
- **Ligonier Ministries** (es.ligonier.org) - Renovando tu Mente
- **El Camino de la Vida** (elcaminodelavida.org)
- **La Biblia Dice** (labibliadice.org) - Una Pausa en tu Vida
- **Coalición por el Evangelio** (coalicionporelevangelio.org) - Podcasts
- **Crianza Reverente** (crianzareverente.com)
- **Cambios Profundos** (cambiosprofundos.com) - Devocionales en Audio

**Total: 22 programas de radio configurados**

## Instalación
1. Crear el entorno virtual:
```sh
python -m venv .venv
```

2. Activar el entorno virtual:
```sh
# En Windows
.\.venv\Scripts\activate

# En Linux/Mac
source .venv/bin/activate
```

3. Instalar las dependencias:
```sh
pip install -r requirements.txt
```

## Configuración

### Método 1: Archivo de configuración (Recomendado)
Los programas se configuran en `config/radio_programs.json`. Este archivo ya incluye todos los programas mencionados.

### Método 2: Variables de entorno
Copia `.env.example` a `.env` y configura las variables:
```sh
cp .env.example .env
```

## Uso

### Ejecutar el descargador
```sh
python main.py
```

### Gestionar programas con CLI
```sh
# Listar todos los programas
python manage_programs.py list

# Agregar un nuevo programa
python manage_programs.py add "Nombre del Programa" "https://ejemplo.com" --description "Descripción"

# Habilitar/deshabilitar programas
python manage_programs.py enable "Nombre del Programa"
python manage_programs.py disable "Nombre del Programa"

# Eliminar un programa
python manage_programs.py remove "Nombre del Programa"

# Ver dominios soportados
python manage_programs.py domains
```

## Estructura del proyecto
```
AutoRadioUpdater/
├── config/
│   └── radio_programs.json    # Configuración de programas
├── src/
│   ├── scrapers/              # Scrapers especializados
│   │   ├── base_scraper.py
│   │   ├── twr360_scraper.py
│   │   ├── semillas_scraper.py
│   │   └── ...
│   ├── config_manager.py      # Gestión de configuración
│   ├── programa_manager.py    # Gestor genérico de programas
│   ├── scraper_factory.py     # Factory para scrapers
│   └── ...
├── main.py                    # Programa principal
├── manage_programs.py         # CLI de gestión
└── .env.example              # Ejemplo de configuración
```

## Compilar a ejecutable
```sh
pyinstaller --onefile main.py
```
