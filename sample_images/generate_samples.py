"""
ImageProof - Enhanced Test Image Generator Script
Creates 5 distinct forensic test scenarios:
1. sample_camera_photo.jpg - Authentic Nikon Z8 DSLR capture with optics & GPS
2. sample_photoshop_edited.jpg - Modified photo with Adobe Photoshop signature
3. sample_social_media.png - Stripped PNG (simulating WhatsApp/Instagram metadata removal)
4. sample_iphone_portrait.jpg - iPhone 15 Pro mobile capture with Bengaluru GPS & iOS firmware
5. sample_dji_drone.jpg - Aerial drone surveillance photo with Mumbai coastal GPS & high altitude
"""

import os
from PIL import Image, ImageDraw

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def create_sample_camera_photo():
    img = Image.new("RGB", (800, 600), color=(20, 50, 90))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 760, 560], outline=(100, 180, 255), width=3)
    draw.text((70, 80), "EVIDENCE SAMPLE #1: Nikon Z8 DSLR", fill=(255, 255, 255))
    draw.text((70, 120), "Authentic Hardware Capture • New Delhi Geolocation", fill=(180, 220, 255))
    draw.text((70, 160), "Optics: 50mm f/2.8 | Shutter: 1/500s | ISO: 400", fill=(140, 190, 240))
    draw.text((70, 200), "Forensic Status: 100% Consistent Hardware EXIF", fill=(100, 230, 150))

    exif = img.getexif()
    exif[0x010f] = "Nikon Corporation"
    exif[0x0110] = "Nikon Z8"
    exif[0x0131] = "Ver.2.00 (Nikon Firmware)"
    exif[0x0132] = "2026:10:25 14:32:10"

    exif_ifd = exif.get_ifd(0x8769)
    exif_ifd[0x9003] = "2026:10:25 14:32:10"
    exif_ifd[0x9004] = "2026:10:25 14:32:10"
    exif_ifd[0x829a] = 0.002
    exif_ifd[0x829d] = 2.8
    exif_ifd[0x8827] = 400
    exif_ifd[0x920a] = 50.0
    exif_ifd[0xa434] = "NIKKOR Z 50mm f/1.8 S"

    gps_ifd = exif.get_ifd(0x8825)
    gps_ifd[1] = "N"
    gps_ifd[2] = (28.0, 36.0, 50.0)
    gps_ifd[3] = "E"
    gps_ifd[4] = (77.0, 12.0, 32.4)
    gps_ifd[6] = 216.0
    gps_ifd[7] = (9.0, 2.0, 10.0)
    gps_ifd[29] = "2026:10:25"

    out_path = os.path.join(OUTPUT_DIR, "sample_camera_photo.jpg")
    img.save(out_path, exif=exif, quality=95)

def create_sample_photoshop_edited():
    img = Image.new("RGB", (800, 600), color=(60, 25, 40))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 760, 560], outline=(255, 120, 140), width=3)
    draw.text((70, 80), "EVIDENCE SAMPLE #2: Photoshop Manipulated Asset", fill=(255, 255, 255))
    draw.text((70, 120), "Editing Artifact Detected • Software Signature Present", fill=(255, 180, 190))
    draw.text((70, 160), "Software: Adobe Photoshop 2024 (Windows)", fill=(255, 140, 150))
    draw.text((70, 200), "Forensic Status: WARNING - Post-Processing Flagged", fill=(255, 100, 100))

    exif = img.getexif()
    exif[0x010f] = "Canon"
    exif[0x0110] = "Canon EOS R5"
    exif[0x0131] = "Adobe Photoshop 2024 (Windows)"
    exif[0x0132] = "2026:10:27 18:45:00"

    exif_ifd = exif.get_ifd(0x8769)
    exif_ifd[0x9003] = "2026:09:12 11:15:00"
    exif_ifd[0x829a] = 0.004
    exif_ifd[0x829d] = 4.0
    exif_ifd[0x8827] = 200

    out_path = os.path.join(OUTPUT_DIR, "sample_photoshop_edited.jpg")
    img.save(out_path, exif=exif, quality=95)

def create_sample_social_media_png():
    img = Image.new("RGB", (640, 480), color=(15, 30, 45))
    draw = ImageDraw.Draw(img)
    draw.rectangle([30, 30, 610, 450], outline=(70, 130, 180), width=3)
    draw.text((60, 80), "EVIDENCE SAMPLE #3: Web / Social Media Asset", fill=(255, 255, 255))
    draw.text((60, 120), "Simulated WhatsApp / Telegram Compression (PNG)", fill=(170, 210, 240))
    draw.text((60, 160), "All EXIF headers & GPS coordinates stripped", fill=(140, 180, 210))
    draw.text((60, 200), "Forensic Status: INFO - Metadata Absent (Privacy Stripping)", fill=(100, 200, 255))

    out_path = os.path.join(OUTPUT_DIR, "sample_social_media.png")
    img.save(out_path, format="PNG")

