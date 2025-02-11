import os
import subprocess
import datetime

def descargar_fotos():
    home_dir = os.path.expanduser("~/nikon/fotos")
    fecha = datetime.datetime.now().strftime("%d%m%Y")
    ruta_destino = os.path.join(home_dir, fecha, datetime.datetime.now().strftime("%F"))
    os.makedirs(ruta_destino, exist_ok=True)
    
    print(f"Directorio destino: {ruta_destino}")
    
    # Matar procesos en conflicto
    subprocess.run(["killall", "PTPCamera"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["sudo", "pkill", "-f", "gvfs"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Sincronizar fecha con la cámara
    subprocess.run(["gphoto2", "--set-config", "datetime=now"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Descargar archivos de la cámara
    comando = [
        "gphoto2", "--get-all-files", "--skip-existing",
        "--filename", f"{ruta_destino}/%F/%:" 
    ]
    
    print("Descargando fotos...")
    subprocess.run(comando)
    print("Descarga completada.")

if __name__ == "__main__":
    descargar_fotos()
    
    # Llamar al script de sincronización de fotos
    import sincronizar_foto
    sincronizar_foto.copiar_id()
