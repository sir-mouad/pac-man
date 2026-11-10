# PyInstaller source-independent desktop distribution. Build on the target OS.
import sys
from pathlib import Path

root = Path(SPECPATH)
a = Analysis(
    [str(root / "pac-man.py")],
    pathex=[str(root)],
    binaries=[],
    datas=[(str(root / "config.json"), ".")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "numpy", "matplotlib"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, [], exclude_binaries=True, name="Pac-Man",
    debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
    console=sys.platform != "darwin",
)
collection = COLLECT(
    exe, a.binaries, a.datas, strip=False, upx=False, name="Pac-Man",
)
if sys.platform == "darwin":
    app = BUNDLE(
        collection, name="Pac-Man.app", icon=None,
        bundle_identifier="club.arcade.pacman",
        info_plist={"NSHighResolutionCapable": True,
                    "CFBundleShortVersionString": "0.1.0"},
    )
