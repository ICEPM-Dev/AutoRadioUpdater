import os
from datetime import datetime


def borrar_archivos_viejos(file_dir):
    if not os.path.exists(file_dir):
        print(f"El directorio {file_dir} no existe.")
        return

    for entry in os.scandir(file_dir):
        if entry.is_file():
            try:
                file_date = datetime.fromtimestamp(entry.stat().st_ctime)
                if file_date.month < datetime.today().month:
                    print(f"Eliminando: {entry.path}")
                    os.remove(entry.path)
            except Exception as e:
                print(f"Error con {entry.path}: {e}")
