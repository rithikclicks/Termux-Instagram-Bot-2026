import py_compile
import os
import shutil
import sys

DIST_DIR = "dist"
FILES_TO_COMPILE = ["rithik.py", "bot_engine.py", "config.py", "interface.py"]
RESOURCES = ["requirements.txt", "README.md", ".gitignore"]

def compile_and_protect():
    print(f"[*] Creating '{DIST_DIR}' directory...")
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)

    print("[*] Compiling core files...")
    for filename in FILES_TO_COMPILE:
        if not os.path.exists(filename):
            print(f"[!] Warning: {filename} not found.")
            continue
            
        # Compile to bytecode
        try:
            cfile = py_compile.compile(filename, cfile=os.path.join(DIST_DIR, filename + "c"), doraise=True)
            print(f"    [+] Compiled {filename} -> {os.path.basename(cfile)}")
        except Exception as e:
            print(f"    [!] Error compiling {filename}: {e}")

    print("[*] Copying resources...")
    for resource in RESOURCES:
        if os.path.exists(resource):
            shutil.copy(resource, DIST_DIR)
            print(f"    [+] Copied {resource}")
        else:
            print(f"    [!] Warning: {resource} not found.")

    print("\n[SUCCESS] Encrypted distribution created in 'dist/' folder!")
    print("You can now zip the 'dist' folder and share it.")
    print("Users can run it using: python rithik.pyc")

if __name__ == "__main__":
    compile_and_protect()
