; Easy Converter - Inno Setup Installer
; Requiere Inno Setup 6+ (https://jrsoftware.org/isdl.php)

#define MyAppName "Easy Converter"
#define MyAppVersion "2.2.0"
#define MyAppPublisher "EasyConverter"
#define MyAppURL "https://github.com/joseamorenoc025/easy-converter"
#define MyAppExeName "EasyConverter.exe"

[Setup]
AppId={{B8A3C2D1-4E5F-4A6B-9C8D-1E2F3A4B5C6D}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={localappdata}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=EasyConverter-Installer-{#MyAppVersion}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Conversor bidireccional PDF a Word

; Firma (opcional, requiere certificado .pfx)
; SignTool=signtool /fd SHA256 /f "$p\..\build\cert.pfx" /p EasyConverter2026 $f

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"
Name: "contextmenu"; Description: "Añadir opciones al menú contextual de Windows"; GroupDescription: "Integración:"
Name: "tesseract"; Description: "Instalar Tesseract OCR (Inglés + Español)"; GroupDescription: "Componentes opcionales:"; Flags: checkedonce

[Files]
Source: "..\dist\EasyConverter.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "tesseract-ocr-w64-setup-5.5.0.20241111.exe"; DestDir: "{tmp}"; Flags: ignoreversion; Tasks: tesseract

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Registry]
; Asociación de archivos .pdf (por usuario, sin admin)
Root: "HKCU"; Subkey: "Software\Classes\.pdf\OpenWithProgids\EasyConverter.PDF"; ValueType: none; Flags: createvalueifdoesntexist
Root: "HKCU"; Subkey: "Software\Classes\EasyConverter.PDF"; ValueType: string; ValueData: "Easy Converter PDF"; Flags: createvalueifdoesntexist
Root: "HKCU"; Subkey: "Software\Classes\EasyConverter.PDF\DefaultIcon"; ValueType: string; ValueData: "{app}\{#MyAppExeName},0"
Root: "HKCU"; Subkey: "Software\Classes\EasyConverter.PDF\shell\open\command"; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" --pdf2word ""%1"""

; Asociación de archivos .docx
Root: "HKCU"; Subkey: "Software\Classes\.docx\OpenWithProgids\EasyConverter.DOCX"; ValueType: none; Flags: createvalueifdoesntexist
Root: "HKCU"; Subkey: "Software\Classes\EasyConverter.DOCX"; ValueType: string; ValueData: "Easy Converter DOCX"; Flags: createvalueifdoesntexist
Root: "HKCU"; Subkey: "Software\Classes\EasyConverter.DOCX\DefaultIcon"; ValueType: string; ValueData: "{app}\{#MyAppExeName},0"
Root: "HKCU"; Subkey: "Software\Classes\EasyConverter.DOCX\shell\open\command"; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" --word2pdf ""%1"""

; Asociación de archivos .doc
Root: "HKCU"; Subkey: "Software\Classes\.doc\OpenWithProgids\EasyConverter.DOC"; ValueType: none; Flags: createvalueifdoesntexist
Root: "HKCU"; Subkey: "Software\Classes\EasyConverter.DOC"; ValueType: string; ValueData: "Easy Converter DOC"; Flags: createvalueifdoesntexist
Root: "HKCU"; Subkey: "Software\Classes\EasyConverter.DOC\DefaultIcon"; ValueType: string; ValueData: "{app}\{#MyAppExeName},0"
Root: "HKCU"; Subkey: "Software\Classes\EasyConverter.DOC\shell\open\command"; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" --word2pdf ""%1"""

; Menú contextual (clic derecho)
Root: "HKCU"; Subkey: "Software\Classes\SystemFileAssociations\.pdf\shell\EasyConverter"; Tasks: contextmenu; ValueType: string; ValueData: "Convertir a Word"
Root: "HKCU"; Subkey: "Software\Classes\SystemFileAssociations\.pdf\shell\EasyConverter\command"; Tasks: contextmenu; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" --pdf2word ""%1"""
Root: "HKCU"; Subkey: "Software\Classes\SystemFileAssociations\.docx\shell\EasyConverter"; Tasks: contextmenu; ValueType: string; ValueData: "Convertir a PDF"
Root: "HKCU"; Subkey: "Software\Classes\SystemFileAssociations\.docx\shell\EasyConverter\command"; Tasks: contextmenu; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" --word2pdf ""%1"""
Root: "HKCU"; Subkey: "Software\Classes\SystemFileAssociations\.doc\shell\EasyConverter"; Tasks: contextmenu; ValueType: string; ValueData: "Convertir a PDF"
Root: "HKCU"; Subkey: "Software\Classes\SystemFileAssociations\.doc\shell\EasyConverter\command"; Tasks: contextmenu; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" --word2pdf ""%1"""

[Run]
Filename: "{tmp}\tesseract-ocr-w64-setup-5.5.0.20241111.exe"; Parameters: "/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /COMPONENTS=""program,tessdata_eng,tessdata_spa"""; StatusMsg: "Instalando Tesseract OCR (Inglés + Español)..."; Flags: waituntilterminated runhidden; Tasks: tesseract
Filename: "{app}\{#MyAppExeName}"; Description: "Ejecutar {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\assets\*"
Type: dirifempty; Name: "{app}\assets"
Type: dirifempty; Name: "{app}"
