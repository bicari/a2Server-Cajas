Add-Type -AssemblyName System.Windows.Forms

# Configuración de la ventana modal
$msgBoxInput = New-Object System.Windows.Forms.MessageBoxButtons
$msgBoxIcon = [System.Windows.Forms.MessageBoxIcon]::Exclamation

# Mostrar el mensaje en una ventana modal
$result = [System.Windows.Forms.MessageBox]::Show("Hemos detectado una desconexión de red, presione ACEPTAR, si desea entrar en modo contingencia", "Atención", $msgBoxInput::OKCancel, $msgBoxIcon)

# Devolver el resultado como código de salida (OK = 1, Cancel = 2)
exit $result
