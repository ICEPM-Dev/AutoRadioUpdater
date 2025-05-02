import os
from datetime import datetime


def borrar_archivos_viejos(file_dir, dias_antiguedad=30):
    if not os.path.exists(file_dir):
        print(f"El directorio {file_dir} no existe.")
        return

    for root, _, files in os.walk(file_dir):
        for name in files:
            path = os.path.join(root, name)
            try:
                fecha_archivo = (datetime.now() - datetime.fromtimestamp(os.stat(path).st_ctime)).days
                print(fecha_archivo)
                if fecha_archivo > dias_antiguedad:
                    print(f"Eliminando: {path}")
                    os.remove(path)
            except Exception as e:
                print(f"Error con {path}: {e}")
