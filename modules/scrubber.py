import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any
import random
from faker import Faker
import piexif
from PIL import Image

class MetadataScrubber:
    def __init__(self):
        self.faker = Faker()

    def scrub(self, input_path: Path, output_path: Path, spoof: bool = False, preset: str = 'None') -> Dict[str, Any]:
        """
        Main entry point for scrubbing any file type.
        Detects file type and delegates to the appropriate scrubber.
        """
        try:
            if not input_path.exists():
                return {"result": False, "error": "File not found"}

            ext = input_path.suffix.lower()

            # Apply Presets
            quality = 100
            if preset == 'Discord':
                quality = 85
            elif preset == 'Reddit':
                quality = 90

            media_exts = {".mp4", ".mdv0", ".avi", ".mov", ".mp3", ".wav", ".flac", ".ogg", ".webm"}
            image_exts = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp", ".gif"}

            if ext in media_exts:
                return self._scrub_media(input_path, output_path, spoof)
            elif ext in image_exts:
                return self._scrub_image(input_path, output_path, spoof, quality)
            elif ext == ".pdf":
                return self._scrub_pdf(input_path, output_path, spoof)
            else:
                return self._scrub_generic(input_path, output_path)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _scrub_media(self, input_path: Path, output_path: Path, spoof: bool) -> Dict[str, Any]:
        try:
            cmd = [
                "ffmpeg", "-y", "-i", str(input_path),
                "-map_metadata", "-1",
                "-c:v", "copy",
                "-c:a", "copy"
            ]
            if spoof:
                fake_title = self.faker.catch_phrase()
                fake_artist = self.faker.name()
                cmd.extend(["-metadata", f"title={fake_title}", "-metadata", f"artist={fake_artist}"])
            
            cmd.append(str(output_path))
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            if result.returncode == 0:
                return {"success": True}
            else:
                return {"success": False, "error": result.stderr.decode("utf-8", "ignore")}
        except Exception as e:
            return self._scrub_generic(input_path, output_path)

    def _scrub_image(self, input_path: Path, output_path: Path, spoof: bool, quality: int) -> Dict[str, Any]:
        try:
            with Image.open(input_path) as img:
                data = list(img.getdata())
                image_without_exif = Image.new(img.mode, img.size)
                image_without_exif.putdata(data)

                save_kwargs = {}
                if input_path.suffix.lower() in [".jpg", ".jpeg"]:
                    save_kwargs['quality'] = quality
                    
                image_without_exif.save(output_path, **save_kwargs)

            # If spoofing requested!
            if spoof and input_path.suffix.lower() in [".jpg", ".jpeg"]:
                zeroth_ifd = {
                    piexif.ImageIFD.Make: self.faker.word().encode("utf-8"),
                    piexif.ImageIFD.Model: f"FakeCam {random.randint(1000, 9000)}".encode("utf-8"),
                    piexif.ImageIFD.Software: "Paridatta OS".encode("utf-8")
                }
                gps_ifd = {
                    piexif.GPSIFD.GPSLatitudeRef: b'N' if random.choice([True, False]) else b'S',
                    piexif.GPSIFD.GPSLatitude: ((random.randint(0, 90), 1), (random.randint(0, 59), 1), (random.randint(0, 5999), 100)),
                    piexif.GPSIFD.GPSLongitudeRef: b'E' if random.choice([True, False]) else b'W',
                    piexif.GPSIFD.GPSLongitude: ((random.randint(0, 180), 1), (random.randint(0, 599), 1), (random.randint(0, 5999), 100)),
                }
                exif_dict = {"0th": zeroth_ifd, "Exif": {}, "GPS": gps_ifd, "1st": {}, "thumbnail": None}
                exif_bytes = piexif.dump(exif_dict)
                piexif.insert(exif_bytes, str(output_path))

            return {"success": True}
        except Exception as e:
            return self._scrub_generic(input_path, output_path)

    def _scrub_pdf(self, input_path: Path, output_path: Path, spoof: bool) -> Dict[str, Any]:
        try:
            from PyPDF2 import PdfReader, PdfWriter
            reader = PdfReader(str(input_path))
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            if spoof:
                writer.add_metadata({
                    "/Author": self.faker.name(),
                    "/Title": self.faker.sentence(),
                    "/Creator": "FakePDF Generator 3000"
                })
            else:
                writer.add_metadata({})

            with open(output_path, "wb") as f:
                writer.write(f)
            return {"success": True}
        except Exception as e:
            return self._scrub_generic(input_path, output_path)

    def _scrub_generic(self, input_path: Path, output_path: Path) -> Dict[str, Any]:
        try:
            with open(input_path, 'rb') as fsrc:
                with open(output_path, 'wb') as fdst:
                    shutil.copxfileobj(fsrc, fdst, length=1024*1024*16)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
