#Lento pero funciona

import os
import shutil
import exiftool

# Rutas de Origen y Destino
Origen_nikon = "/home/redesiiucsa/fotos"
Destino_pi = "/home/redesiiucsa/original"

# Archivos de control
Contador_dir = "/home/logs"
Contador_id = os.path.join(Contador_dir, "contador.txt")
Procesados_id = os.path.join(Contador_dir, "procesados.txt")

# Crear carpetas si no existen
os.makedirs(Destino_pi, exist_ok=True)
os.makedirs(Contador_dir, exist_ok=True)

# Obtener el último ID usado
def get_ultimo_id():
    try:
        with open(Contador_id, "r") as f:
            contenido = f.read().strip()
            return int(contenido) if contenido.isdigit() else 0
    except FileNotFoundError:
        with open(Contador_id, "w") as f:
            f.write("0")
        return 0

# Guardar el nuevo ID
def guardar_id(ultimo_id):
    with open(Contador_id, "w") as f:
        f.write(str(ultimo_id))

# Leer lista de archivos ya procesados
def cargar_procesados():
    procesados = {}
    try:
        with open(Procesados_id, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    nombre, fecha_creacion = line.split(',')
                    procesados[nombre] = fecha_creacion
                except ValueError:
                    print(f"⚠ Línea malformada en {Procesados_id}: {line}, ignorando...")
    except FileNotFoundError:
        pass
    return procesados

# Guardar archivo procesado con fecha de captura
def guardar_procesado(nombre_archivo, fecha_creacion):
    with open(Procesados_id, "a") as f:
        f.write(f"{nombre_archivo},{fecha_creacion}\n")

# Obtener la fecha de captura desde EXIF con exiftool
def get_fecha_exif(ruta_archivo):
    try:
        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata([ruta_archivo])
            if metadata and metadata[0]:
                d = metadata[0]
                if "EXIF:DateTimeOriginal" in d:
                    return d["EXIF:DateTimeOriginal"]
                elif "File:CreateDate" in d:
                    return d["File:CreateDate"]
                else:
                    return None
            else:
                return None
    except exiftool.exceptions.ExifToolExecuteError as e:
        print(f"ExifTool Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# Copiar imágenes sin duplicados y comparar por metadatos EXIF
def copiar_id():
    viejo_id = get_ultimo_id()
    procesados = cargar_procesados()

    print(f"Buscando imágenes en: {Origen_nikon}")
    print(f" Archivos ya procesados: {len(procesados)}")

    for root, _, files in os.walk(Origen_nikon):
        print(f"Explorando: {root}, Archivos encontrados: {len(files)}")

        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".JPG", ".JPEG")):
                src = os.path.join(root, file)
                fecha_creacion = get_fecha_exif(src)

                if fecha_creacion is None:
                    print(f"No se pudo obtener la fecha de {file}, ignorando...")
                    continue

                # Verificar si el archivo ya existe con la misma fecha de creación
                if file in procesados and procesados[file] == fecha_creacion:
                    print(f" {file} ya fue procesado, ignorando...")
                    continue

                viejo_id += 1
                dest_nombre = f"Arasunu_{viejo_id:03d}_{fecha_creacion.replace(':', '').replace(' ', '')}.jpg"
                dest = os.path.join(Destino_pi, dest_nombre)

                shutil.copy2(src, dest)
                print(f"Copiado: {dest}")

                guardar_procesado(file, fecha_creacion)
                guardar_id(viejo_id)

if __name__ == "__main__":
    copiar_id()