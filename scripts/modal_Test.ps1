# Cargar ensamblado necesario para usar Windows Forms
Add-Type -AssemblyName System.Windows.Forms

# Mostrar el mensaje en una ventana modal
$result = [System.Windows.Forms.MessageBox]::Show(
    "Se ha detectado una desconexión de red. Presione ACEPTAR para entrar en modo contingencia.",
    "ATENCIÓN",
    [System.Windows.Forms.MessageBoxButtons]::OK,
    [System.Windows.Forms.MessageBoxIcon]::Exclamation,
    [System.Windows.Forms.MessageBoxDefaultButton]::Button1,
    [System.Windows.Forms.MessageBoxOptions]::DefaultDesktopOnly
)

# Devolver el resultado como código de salida (OK = 1)
exit $result
