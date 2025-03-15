import re

def limpiar_nombre_archivo(nombre):
    nombre_limpio = re.sub(r'[<>:"/\\?|*]', '', nombre)
    nombre_limpio = nombre_limpio.replace(' ', '_')

    return nombre_limpio.strip()