def create_sample_iphone_portrait():
    img = Image.new("RGB", (800, 600), color=(25, 45, 35))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 760, 560], outline=(100, 220, 160), width=3)
    draw.text((70, 80), "EVIDENCE SAMPLE #4: Apple iPhone 15 Pro", fill=(255, 255, 255))
    draw.text((70, 120), "Mobile Incident Photo • Bengaluru Geolocation", fill=(180, 240, 200))
    draw.text((70, 160), "Optics: 24mm f/1.78 | ISO: 80 | iOS 17.5.1", fill=(140, 210, 170))
    draw.text((70, 200), "Forensic Status: Authentic Smartphone Telemetry", fill=(100, 255, 150))

    exif = img.getexif()
    exif[0x010f] = "Apple"
    exif[0x0110] = "iPhone 15 Pro"
    exif[0x0131] = "17.5.1"  # iOS version
    exif[0x0132] = "2026:10:26 18:22:45"

    exif_ifd = exif.get_ifd(0x8769)
    exif_ifd[0x9003] = "2026:10:26 18:22:45"
    exif_ifd[0x9004] = "2026:10:26 18:22:45"
    exif_ifd[0x829a] = 0.008333333333333333 # 1/120s
    exif_ifd[0x829d] = 1.78
    exif_ifd[0x8827] = 80
    exif_ifd[0x920a] = 6.765
    exif_ifd[0xa434] = "iPhone 15 Pro back triple camera 6.76mm f/1.78"

    # Bengaluru GPS: 12.9716° N, 77.5946° E, Alt: 920m
    gps_ifd = exif.get_ifd(0x8825)
    gps_ifd[1] = "N"
    gps_ifd[2] = (12.0, 58.0, 17.75)
    gps_ifd[3] = "E"
    gps_ifd[4] = (77.0, 35.0, 40.56)
    gps_ifd[6] = 920.0
    gps_ifd[7] = (12.0, 52.0, 45.0)
    gps_ifd[29] = "2026:10:26"

    out_path = os.path.join(OUTPUT_DIR, "sample_iphone_portrait.jpg")
    img.save(out_path, exif=exif, quality=95)

def create_sample_dji_drone():
    img = Image.new("RGB", (800, 600), color=(40, 30, 60))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 760, 560], outline=(180, 140, 240), width=3)
    draw.text((70, 80), "EVIDENCE SAMPLE #5: DJI Mavic 3 Pro Drone", fill=(255, 255, 255))
    draw.text((70, 120), "Aerial Surveillance Feed • Mumbai Coastal Coordinates", fill=(210, 180, 255))
    draw.text((70, 160), "Altitude: 154.5m ASL | Shutter: 1/800s | ISO: 100", fill=(170, 140, 220))
    draw.text((70, 200), "Forensic Status: Authentic UAV Aerial Capture", fill=(200, 160, 255))

    exif = img.getexif()
    exif[0x010f] = "DJI"
    exif[0x0110] = "Mavic 3 Pro"
    exif[0x0131] = "v01.00.0600 (DJI Firmware)"
    exif[0x0132] = "2026:10:27 07:15:30"

    exif_ifd = exif.get_ifd(0x8769)
    exif_ifd[0x9003] = "2026:10:27 07:15:30"
    exif_ifd[0x9004] = "2026:10:27 07:15:30"
    exif_ifd[0x829a] = 0.00125 # 1/800s
    exif_ifd[0x829d] = 2.8
    exif_ifd[0x8827] = 100
    exif_ifd[0x920a] = 24.0
    exif_ifd[0xa434] = "Hasselblad 24mm f/2.8"

    # Mumbai Marine Drive GPS: 18.9438° N, 72.8231° E, Alt: 154.5m
    gps_ifd = exif.get_ifd(0x8825)
    gps_ifd[1] = "N"
    gps_ifd[2] = (18.0, 56.0, 37.68)
    gps_ifd[3] = "E"
    gps_ifd[4] = (72.0, 49.0, 23.16)
    gps_ifd[6] = 154.5
    gps_ifd[7] = (1.0, 45.0, 30.0)
    gps_ifd[29] = "2026:10:27"

    out_path = os.path.join(OUTPUT_DIR, "sample_dji_drone.jpg")
    img.save(out_path, exif=exif, quality=95)

if __name__ == "__main__":
    create_sample_camera_photo()
    create_sample_photoshop_edited()
    create_sample_social_media_png()
    create_sample_iphone_portrait()
    create_sample_dji_drone()
    print("All 5 forensic sample images generated successfully!")
