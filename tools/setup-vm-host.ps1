#Requires -RunAsAdministrator
<#
  LokroOS VM-Host-Setup (Windows, EINMALIG als Administrator ausfuehren):
    1. Installiert Oracle VirtualBox via winget (falls fehlend)
    2. Laedt Kubuntu 24.04.5 LTS (Plasma-Basis fuer LokroOS) + prueft SHA256
    3. Erstellt die VM "LokroOS-Test" (8 GB RAM, 4 CPUs, 40 GB VDI, VMSVGA+3D, NAT)
    4. Startet die VM - danach in der VM: Kubuntu installieren, Snapshot,
       LokroOS-Provisionierung (siehe docs/INSTALL.md Abschnitt B).

  Gebrauch (elevated PowerShell):
    .\tools\setup-vm-host.ps1
    .\tools\setup-vm-host.ps1 -VmName "LokroOS-Test2" -MemoryMB 8192 -Cpus 4 -DiskGB 40
    .\tools\setup-vm-host.ps1 -Recreate   # vorhandene VM gleichen Namens neu aufbauen
    .\tools\setup-vm-host.ps1 -VmName "LokroOS-ISO-Test" -CustomIso "C:\Users\lokro\projekte\lokroos\iso\output\lokroos-0.4.0-amd64.iso"
       # eigene ISO einhaengen (z.B. LokroOS-Build) statt Kubuntu zu laden

  Idempotent: Vorhandenes (VirtualBox, ISO mit gueltiger Checksumme) wird uebersprungen.
  Hinweis: Datei bewusst nur ASCII (Umlaute als ae/oe/ue), damit PowerShell 5.1
  ohne BOM-Probleme laeuft.
#>
[CmdletBinding()]
param(
  [string]$VmName = "LokroOS-Test",
  [int]$MemoryMB = 8192,
  [int]$Cpus = 4,
  [int]$DiskGB = 40,
  [string]$IsoDir = (Join-Path $env:USERPROFILE "Downloads\ISO"),
  [string]$CustomIso = "",
  [switch]$Recreate
)

$ErrorActionPreference = "Stop"
$IsoBase = "https://cdimage.ubuntu.com/kubuntu/releases/24.04/release"
$IsoFile = "kubuntu-24.04.5-desktop-amd64.iso"
$IsoPath = Join-Path $IsoDir $IsoFile

function Write-Step($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }

# --- 0. Admin-Guard (durch #Requires abgedeckt, doppelt haelt besser) ---
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
  throw "Bitte in einer PowerShell MIT Administratorrechten starten."
}

