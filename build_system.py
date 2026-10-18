#!/usr/bin/env python3
"""Prototype source packaging; full media/OS builds remain unimplemented."""

import sys
import zipfile
import json
from pathlib import Path
from datetime import datetime

class ForgeBuilder:
    """Source packager with explicit failures for unimplemented components."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        
    def build_all(self):
        """Build everything"""
        print("🔥 THE FORGE - COMPLETE BUILD SYSTEM")
        print("=" * 70)
        print()
        
        steps = [
            ("1. Setup Build Environment", self.setup_environment),
            ("2. Build Core System", self.build_core),
            ("3. Build Video Editor", self.build_video_editor),
            ("4. Build Linux OS", self.build_linux_os),
            ("5. Build Documentation", self.build_documentation),
            ("6. Create Distribution Package", self.create_distribution),
            ("7. Generate Checksums", self.generate_checksums),
        ]
        
        for step_name, step_func in steps:
            print(f"\n{step_name}")
            print("-" * 70)
            try:
                step_func()
                print(f"✅ {step_name} - COMPLETE")
            except Exception as e:
                print(f"❌ {step_name} - FAILED: {e}")
                return False
        
        print()
        print("=" * 70)
        print("🎉 BUILD COMPLETE!")
        print(f"📦 Distribution: {self.dist_dir}")
        return True
    
    def setup_environment(self):
        """Setup build environment"""
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        print("   ✓ Build directories created")
        
    def build_core(self):
        """Build core Python implementation"""
        print("   Building Python core...")
        # Core is already built, just verify
        core_files = [
            "forge_implementation.py",
            "forge_server.py",
            "forge_cli.py",
            "forge_gui.py"
        ]
        for f in core_files:
            if (self.project_root / f).exists():
                print(f"   ✓ {f}")
            else:
                raise FileNotFoundError(f"Required source file missing: {f}")
    
    def build_video_editor(self):
        """Build video editor components"""
        raise NotImplementedError("Video editor build is not implemented; no editor was built")
        
    def build_linux_os(self):
        """Prepare Linux OS builder"""
        raise NotImplementedError("Linux image build is not implemented; no ISO was created")
        
    def build_documentation(self):
        """Compile all documentation"""
        print("   Documentation ready")
        
    def create_distribution(self):
        """Package prototype sources, dependencies and UI assets, not an OS."""
        required = ["forge_implementation.py", "forge_server.py", "forge_cli.py",
                    "forge_gui.py", "forge_local.py", "requirements.txt", "README.md", "LICENSE"]
        for name in required:
            if not (self.project_root / name).is_file():
                raise FileNotFoundError(f"Required package input missing: {name}")
        self.dist_dir.mkdir(parents=True, exist_ok=True)
        zip_name = f"FORGE_prototype_source_{datetime.now().strftime('%Y%m%d')}.zip"
        zip_path = self.dist_dir / zip_name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            inputs = set(self.project_root.glob("*.py"))
            inputs.update(self.project_root / name for name in required)
            inputs.update(self.project_root / name for name in
                          ("Makefile", "package.json", "forge_knowledge_base.json",
                           "forge_vllm_config.json"))
            for folder in ("docs", "templates", "static", "tests"):
                inputs.update((self.project_root / folder).rglob("*"))
            for path in sorted(inputs):
                relative = path.relative_to(self.project_root)
                if (path.is_file() and not path.is_symlink()
                        and not any(part.startswith(".") or part == "__pycache__"
                                    for part in relative.parts)
                        and path.suffix not in (".pyc", ".pyo")):
                    zipf.write(path, relative.as_posix())
        
        print(f"   ✓ Created: {zip_name}")
        print(f"   ✓ Size: {zip_path.stat().st_size / 1024 / 1024:.2f} MB")
        
        return zip_path
    
    def generate_checksums(self):
        """Generate checksums for verification"""
        print("   Generating checksums...")
        
        checksums = {}
        for file in self.dist_dir.glob("*.zip"):
            import hashlib
            with open(file, 'rb') as f:
                checksums[file.name] = {
                    'md5': hashlib.md5(f.read()).hexdigest(),
                    'size': file.stat().st_size
                }
            checksums[file.name]['sha256'] = hashlib.sha256(file.read_bytes()).hexdigest()
        
        checksum_file = self.dist_dir / "checksums.json"
        with open(checksum_file, 'w') as f:
            json.dump(checksums, f, indent=2)
        
        print(f"   ✓ Checksums saved to {checksum_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-only", action="store_true",
                        help="Package the Python prototype; does not build an OS or editor")
    args = parser.parse_args()
    builder = ForgeBuilder()
    if args.source_only:
        builder.create_distribution()
        builder.generate_checksums()
        success = True
    else:
        success = builder.build_all()
    sys.exit(0 if success else 1)
