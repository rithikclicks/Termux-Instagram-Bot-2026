import os
import base64
import zlib
import shutil

# Files to obfuscate
FILES = ["rithik.py", "bot_engine.py", "config.py", "interface.py"]
# Resources to copy directly
RESOURCES = ["requirements.txt", "README.md", ".gitignore", "license.key"] # Added license.key if exists
OUTPUT_DIR = "Protected_Bot"

def obfuscate_file(filepath):
    """Reads a file, compresses/encodes it, and returns the loader code."""
    with open(filepath, 'rb') as f:
        content = f.read()
    
    # 1. Compress
    compressed = zlib.compress(content, level=9)
    # 2. Base64 Encode
    encoded = base64.b64encode(compressed)
    
    # 3. Create Loader Stub
    loader_code = f"""import base64, zlib, builtins
try:
    exec(zlib.decompress(base64.b64decode({encoded})))
except Exception as e:
    print(f"Error loading protected module: {{e}}")
    exit(1)
"""
    return loader_code

def main():
    print(f"[*] Creating Protected Distribution in '{OUTPUT_DIR}'...")
    
    # Create/Clean Output Dir
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    
    # Process Files
    for filename in FILES:
        if os.path.exists(filename):
            print(f"[*] Encrypting {filename}...")
            try:
                protected_code = obfuscate_file(filename)
                
                # Write to output dir
                out_path = os.path.join(OUTPUT_DIR, filename)
                with open(out_path, 'w') as f:
                    f.write(protected_code)
                    
                print(f"    [+] Protected {filename}")
            except Exception as e:
                print(f"    [!] Failed to protect {filename}: {e}")
        else:
            print(f"    [!] Warning: {filename} not found.")

    # Copy Resources
    print("[*] Copying resources...")
    for res in RESOURCES:
        if os.path.exists(res):
            shutil.copy(res, OUTPUT_DIR)
            print(f"    [+] Copied {res}")
    
    print("\n[SUCCESS] Protected Bot created in 'Protected_Bot/' folder!")
    print("You can zip this folder and share it. The source code is now hidden.")

if __name__ == "__main__":
    main()
