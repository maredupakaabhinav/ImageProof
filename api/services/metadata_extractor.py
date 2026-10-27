"""
ImageProof - Digital Evidence Authenticity Analyzer
Service: Image Metadata Extractor (Pillow)

Extracts file properties, EXIF tags, camera hardware details, timestamps,
and GPS geolocation coordinates from evidence images.
"""

import os
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def _format_size(size_bytes: int) -> str:
    """Converts raw byte count into human-readable string (KB, MB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

def _serialize_exif_value(value):
    """
    Safely converts Pillow EXIF objects (like IFDRational, bytes, tuples)
    into standard Python JSON-serializable types.
    """
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8", errors="replace").strip("\x00")
        except Exception:
            return str(value)
    elif hasattr(value, "real") and hasattr(value, "numerator"):  # IFDRational or Fraction
        try:
            val_float = float(value)
            # If it's a clean integer value, return as int
            return int(val_float) if val_float.is_integer() else round(val_float, 4)
        except Exception:
            return str(value)
    elif isinstance(value, (list, tuple)):
        return [_serialize_exif_value(item) for item in value]
    elif isinstance(value, dict):
        return {str(k): _serialize_exif_value(v) for k, v in value.items()}
    elif isinstance(value, (int, float, str, bool)) or value is None:
        return value
    return str(value)

def _convert_dms_to_decimal(dms, ref: str) -> float:
    """
    Converts GPS Degrees/Minutes/Seconds tuple to decimal degrees.
    e.g., ((28, 1), (36, 1), (5012, 100)) with ref 'N' -> 28.613922
    """
    try:
        deg = float(dms[0])
        minute = float(dms[1])
        sec = float(dms[2])
        decimal = deg + (minute / 60.0) + (sec / 3600.0)
        if ref in ["S", "W"]:
            decimal = -decimal
        return round(decimal, 6)
    except Exception:
        return None

def extract_metadata(file_path: str, original_filename: str = None) -> dict:
    """
    Analyzes an image file using Pillow and extracts structured metadata.
    
    :param file_path: Path to the target image file.
    :param original_filename: Original client filename if different from disk.
    :return: Structured dictionary containing categorized forensic metadata.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image not found at path: {file_path}")

    file_size = os.path.getsize(file_path)
    stat_info = os.stat(file_path)
    
    base_name = original_filename if original_filename else os.path.basename(file_path)
    ext = os.path.splitext(base_name)[1].lower()
    
    file_info = {
        "filename": base_name,
        "extension": ext,
        "size_bytes": file_size,
        "size_formatted": _format_size(file_size),
        "fs_created": datetime.fromtimestamp(stat_info.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
        "fs_modified": datetime.fromtimestamp(stat_info.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
        "width": None,
        "height": None,
        "aspect_ratio": None,
        "megapixels": None,
        "format": None,
        "mode": None
    }
    
    camera_info = {
        "make": None,
        "model": None,
        "software": None,
        "lens_model": None,
        "exposure_time": None,
        "f_number": None,
        "iso": None,
        "focal_length": None,
        "flash": None,
        "orientation": None
    }
    
    timestamp_info = {
        "datetime_original": None,
        "datetime_digitized": None,
        "datetime_modified": None
    }
    
    gps_info = {
        "has_gps": False,
        "latitude": None,
        "longitude": None,
        "altitude": None,
        "gps_timestamp": None,
        "dms_latitude": None,
        "dms_longitude": None,
        "maps_url": None
    }
    
    raw_exif_clean = {}
    has_exif = False

    # Open image with Pillow
    with Image.open(file_path) as img:
        width, height = img.size
        file_info["width"] = width
        file_info["height"] = height
        file_info["format"] = img.format or ext.replace(".", "").upper()
        file_info["mode"] = img.mode
        
        # Calculate Megapixels
        mp = (width * height) / 1_000_000
        file_info["megapixels"] = f"{mp:.2f} MP"
        
        # Calculate Aspect Ratio
        if height > 0:
            ratio = width / height
            file_info["aspect_ratio"] = f"{ratio:.2f}:1"
            
        # Extract EXIF metadata if supported by file format
        raw_exif = img.getexif()
        if raw_exif:
            has_exif = True
            gps_raw_data = {}
            
            for tag_id, value in raw_exif.items():
                tag_name = TAGS.get(tag_id, str(tag_id))
                
                # Check for GPS Info IFD (Tag 34853)
                if tag_name == "GPSInfo" or tag_id == 34853:
                    try:
                        gps_ifd = raw_exif.get_ifd(tag_id)
                        for gps_id, gps_val in gps_ifd.items():
                            sub_tag = GPSTAGS.get(gps_id, str(gps_id))
                            gps_raw_data[sub_tag] = _serialize_exif_value(gps_val)
                    except Exception:
                        pass
                else:
                    raw_exif_clean[tag_name] = _serialize_exif_value(value)
            
            # Map standard camera fields
            camera_info["make"] = raw_exif_clean.get("Make")
            camera_info["model"] = raw_exif_clean.get("Model")
            camera_info["software"] = raw_exif_clean.get("Software")
            camera_info["orientation"] = raw_exif_clean.get("Orientation")
            
            # Exposure / Optics
            if "ExposureTime" in raw_exif_clean:
                exp = raw_exif_clean["ExposureTime"]
                camera_info["exposure_time"] = f"1/{round(1/exp)}" if (isinstance(exp, (int, float)) and exp > 0 and exp < 1) else str(exp)
            if "FNumber" in raw_exif_clean:
                camera_info["f_number"] = f"f/{raw_exif_clean['FNumber']}"
            if "ISOSpeedRatings" in raw_exif_clean:
                camera_info["iso"] = str(raw_exif_clean["ISOSpeedRatings"])
            if "FocalLength" in raw_exif_clean:
                camera_info["focal_length"] = f"{raw_exif_clean['FocalLength']} mm"
            if "LensModel" in raw_exif_clean:
                camera_info["lens_model"] = str(raw_exif_clean["LensModel"])
            if "Flash" in raw_exif_clean:
                camera_info["flash"] = str(raw_exif_clean["Flash"])
                
            # Timestamps
            timestamp_info["datetime_modified"] = raw_exif_clean.get("DateTime")
            timestamp_info["datetime_original"] = raw_exif_clean.get("DateTimeOriginal")
            timestamp_info["datetime_digitized"] = raw_exif_clean.get("DateTimeDigitized")
            
            # If DateTimeOriginal wasn't at the root, check Exif IFD (Tag 34665)
            try:
                exif_ifd = raw_exif.get_ifd(34665)
                for sub_id, sub_val in exif_ifd.items():
                    sub_name = TAGS.get(sub_id, str(sub_id))
                    serialized_val = _serialize_exif_value(sub_val)
                    raw_exif_clean[sub_name] = serialized_val
                    
                    if sub_name == "DateTimeOriginal" and not timestamp_info["datetime_original"]:
                        timestamp_info["datetime_original"] = serialized_val
                    elif sub_name == "DateTimeDigitized" and not timestamp_info["datetime_digitized"]:
                        timestamp_info["datetime_digitized"] = serialized_val
                    elif sub_name == "LensModel" and not camera_info["lens_model"]:
                        camera_info["lens_model"] = str(serialized_val)
                    elif sub_name == "FNumber" and not camera_info["f_number"]:
                        camera_info["f_number"] = f"f/{serialized_val}"
                    elif sub_name == "ExposureTime" and not camera_info["exposure_time"]:
                        exp = serialized_val
                        camera_info["exposure_time"] = f"1/{round(1/exp)}" if (isinstance(exp, (int, float)) and exp > 0 and exp < 1) else str(exp)
                    elif sub_name == "ISOSpeedRatings" and not camera_info["iso"]:
                        camera_info["iso"] = str(serialized_val)
                    elif sub_name == "FocalLength" and not camera_info["focal_length"]:
                        camera_info["focal_length"] = f"{serialized_val} mm"
            except Exception:
                pass
                
            # Decode GPS Coordinates
            if gps_raw_data and "GPSLatitude" in gps_raw_data and "GPSLongitude" in gps_raw_data:
                lat_ref = gps_raw_data.get("GPSLatitudeRef", "N")
                lng_ref = gps_raw_data.get("GPSLongitudeRef", "E")
                lat = _convert_dms_to_decimal(gps_raw_data["GPSLatitude"], lat_ref)
                lng = _convert_dms_to_decimal(gps_raw_data["GPSLongitude"], lng_ref)
                
                if lat is not None and lng is not None:
                    gps_info["has_gps"] = True
                    gps_info["latitude"] = lat
                    gps_info["longitude"] = lng
                    gps_info["dms_latitude"] = f"{gps_raw_data['GPSLatitude']} {lat_ref}"
                    gps_info["dms_longitude"] = f"{gps_raw_data['GPSLongitude']} {lng_ref}"
                    gps_info["maps_url"] = f"https://www.google.com/maps?q={lat},{lng}"
                    
                    if "GPSAltitude" in gps_raw_data:
                        try:
                            gps_info["altitude"] = f"{float(gps_raw_data['GPSAltitude']):.1f} meters"
                        except Exception:
                            gps_info["altitude"] = str(gps_raw_data["GPSAltitude"])
                            
                    if "GPSDateStamp" in gps_raw_data and "GPSTimeStamp" in gps_raw_data:
                        gps_info["gps_timestamp"] = f"{gps_raw_data['GPSDateStamp']} {gps_raw_data['GPSTimeStamp']}"

    return {
        "has_exif": has_exif and len(raw_exif_clean) > 0,
        "file_info": file_info,
        "camera_info": camera_info,
        "timestamp_info": timestamp_info,
        "gps_info": gps_info,
        "raw_exif": raw_exif_clean
    }
