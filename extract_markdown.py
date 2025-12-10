#!/usr/bin/env python3
"""
Extract markdown cells from Jupyter notebooks to lightweight JSON files.
This reduces file size by ~90% for efficient translation.

Creates two files per notebook:
1. *_extracted.json - Original extraction (backup reference)
2. *_translated.json - Working copy for AI to edit iteratively

Both files have identical structure with 'translation': null fields.
AI fills the 'translation' fields in *_translated.json through multiple edits.
"""

import json
import re
import argparse
from pathlib import Path

def modify_google_drive_paths(text):
    """Replace Google Drive paths with local paths."""
    # Pattern: /content/gdrive/MyDrive/DataScience/data/ -> data/
    patterns = [
        (r'/content/gdrive/MyDrive/DataScience/data/', 'data/'),
        (r'/content/gdrive/My Drive/DataScience/data/', 'data/'),
        (r"'/content/gdrive/MyDrive/DataScience/data/", "'data/"),
        (r'"/content/gdrive/MyDrive/DataScience/data/', '"data/'),
    ]
    
    result = text
    for pattern, replacement in patterns:
        result = result.replace(pattern, replacement)
    
    return result

def extract_markdown_cells(notebook_path):
    """
    Extract markdown cells from a notebook.
    
    Returns:
        dict: Extraction result with notebook name, metadata, and markdown cells
    """
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    cells = notebook.get('cells', [])
    total_cells = len(cells)
    markdown_cells = []
    code_cells = 0
    
    for i, cell in enumerate(cells):
        cell_type = cell.get('cell_type')
        
        if cell_type == 'markdown':
            # Get source and apply path modifications
            source = cell.get('source', [])
            if isinstance(source, str):
                source = [source]
            
            # Modify Google Drive paths in markdown
            modified_source = []
            for line in source:
                modified_line = modify_google_drive_paths(line)
                modified_source.append(modified_line)
            
            markdown_cells.append({
                'cell_index': i,
                'source_lines': modified_source,
                'translation': None
            })
        elif cell_type == 'code':
            code_cells += 1
    
    return {
        'notebook_name': notebook_path.name,
        'extraction_metadata': {
            'total_cells': total_cells,
            'markdown_cells': len(markdown_cells),
            'code_cells': code_cells
        },
        'markdown_cells': markdown_cells
    }

def main():
    parser = argparse.ArgumentParser(description='Extract markdown cells from notebooks')
    parser.add_argument('--notebooks-dir', type=str, default='notebooks',
                        help='Directory containing original notebooks')
    parser.add_argument('--output-dir', type=str, default='translation_workspace',
                        help='Output directory for extracted JSON files')
    parser.add_argument('--chapters', type=str, nargs='+', default=['14', '15', '16', '17'],
                        help='Chapter prefixes to process')
    
    args = parser.parse_args()
    
    notebooks_dir = Path(args.notebooks_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Build patterns from chapters
    patterns = [f"{ch}*.ipynb" for ch in args.chapters]
    
    total_notebooks = 0
    total_markdown_cells = 0
    
    print(f"Extracting markdown cells from chapters: {', '.join(args.chapters)}")
    print(f"Output directory: {output_dir}")
    print("=" * 60)
    
    for pattern in patterns:
        for notebook_path in sorted(notebooks_dir.glob(pattern)):
            try:
                result = extract_markdown_cells(notebook_path)

                # Save extracted JSON
                extracted_filename = notebook_path.stem + '_extracted.json'
                extracted_path = output_dir / extracted_filename

                with open(extracted_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                # Also create translated JSON (copy of extracted) for AI to edit iteratively
                translated_filename = notebook_path.stem + '_translated.json'
                translated_path = output_dir / translated_filename

                with open(translated_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                md_count = result['extraction_metadata']['markdown_cells']
                total_cells = result['extraction_metadata']['total_cells']

                print(f"✓ {notebook_path.name}")
                print(f"    → {md_count} markdown cells / {total_cells} total cells")
                print(f"    → Created: {extracted_filename} + {translated_filename}")

                total_notebooks += 1
                total_markdown_cells += md_count

            except Exception as e:
                print(f"✗ Error processing {notebook_path.name}: {e}")
    
    print("=" * 60)
    print(f"Summary: {total_notebooks} notebooks processed")
    print(f"         {total_markdown_cells} total markdown cells extracted")
    print(f"         Created {total_notebooks * 2} JSON files ({total_notebooks} extracted + {total_notebooks} translated)")
    print(f"         Output saved to {output_dir}/")
    print(f"\nNext step: AI will iteratively edit *_translated.json files to fill translation fields")

if __name__ == "__main__":
    main()
