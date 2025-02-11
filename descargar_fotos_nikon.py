import os
import subprocess
import datetime
import shutil

def descargar_fotos():
    home_dir = os.path.expanduser("~/nikon/fotos_teste")
    fecha = datetime.datetime.now().strftime("%d%m%Y")
    ruta_destino = os.path.join(home_dir, fecha)
    ruta_temp = os.path.join(home_dir, "temp")
    
    os.makedirs(ruta_destino, exist_ok=True)
    os.makedirs(ruta_temp, exist_ok=True)
    
    print(f"[{datetime.datetime.now()}] Directorio destino: {ruta_destino}")

    # Matar procesos en conflicto
    subprocess.run(["killall", "PTPCamera"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["sudo", "pkill", "-f", "gvfs"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Sincronizar fecha con la cámara
    subprocess.run(["gphoto2", "--set-config", "datetime=now"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    while True:  # Bucle infinito sin pausas
        print(f"[{datetime.datetime.now()}]  Buscando fotos nuevas...")
        
        # Descargar archivos a un directorio temporal
        resultado = subprocess.run(["gphoto2", "--get-all-files", "--filename", os.path.join(ruta_temp, "%f")], capture_output=True, text=True)
        
        if "No camera found" in resultado.stderr:
            print(f"[{datetime.datetime.now()}]  Cámara no encontrada. Esperando reconexión...")
            continue  # Vuelve a intentar inmediatamente
        
        print(f"[{datetime.datetime.now()}] Descarga completada en temporales.")

        # Mover solo archivos nuevos usando rsync
        print(f"[{datetime.datetime.now()}]  Moviendo fotos nuevas al destino final...")
        subprocess.run(["rsync", "-av", "--ignore-existing", f"{ruta_temp}/", f"{ruta_destino}/"])

        # Limpiar temporales después de mover
        shutil.rmtree(ruta_temp)
        os.makedirs(ruta_temp, exist_ok=True)
        
        print(f"[{datetime.datetime.now()}]  Proceso finalizado. Reiniciando ciclo...\n")

if __name__ == "__main__":
    descargar_fotos()
