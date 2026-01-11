#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
from src.ingestion.parser import NepaliLegalParser
import os

files = [f for f in os.listdir('data/raw') if f.endswith('.pdf')]
p = NepaliLegalParser(f'data/raw/{files[0]}')
act = p.parse()

print(f'Parts: {len(act.parts)}')
print(f'Chapters (direct): {len(act.chapters)}')

for i, part in enumerate(act.parts[:3]):
    print(f'\nPart {i+1}:')
    print(f'  Chapters: {len(part.chapters)}')
    for j, chap in enumerate(part.chapters[:2]):
        print(f'    Chapter {j+1}: {len(chap.sections)} sections')
