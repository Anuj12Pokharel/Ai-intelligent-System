"""
Quick analysis of downloaded files
"""
import os

files = os.listdir('data/raw')
print(f"Total files: {len(files)}\n")

for i, f in enumerate(files, 1):
    path = os.path.join('data/raw', f)
    size = os.path.getsize(path) / 1024  # KB
    ext = os.path.splitext(f)[1]
    print(f"{i}. {f[:60]}")
    print(f"   Type: {ext}, Size: {size:.1f} KB")
