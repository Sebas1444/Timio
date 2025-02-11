import os
import shutil
import exiftool
import time

# Rutas de Origen y Destino
Origen_nikon = "nikon/fotos_teste"
Destino_pi = "nikon/original"

# Archivos de control
Contador_dir = "/home/timio/nikon/logs"
Contador_id = os.path.join(Contador_dir, "contador.txt")
Procesados_id = os.path.join(Contador_dir, "procesados.txt")

# Crear carpetas si no existen
os.makedirs(Destino_pi, exist_ok=True)
os.makedirs(Contador_dir, exist_ok=True)

def get_ultimo_id():
    try:
        with open(Contador_id, "r") as f:
            contenido = f.read().strip()
            return int(contenido) if contenido.isdigit() else 0
    except FileNotFoundError:
        with open(Contador_id, "w") as f:
            f.write("0")
        return 0

def guardar_id(ultimo_id):
    with open(Contador_id, "w") as f:
        f.write(str(ultimo_id))

def cargar_procesados():
    procesados = set()
    try:
        with open(Procesados_id, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    procesados.add(line)
    except FileNotFoundError:
        pass
    return procesados

def guardar_procesado(identificador):
    with open(Procesados_id, "a") as f:
        f.write(f"{identificador}\n")

def get_fecha_exif(ruta_archivo):
    try:
        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata([ruta_archivo])
            if metadata and metadata[0]:
                d = metadata[0]
                return d.get("EXIF:DateTimeOriginal") or d.get("File:CreateDate")
            return None
    except exiftool.exceptions.ExifToolExecuteError as e:
        print(f"ExifTool Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

def copiar_id():
    while True:
        viejo_id = get_ultimo_id()
        procesados = cargar_procesados()

        print(f"Buscando imágenes en: {Origen_nikon}")
        print(f"Archivos ya procesados: {len(procesados)}")

        for root, _, files in os.walk(Origen_nikon):
            print(f" Explorando: {root}, Archivos encontrados: {len(files)}")

            for file in files:
                if file.lower().endswith((".jpg", ".jpeg")):
                    src = os.path.join(root, file)
                    fecha_creacion = get_fecha_exif(src)

                    if fecha_creacion is None:
                        print(f" No se pudo obtener la fecha de {file}, ignorando...")
                        continue

                    identificador = f"{file},{fecha_creacion}"
                    if identificador in procesados:
                        print(f" {file} ya fue procesado con la misma fecha, ignorando...")
                        continue

                    viejo_id += 1
                    dest_nombre = f"Arasunu_{viejo_id:03d}_{fecha_creacion.replace(':', '').replace(' ', '')}.jpg"
                    dest = os.path.join(Destino_pi, dest_nombre)

                    shutil.copy2(src, dest)
                    print(f" Copiado: {dest}")

                    procesados.add(identificador)
                    guardar_procesado(identificador)
                    guardar_id(viejo_id)
        
        time.sleep(2)  # Espera 2 segundos antes de volver a verificar

if __name__ == "__main__":
    copiar_id()
