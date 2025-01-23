Add-Type -AssemblyName System.Windows.Forms

# Configuración de la ventana modal
$msgBoxInput = New-Object System.Windows.Forms.MessageBoxButtons
$msgBoxIcon = [System.Windows.Forms.MessageBoxIcon]::Exclamation
$form = New-Object System.Windows.Forms.Form
$form.Text = "Aviso"
$form.StartPosition = "CenterScreen"
$form.TopMost = $true  # Hacer que la ventana sea topmost
# Mostrar el mensaje en una ventana modal
[System.Windows.Forms.MessageBox]::Show($form,"Sistema en linea, presione ACEPTAR para conectarse al servidor", "AVISO", $msgBoxInput::OK, $msgBoxIcon)


