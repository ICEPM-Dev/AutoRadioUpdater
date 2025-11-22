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
    ahora = datetime.now()
    
    for root, _, files in os.walk(file_dir):
        for name in files:
            path = os.path.join(root, name)
            try:
                # Usar mtime (última modificación) en lugar de ctime (creación)
                # mtime es más confiable en todos los sistemas operativos
                file_mtime = datetime.fromtimestamp(os.stat(path).st_mtime)
                dias_desde_modificacion = (ahora - file_mtime).days
                
                if dias_desde_modificacion > dias_antiguedad:
                    print(f"Eliminando: {path} ({dias_desde_modificacion} días)")
                    os.remove(path)
                    archivos_eliminados += 1
                else:
                    # Debug: mostrar archivos que NO se eliminan
                    print(f"  Manteniendo: {name} ({dias_desde_modificacion} días)")
                    
            except Exception as e:
                print(f"Error con {path}: {e}")
    
    return archivos_eliminados