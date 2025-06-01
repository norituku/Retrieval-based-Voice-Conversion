"""
Nuitka configuration for Voice Converter Mac App
"""

# Nuitka options configuration
nuitka_options = {
    # Basic options
    'standalone': True,
    'onefile': False,  # スタンドアロンバンドルを使用
    'assume-yes-for-downloads': True,
    
    # macOS specific
    'macos-create-app-bundle': True,
    'macos-app-name': 'Voice Converter',
    'macos-app-mode': 'gui',
    'macos-app-version': '1.0.0',
    'macos-signed-app-name': 'Voice Converter',
    
    # Plugins
    'enable-plugins': [
        'tk-inter',
        'numpy',
        'multiprocessing'
    ],
    
    # Include modules
    'include-modules': [
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'json',
        'subprocess',
        'threading',
        'pathlib',
        'datetime',
        'os',
        'sys',
        'math',
        'time',
        'wave',
        'struct',
        'tempfile',
        'shutil',
        'platform',
        'traceback',
        'logging'
    ],
    
    # Include data files and directories
    'include-data-dirs': [
        'configs=configs',
        'model_dir=model_dir',
        'rvc=rvc'
    ],
    
    'include-data-files': [
        'gui_settings.json=gui_settings.json',
        'README.md=README.md'
    ],
    
    # Output options
    'output-dir': 'dist',
    'remove-output': True,
    
    # Optimization（このバージョンのNuitkaではサポート外）
    # 'optimize': 2,
    
    # Debug options
    'show-progress': True,
    'show-memory': True,
    'quiet': False
}

# Additional files to include in the app bundle
additional_resources = {
    'Info.plist': '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>Voice Converter</string>
    <key>CFBundleIdentifier</key>
    <string>com.rvc.voiceconverter</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>Voice Converter</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSHumanReadableCopyright</key>
    <string>Copyright © 2024 RVC Project. All rights reserved.</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
    <key>NSRequiresAquaSystemAppearance</key>
    <false/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.music</string>
    <key>NSMicrophoneUsageDescription</key>
    <string>Voice Converter needs access to your microphone for voice input.</string>
</dict>
</plist>'''
}