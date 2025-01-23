Add-Type -AssemblyName System.Windows.Forms

# Configuración de la ventana modal
$msgBoxInput = New-Object System.Windows.Forms.MessageBoxButtons
$msgBoxIcon = [System.Windows.Forms.MessageBoxIcon]::Exclamation
$form = New-Object System.Windows.Forms.Form
$form.Text = "Aviso"
$form.StartPosition = "CenterScreen"
$form.TopMost = $true  # Hacer que la ventana sea topmost
# Mostrar el mensaje en una ventana modal
$result = [System.Windows.Forms.MessageBox]::Show($form,"Se ha detectado una desconexión de red presione ACEPTAR para entrar en modo contingencia", "ATENCIÓN", $msgBoxInput::OK, $msgBoxIcon)

# Devolver el resultado como código de salida (OK = 1, Cancel = 2)
exit $result
