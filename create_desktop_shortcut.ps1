$ErrorActionPreference = "Stop"

function New-LabIcon {
    param(
        [Parameter(Mandatory = $true)]
        [string]$IconPath
    )

    Add-Type -AssemblyName System.Drawing

    $size = 256
    $bitmap = New-Object System.Drawing.Bitmap($size, $size)
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.Clear([System.Drawing.Color]::FromArgb(15, 23, 42))

    $linePen = New-Object System.Drawing.Pen([System.Drawing.Color]::FromArgb(226, 232, 240), 12)
    $linePen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
    $linePen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round

    $amberBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(245, 158, 11))
    $skyBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(56, 189, 248))
    $greenBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(52, 211, 153))

    $leftNode = New-Object System.Drawing.Rectangle(42, 42, 54, 54)
    $rightNode = New-Object System.Drawing.Rectangle(160, 42, 54, 54)
    $bottomNode = New-Object System.Drawing.Rectangle(101, 142, 58, 58)

    $graphics.DrawLine($linePen, 69, 69, 130, 171)
    $graphics.DrawLine($linePen, 187, 69, 130, 171)
    $graphics.FillEllipse($amberBrush, $leftNode)
    $graphics.FillEllipse($skyBrush, $rightNode)
    $graphics.FillEllipse($greenBrush, $bottomNode)

    $pngStream = New-Object System.IO.MemoryStream
    $bitmap.Save($pngStream, [System.Drawing.Imaging.ImageFormat]::Png)
    $pngBytes = $pngStream.ToArray()

    $iconStream = New-Object System.IO.MemoryStream
    $writer = New-Object System.IO.BinaryWriter($iconStream)
    $writer.Write([UInt16]0)
    $writer.Write([UInt16]1)
    $writer.Write([UInt16]1)
    $writer.Write([byte]0)
    $writer.Write([byte]0)
    $writer.Write([byte]0)
    $writer.Write([byte]0)
    $writer.Write([UInt16]1)
    $writer.Write([UInt16]32)
    $writer.Write([UInt32]$pngBytes.Length)
    $writer.Write([UInt32]22)
    $writer.Write($pngBytes)

    [System.IO.File]::WriteAllBytes($IconPath, $iconStream.ToArray())

    $writer.Dispose()
    $iconStream.Dispose()
    $pngStream.Dispose()
    $amberBrush.Dispose()
    $skyBrush.Dispose()
    $greenBrush.Dispose()
    $linePen.Dispose()
    $graphics.Dispose()
    $bitmap.Dispose()
}

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$StartBat = Join-Path $ProjectRoot "start.bat"
$IconPath = Join-Path $ProjectRoot "ai-idea-research-lab.ico"
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "AI Idea Research Lab.lnk"

if (-not (Test-Path $StartBat)) {
    throw "start.bat not found at '$StartBat'."
}

if (-not (Test-Path $IconPath)) {
    New-LabIcon -IconPath $IconPath
}

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $StartBat
$Shortcut.WorkingDirectory = $ProjectRoot
$Shortcut.Description = "Launch AI Idea Research Lab"
$Shortcut.IconLocation = "$IconPath,0"
$Shortcut.WindowStyle = 1
$Shortcut.Save()

Write-Host "Desktop shortcut created:"
Write-Host $ShortcutPath
