param(
  [string]$Destino = "./backups"
)

$origen = Join-Path $PSScriptRoot "../0.3 Desarrollo/instance"
New-Item -ItemType Directory -Force -Path $Destino | Out-Null
if (Test-Path $origen) {
  $marca = Get-Date -Format "yyyyMMdd-HHmmss"
  Copy-Item -Recurse -Force $origen (Join-Path $Destino "instance-$marca")
  Write-Output "Respaldo creado en $Destino"
} else {
  Write-Output "Aún no existe instance; ejecuta la aplicación primero."
}

