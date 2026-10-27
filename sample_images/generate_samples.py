"""
ImageProof - Test Image Generator Script
Creates 3 representative forensic test cases:
1. sample_camera_photo.jpg - Authentic direct-from-sensor photo with full EXIF & GPS
2. sample_photoshop_edited.jpg - Photo with Photoshop software signature
3. sample_social_media.png - Stripped image (no EXIF metadata)
"""

import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def create_sample_camera_photo():
    """Generates an image with authentic camera EXIF and GPS tags."""
    img = Image.new("RGB", (800, 600), color=(20, 50, 90))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 750, 550], outline=(100, 180, 255), width=4)
    draw.text((80, 100), "ImageProof Sample Evidence #1", fill=(255, 255, 255))
    draw.text((80, 140), "Authentic Camera Capture Simulation (Nikon Z8)", fill=(180, 220, 255))
    draw.text((80, 180), "Embedded: Camera Make, Model, Optics, GPS Coordinates", fill=(150, 200, 240))

    exif = img.getexif()
    exif[0x010f] = "Nikon Corporation"       # Make
    exif[0x0110] = "Nikon Z8"                 # Model
    exif[0x0131] = "Ver.2.00 (Firmware)"      # Software (Firmware, not editor)
    exif[0x0132] = "2026:10:25 14:32:10"      # DateTime

    # Exif IFD
    exif_ifd = exif.get_ifd(0x8769)
    exif_ifd[0x9003] = "2026:10:25 14:32:10"  # DateTimeOriginal
    exif_ifd[0x9004] = "2026:10:25 14:32:10"  # DateTimeDigitized
    exif_ifd[0x829a] = 0.002                  # 1/500s
    exif_ifd[0x829d] = 2.8                    # f/2.8
    exif_ifd[0x8827] = 400                    # ISO 400
    exif_ifd[0x920a] = 50.0                   # 50mm
    exif_ifd[0xa434] = "NIKKOR Z 50mm f/1.8 S" # LensModel

    # GPS IFD (New Delhi: 28.6139° N, 77.2090° E)
    gps_ifd = exif.get_ifd(0x8825)
    gps_ifd[1] = "N"
    gps_ifd[2] = (28.0, 36.0, 50.0)
    gps_ifd[3] = "E"
    gps_ifd[4] = (77.0, 12.0, 32.4)
    gps_ifd[6] = 216.0                         # 216m altitude
    gps_ifd[7] = (9.0, 2.0, 10.0)             # GPS Time
    gps_ifd[29] = "2026:10:25"                # GPS Date

    out_path = os.path.join(OUTPUT_DIR, "sample_camera_photo.jpg")
    img.save(out_path, exif=exif, quality=95)
    print(f"Created: {out_path}")

def create_sample_photoshop_edited():
    """Generates an image containing editing software signatures."""
    img = Image.new("RGB", (800, 600), color=(60, 25, 40))
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 750, 550], outline=(255, 120, 140), width=4)
    draw.text((80, 100), "ImageProof Sample Evidence #2", fill=(255, 255, 255))
    draw.text((80, 140), "Manipulated / Exported Image Simulation", fill=(255, 180, 190))
    draw.text((80, 180), "Embedded: Adobe Photoshop 2024 Software Signature", fill=(240, 150, 160))

    exif = img.getexif()
    exif[0x010f] = "Canon"
    exif[0x0110] = "Canon EOS R5"
    exif[0x0131] = "Adobe Photoshop 2024 (Windows)" # Software signature triggering warning
    exif[0x0132] = "2026:10:27 18:45:00"            # Modification time

    exif_ifd = exif.get_ifd(0x8769)
    exif_ifd[0x9003] = "2026:09:12 11:15:00"        # Capture date diverged from edit date
    exif_ifd[0x829a] = 0.004                        # 1/250s
    exif_ifd[0x829d] = 4.0                          # f/4
    exif_ifd[0x8827] = 200

    out_path = os.path.join(OUTPUT_DIR, "sample_photoshop_edited.jpg")
    img.save(out_path, exif=exif, quality=95)
    print(f"Created: {out_path}")

def create_sample_social_media_png():
    """Generates a stripped PNG image mimicking WhatsApp / web download."""
    img = Image.new("RGB", (640, 480), color=(15, 30, 45))
    draw = ImageDraw.Draw(img)
    draw.rectangle([30, 30, 610, 450], outline=(70, 130, 180), width=3)
    draw.text((60, 80), "ImageProof Sample Evidence #3", fill=(255, 255, 255))
    draw.text((60, 120), "Web / Social Media Stripped Image (PNG)", fill=(170, 210, 240))
    draw.text((60, 160), "Notice: All EXIF & GPS stripped for privacy/compression", fill=(140, 180, 210))

    out_path = os.path.join(OUTPUT_DIR, "sample_social_media.png")
    img.save(out_path, format="PNG")
    print(f"Created: {out_path}")

if __name__ == "__main__":
    create_sample_camera_photo()
    create_sample_photoshop_edited()
    create_sample_social_media_png()
    print("All 3 sample forensic images successfully generated!")
