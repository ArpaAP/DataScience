import json
import sys
from pathlib import Path

def sync_notebook_outputs(original_path, translated_path):
    """
    Synchronize outputs from original notebook to translated notebook.
    Preserves all translated content but copies outputs from original cells.
    """
    # Read both notebooks
    with open(original_path, 'r', encoding='utf-8') as f:
        original_nb = json.load(f)

    with open(translated_path, 'r', encoding='utf-8') as f:
        translated_nb = json.load(f)

    # Check if notebooks have same number of cells
    if len(original_nb['cells']) != len(translated_nb['cells']):
        print(f"Warning: Different number of cells in {original_path.name}")
        print(f"  Original: {len(original_nb['cells'])}, Translated: {len(translated_nb['cells'])}")
        min_cells = min(len(original_nb['cells']), len(translated_nb['cells']))
    else:
        min_cells = len(original_nb['cells'])

    # Copy outputs from original to translated
    outputs_copied = 0
    for i in range(min_cells):
        orig_cell = original_nb['cells'][i]
        trans_cell = translated_nb['cells'][i]

        # Only copy outputs for code cells
        if orig_cell.get('cell_type') == 'code' and trans_cell.get('cell_type') == 'code':
            if 'outputs' in orig_cell and len(orig_cell['outputs']) > 0:
                trans_cell['outputs'] = orig_cell['outputs']
                outputs_copied += 1

            # Also copy execution_count if present
            if 'execution_count' in orig_cell:
                trans_cell['execution_count'] = orig_cell['execution_count']

    # Write the updated translated notebook
    with open(translated_path, 'w', encoding='utf-8') as f:
        json.dump(translated_nb, f, ensure_ascii=False, indent=1)

    print(f"✓ {translated_path.name}: {outputs_copied} outputs synchronized")
    return outputs_copied

def main():
    notebooks_dir = Path("notebooks")
    translated_dir = Path("translated")

    # Get all chapter 10 and 13 notebooks
    patterns = ["10*.ipynb", "13*.ipynb"]

    total_outputs = 0
    files_processed = 0

    for pattern in patterns:
        for original_path in sorted(notebooks_dir.glob(pattern)):
            translated_path = translated_dir / original_path.name

            if not translated_path.exists():
                print(f"⚠ Skipping {original_path.name}: translated version not found")
                continue

            try:
                outputs = sync_notebook_outputs(original_path, translated_path)
                total_outputs += outputs
                files_processed += 1
            except Exception as e:
                print(f"✗ Error processing {original_path.name}: {e}")

    print(f"\n{'='*60}")
    print(f"Summary: {files_processed} files processed, {total_outputs} total outputs synchronized")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
