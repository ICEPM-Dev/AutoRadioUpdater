import os
from datetime import datetime


def borrar_archivos_viejos(file_dir):
    today = datetime.today()

    for root, dirs, files in os.walk(file_dir):
        for file in files:
            file_path = os.path.join(root, file)

            try:
                file_created_time = os.path.getctime(file_path)
                file_date = datetime.fromtimestamp(file_created_time)

                if file_date.month < today.month:
                    print(f"Eliminando: {file_path}")
                    os.remove(file_path)
            except Exception as e:
                print(f"Error con {file_path}: {e}")
