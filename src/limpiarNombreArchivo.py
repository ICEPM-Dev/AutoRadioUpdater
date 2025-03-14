def limpiar_nombre_archivo(nombre):
    nombre_limpio = (
        nombre
        .replace('"', '')
        .replace(':', '')
        .replace('/', '_')
        .replace('\\', '_')
        .replace('?', '')
        .replace('<', '')
        .replace('>', '')
        .replace('|', '')
        .strip()
    )
    nombre_limpio = nombre_limpio.replace(' ', '_')
    return nombre_limpio
