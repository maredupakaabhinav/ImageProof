"""
ImageProof - Digital Evidence Authenticity Analyzer
Service: Cryptographic File Integrity Hasher (SHA-256)

Cyber Forensics Context:
In digital forensics (ISO/IEC 27037 standard), establishing evidence integrity
is paramount. A cryptographic hash functions as a unique mathematical digital
fingerprint. 

Key Forensics Principles:
1. Determinism: The same file will always produce the exact same SHA-256 hash.
2. Avalanche Effect: Changing even a single bit in the image file completely 
   alters the output hash.
3. Integrity vs. Authenticity: A hash verifies that an evidence file has not been 
   altered since it was acquired, provided an investigator has an authoritative
   reference hash recorded at the time of seizure.
"""

import hashlib
import os

def calculate_sha256(file_path: str) -> str:
    """
    Computes the SHA-256 cryptographic checksum of a given file.
    
    Reads in 64 KB (65,536 bytes) chunks to ensure efficient memory usage,
    even when processing high-resolution forensics images.
    
    :param file_path: Absolute or relative path to the image file.
    :return: 64-character lowercase hexadecimal SHA-256 string.
    :raises FileNotFoundError: If the specified file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Target file not found for hashing: {file_path}")
        
    sha256_hasher = hashlib.sha256()
    
    # Process file in 64KB blocks to prevent memory exhaustion
    CHUNK_SIZE = 65536
    with open(file_path, "rb") as evidence_file:
        while True:
            chunk = evidence_file.read(CHUNK_SIZE)
            if not chunk:
                break
            sha256_hasher.update(chunk)
            
    return sha256_hasher.hexdigest()
