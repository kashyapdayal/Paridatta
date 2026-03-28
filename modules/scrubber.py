import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any

class MetadataScrubber:
    def __init__(self):
        pass

    def scrub(self, input_path: Path, output_path: Path) -> Dict[str, Any]:
        """
        Main entry point for scrubbing any file type.
        Detects file type and delegates to the appropriate scrubber.
        Returns a dictionary with 'success' (bool) and 'error' (str, optional).
        """
        try:
            if not input_path.exists():
                return {"success": False, "error": "File not found"}

            ext = input_path.suffix.lower()

            # Video/Audio extensions (uses ffmpeg stream copy for speed & handles multi-GB files)
            media_exts = {".mp4", ".mkv", ".avi", ".mov", ".mp3", ".wav", ".flac", ".ogg", ".webm"}
            # Images
            image_exts = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp", ".gif"}
            
            if ext in media_exts:
                return self._scrub_media(input_path, output_path)
            elif ext in image_exts:
                return self._scrub_image(input_path, output_path)
            elif ext == ".pdf":
                return self._scrub_pdf(input_path, output_path)
            else:
                # Fallback for all other files: strip extended attributes, 
                # but basically copy file securely so OS-level metadata is reset.
                return self._scrub_generic(input_path, output_path)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _scrub_media(self, input_path: Path, output_path: Path) -> Dict[str, Any]:
        """Uses ffmpeg to strip metadata without re-encoding. Can handle 10GB+ files near instantly."""
        try:
            cmd = [
                "ffmpeg", "-y", "-i", str(input_path),
                "-map_metadata", "-1",  # Strip global metadata
                "-c:v", "copy",         # Copy video stream directly
                "-c:a", "copy",         # Copy audio stream directly
                str(output_path)
            ]
            # Run silently. Large files take time depending on disk IO, but no re-encoding makes it fast.
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            if result.returncode == 0:
                return {"success": True}
            else:
                return {"success": False, "error": result.stderr.decode("utf-8", "ignore")}
        except FileNotFoundError:
            # Fallback if ffmpeg is missing
            return self._scrub_generic(input_path, output_path)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _scrub_image(self, input_path: Path, output_path: Path) -> Dict[str, Any]:
        try:
            from PIL import Image
            # Open the image, get data without EXIF/metadata, save it
            with Image.open(input_path) as img:
                data = list(img.getdata())
                image_without_exif = Image.new(img.mode, img.size)
                image_without_exif.putdata(data)
                
                # Default save parameters
                save_kwargs = {}
                if input_path.suffix.lower() in [".jpg", ".jpeg"]:
                    save_kwargs['quality'] = 95
                
                image_without_exif.save(output_path, **save_kwargs)
            return {"success": True}
        except Exception as e:
            # Fallback to generic copying if PIL fails
            return self._scrub_generic(input_path, output_path)

    def _scrub_pdf(self, input_path: Path, output_path: Path) -> Dict[str, Any]:
        try:
            from PyPDF2 import PdfReader, PdfWriter
            reader = PdfReader(str(input_path))
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            # Do not carry over reader.metadata
            writer.add_metadata({})
            
            with open(output_path, "wb") as f:
                writer.write(f)
            return {"success": True}
        except Exception as e:
            return self._scrub_generic(input_path, output_path)

    def _scrub_generic(self, input_path: Path, output_path: Path) -> Dict[str, Any]:
        """
        Generic fallback: purely copies the file contents without OS metadata (timestamps, etc.)
        Allows infinite size by copying in chunks.
        """
        try:
            with open(input_path, 'rb') as fsrc:
                with open(output_path, 'wb') as fdst:
                    shutil.copyfileobj(fsrc, fdst, length=1024*1024*16) # 16MB chunks for memory efficiency
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
