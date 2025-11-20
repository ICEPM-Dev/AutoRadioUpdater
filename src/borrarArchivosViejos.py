import os
from datetime import datetime


def borrar_archivos_viejos(file_dir, dias_antiguedad):
    """
    Borra archivos más antiguos que dias_antiguedad
    
    Args:
        file_dir: Directorio donde buscar archivos
        dias_antiguedad: Número de días de antigüedad para borrar
        
    Returns:
        int: Número de archivos eliminados
    """
    if not os.path.exists(file_dir):
        print(f"El directorio {file_dir} no existe.")
        return 0
    
    archivos_eliminados = 0
    
    for root, _, files in os.walk(file_dir):
        for name in files:
            path = os.path.join(root, name)
            try:
                fecha_archivo = (datetime.now() - datetime.fromtimestamp(os.stat(path).st_ctime)).days
                
                if fecha_archivo > dias_antiguedad:
                    print(f"Eliminando: {path} ({fecha_archivo} días)")
                    os.remove(path)
                    archivos_eliminados += 1
            except Exception as e:
                print(f"Error con {path}: {e}")
    
    return archivos_eliminados