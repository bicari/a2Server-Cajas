import subprocess


def show_modal_window(path_script: str):
    # Ruta al script de PowerShell

    # Comando para ejecutar el script de PowerShell
    command = [r'powershell.exe', '-ExecutionPolicy', 'Unrestricted', '-File', path_script]

    try:
        # Ejecutar el comando de PowerShell
        result = subprocess.run(command, capture_output=True, text=True)

        # Capturar el código de salida del proceso
        return result.returncode
    
    except Exception as e:
        return "Error al ejecutar el script de PowerShell: {e}".format(e=e)

def show_message_powershell(path_script: str):
    print(f'Ejecutando script {path_script}')
    result=subprocess.run([r'powershell.exe', '-ExecutionPolicy', 'Unrestricted', '-File', path_script], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
    print(result.stderr, result.stdout, result.returncode)

