# AutoRadioUpdater
Programa que automaticamente actualiza el contenido de la radio

# Instalar
Primero debes crear el entorno virtual con el siguiente comando:
python -m venv .venv

Para activarlo escribe:
```sh
.\.venv\Scripts\activate
```

Por ultimo, para instalar las dependencias:
```sh
pip install -r .\requirements.txt
```

Para compilar el codigo en .exe, ejecuta el siguiente comando:
```sh
pyinstaller --onefile 'main.py'
```