# --- 1. VirtualBox ---
Write-Step "1/4 VirtualBox pruefen/installieren"
$vbox = Get-Command VBoxManage -ErrorAction SilentlyContinue
if (-not $vbox) {
  $vboxDefault = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
  if (Test-Path -LiteralPath $vboxDefault) { $vbox = @{ Source = $vboxDefault } }
}
if (-not $vbox) {
  Write-Host "VirtualBox fehlt - installiere via winget (dauert einige Minuten) ..."
  winget install --exact --id Oracle.VirtualBox --silent --accept-package-agreements --accept-source-agreements
  if ($LASTEXITCODE -ne 0) { throw "winget-Installation fehlgeschlagen (Exit $LASTEXITCODE)." }
  $env:Path += ";C:\Program Files\Oracle\VirtualBox"
}
$VBoxManage = (Get-Command VBoxManage -ErrorAction SilentlyContinue).Source
if (-not $VBoxManage) { $VBoxManage = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" }
& $VBoxManage --version
Write-Host "VBoxManage: $VBoxManage"

# --- 2. ISO-Download + SHA256-Pruefung (entfaellt bei -CustomIso) ---
if ($CustomIso -ne "") {
  if (-not (Test-Path -LiteralPath $CustomIso)) { throw "CustomIso nicht gefunden: $CustomIso" }
  $IsoPath = $CustomIso
  Write-Step "2/4 Eigenes ISO: $IsoPath (Download uebersprungen)"
} else {
Write-Step "2/4 Kubuntu-ISO (5,1 GB) pruefen/laden"
New-Item -ItemType Directory -Path $IsoDir -Force | Out-Null
function Get-WantHash {
  # Laedt SHA256SUMS als DATEI (Content-Property von Invoke-WebRequest ist je nach
  # Content-Type ein Byte-Array - deshalb nie direkt parsen) und matcht den Dateinamen
  # EXAKT (kein Substring: sonst treffen auch .torrent/.zsync-Zeilen).
  $sumFile = Join-Path $IsoDir "SHA256SUMS"
  Invoke-WebRequest -Uri "$IsoBase/SHA256SUMS" -OutFile $sumFile
  foreach ($line in (Get-Content -LiteralPath $sumFile)) {
    $parts = $line -split "\s+"
    if ($parts.Count -ge 2 -and $parts[-1].TrimStart("*") -eq $IsoFile) { return $parts[0].ToLower() }
  }
  throw "Dateiname $IsoFile nicht in SHA256SUMS gefunden (geprueft: $sumFile)."
}
$needDownload = $true
if (Test-Path -LiteralPath $IsoPath) {
  Write-Host "ISO vorhanden - pruefe Checksumme ..."
  $want = Get-WantHash
  $have = (Get-FileHash -LiteralPath $IsoPath -Algorithm SHA256).Hash.ToLower()
  if ($have -eq $want) { Write-Host "Checksumme OK - Download uebersprungen."; $needDownload = $false }
  else { Write-Warning "Checksumme falsch - lade erneut." }
}
if ($needDownload) {
  Write-Host "Lade $IsoFile (ca. 5,1 GB, fortsetzbar) ..."
  try {
    Start-BitsTransfer -Source "$IsoBase/$IsoFile" -Destination $IsoPath -Description "Kubuntu 24.04.5 ISO"
  } catch {
    Write-Warning "BITS fehlgeschlagen, Fallback Invoke-WebRequest ..."
    Invoke-WebRequest -Uri "$IsoBase/$IsoFile" -OutFile $IsoPath
  }
  $want = Get-WantHash
  $have = (Get-FileHash -LiteralPath $IsoPath -Algorithm SHA256).Hash.ToLower()
  if ($have -ne $want) { throw "SHA256 mismatch! Datei ggf. beschaedigt: $IsoPath" }
  Write-Host "Checksumme OK."
}
} # Ende else (Kubuntu-Download); bei -CustomIso entfaellt Abschnitt 2

# --- 3. VM erstellen (idempotent) ---
Write-Step "3/4 VM $VmName erstellen"
$existing = & $VBoxManage list vms | Select-String -Pattern "`"$VmName`""
if ($existing) {
  if ($Recreate) {
    Write-Warning "VM existiert - wird geloescht und neu erstellt."
    & $VBoxManage unregistervm $VmName --delete
  } else {
    Write-Host "VM existiert bereits - ueberspringe Erstellung (mit -Recreate neu aufbauen)."
    Write-Step "4/4 VM starten"
    & $VBoxManage startvm $VmName --type gui
    return
  }
}
& $VBoxManage createvm --name $VmName --ostype "Ubuntu_64" --register
& $VBoxManage modifyvm $VmName --memory $MemoryMB --cpus $Cpus --vram 128 --graphicscontroller vmsvga --accelerate3d on --nic1 nat --audio-driver dsound --audio-enabled on --audio-controller hda --clipboard-mode bidirectional --draganddrop bidirectional --usb on --usbehci on --boot1 dvd --boot2 disk
$vmFolder = Join-Path ([Environment]::GetFolderPath("UserProfile")) (Join-Path "VirtualBox VMs" $VmName)
$vdi = Join-Path $vmFolder "$VmName.vdi"
& $VBoxManage createmedium disk --filename $vdi --size ($DiskGB * 1024) --format VDI --variant Standard
& $VBoxManage storagectl $VmName --name "SATA" --add sata --controller IntelAhci --portcount 1
& $VBoxManage storageattach $VmName --storagectl "SATA" --port 0 --device 0 --type hdd --medium $vdi
& $VBoxManage storagectl $VmName --name "IDE" --add ide --controller PIIX4
& $VBoxManage storageattach $VmName --storagectl "IDE" --port 1 --device 0 --type dvddrive --medium $IsoPath
& $VBoxManage showvminfo $VmName --machinereadable | Select-String -Pattern "^(memory|cpus|firmware)" | Select-Object -First 4

# --- 4. Start ---
Write-Step "4/4 VM starten"
Write-Host "Naechste Schritte IN der VM (siehe docs/INSTALL.md Abschnitt B):"
Write-Host "  1. Kubuntu installieren (Drittanbieter-Treiber: ja)"
Write-Host "  2. Snapshot frisch-installiert anlegen"
Write-Host "  3. git clone + sudo ./iso/provision-lokroos.sh"
& $VBoxManage startvm $VmName --type gui
