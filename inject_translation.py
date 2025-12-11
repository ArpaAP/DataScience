#!/usr/bin/env python3
"""
Inject translated markdown cells back into Jupyter notebooks.
Reads *_translated.json files (edited iteratively by AI) and injects translations.
Preserves all code cells, outputs, and notebook structure.
"""

import json
import argparse
from pathlib import Path

def modify_code_cell_paths(source):
    """Replace Google Drive paths with local paths in code cells."""
    patterns = [
        ('/content/gdrive/MyDrive/DataScience/data/', 'data/'),
        ('/content/gdrive/My Drive/DataScience/data/', 'data/'),
        ("'/content/gdrive/MyDrive/DataScience/data/", "'data/"),
        ('"/content/gdrive/MyDrive/DataScience/data/', '"data/'),
    ]
    
    result = source
    for pattern, replacement in patterns:
        result = result.replace(pattern, replacement)
    
    return result

def inject_translations(original_path, translation_path, output_path):
    """
    Inject translations into a notebook.

    Reads *_translated.json (created by extract_markdown.py and edited by AI)
    and replaces markdown cells in the original notebook with translations.

    Args:
        original_path: Path to original notebook
        translation_path: Path to translated JSON file (iteratively edited by AI)
        output_path: Path for output notebook

    Returns:
        tuple: (success, message)
    """
    # Read original notebook
    with open(original_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)
    
    # Read translation data
    with open(translation_path, 'r', encoding='utf-8') as f:
        translation_data = json.load(f)
    
    # Build index map from translation data and validate completeness
    translation_map = {}
    missing_translations = []

    for cell_data in translation_data['markdown_cells']:
        cell_index = cell_data['cell_index']
        translation = cell_data.get('translation')
        source = cell_data.get('source_lines', [])

        # Allow empty translations only if source is also empty (valid empty cell)
        if translation is None:
            missing_translations.append(cell_index)
        elif translation == [] and source != []:
            missing_translations.append(cell_index)
        else:
            translation_map[cell_index] = translation

    # Check if all translations are present
    if missing_translations:
        return False, f"Missing translations for {len(missing_translations)} cells: {missing_translations}"
    
    # Inject translations and modify code paths
    cells_modified = 0
    code_cells_modified = 0
    
    for i, cell in enumerate(notebook['cells']):
        cell_type = cell.get('cell_type')
        
        if cell_type == 'markdown' and i in translation_map:
            # Replace source with translation
            translation = translation_map[i]
            if isinstance(translation, str):
                translation = [translation]
            cell['source'] = translation
            cells_modified += 1
        
        elif cell_type == 'code':
            # Modify Google Drive paths in code cells
            source = cell.get('source', [])
            if isinstance(source, list):
                source_str = ''.join(source)
            else:
                source_str = source
            
            modified_source = modify_code_cell_paths(source_str)
            
            if modified_source != source_str:
                # Keep as list format with proper line breaks
                if isinstance(source, list):
                    lines = []
                    current_line = ""
                    for char in modified_source:
                        current_line += char
                        if char == '\n':
                            lines.append(current_line)
                            current_line = ""
                    if current_line:
                        lines.append(current_line)
                    cell['source'] = lines if lines else [modified_source]
                else:
                    cell['source'] = modified_source
                code_cells_modified += 1
    
    # Verify all translations were applied
    expected = len(translation_map)
    if cells_modified != expected:
        return False, f"Cell count mismatch: expected {expected}, applied {cells_modified}"
    
    # Write output notebook
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, ensure_ascii=False, indent=1)
    
    return True, f"{cells_modified} markdown cells injected, {code_cells_modified} code cells path-modified"

def main():
    parser = argparse.ArgumentParser(description='Inject translations into notebooks')
    parser.add_argument('--original-dir', type=str, default='notebooks',
                        help='Directory containing original notebooks')
    parser.add_argument('--translations-dir', type=str, default='translation_workspace',
                        help='Directory containing translated JSON files')
    parser.add_argument('--output-dir', type=str, default='translated',
                        help='Output directory for translated notebooks')
    parser.add_argument('--chapters', type=str, nargs='+', default=['14', '15', '16', '17'],
                        help='Chapter prefixes to process')
    
    args = parser.parse_args()
    
    original_dir = Path(args.original_dir)
    translations_dir = Path(args.translations_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    patterns = [f"{ch}*.ipynb" for ch in args.chapters]
    
    total_notebooks = 0
    successful = 0
    
    print(f"Injecting translations for chapters: {', '.join(args.chapters)}")
    print(f"Reading from: {translations_dir}/*_translated.json")
    print(f"Output to: {output_dir}/")
    print("=" * 60)
    
    for pattern in patterns:
        for original_path in sorted(original_dir.glob(pattern)):
            # Find corresponding translation file
            translation_filename = original_path.stem + '_translated.json'
            translation_path = translations_dir / translation_filename
            
            if not translation_path.exists():
                print(f"⚠ Skipping {original_path.name}: translation file not found")
                continue
            
            output_path = output_dir / original_path.name
            
            try:
                success, message = inject_translations(original_path, translation_path, output_path)
                
                if success:
                    print(f"✓ {original_path.name}")
                    print(f"    → {message}")
                    successful += 1
                else:
                    print(f"✗ {original_path.name}")
                    print(f"    → Error: {message}")
                
                total_notebooks += 1
                
            except Exception as e:
                print(f"✗ Error processing {original_path.name}: {e}")
                total_notebooks += 1
    
    print("=" * 60)
    print(f"Summary: {successful}/{total_notebooks} notebooks successfully processed")
    print(f"         Output saved to {output_dir}/")

if __name__ == "__main__":
    main()
