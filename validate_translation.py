import json
from pathlib import Path
from difflib import unified_diff

class NotebookValidator:
    def __init__(self, original_path, translated_path):
        self.original_path = original_path
        self.translated_path = translated_path
        self.issues = []

        with open(original_path, 'r', encoding='utf-8') as f:
            self.original = json.load(f)

        with open(translated_path, 'r', encoding='utf-8') as f:
            self.translated = json.load(f)

    def validate_cell_count(self):
        """Check if both notebooks have the same number of cells"""
        orig_count = len(self.original['cells'])
        trans_count = len(self.translated['cells'])

        if orig_count != trans_count:
            self.issues.append(
                f"❌ Cell count mismatch: Original={orig_count}, Translated={trans_count}"
            )
            return False
        return True

    def validate_cell_types(self):
        """Check if cell types match in order"""
        mismatches = []
        for i, (orig_cell, trans_cell) in enumerate(zip(self.original['cells'], self.translated['cells'])):
            orig_type = orig_cell.get('cell_type')
            trans_type = trans_cell.get('cell_type')

            if orig_type != trans_type:
                mismatches.append(f"  Cell {i}: {orig_type} → {trans_type}")

        if mismatches:
            self.issues.append(f"❌ Cell type mismatches:\n" + "\n".join(mismatches))
            return False
        return True

    def validate_code_cells(self):
        """Check if code cells have identical source code"""
        mismatches = []
        for i, (orig_cell, trans_cell) in enumerate(zip(self.original['cells'], self.translated['cells'])):
            if orig_cell.get('cell_type') != 'code':
                continue

            orig_source = ''.join(orig_cell.get('source', []))
            trans_source = ''.join(trans_cell.get('source', []))

            if orig_source != trans_source:
                mismatches.append(f"  Cell {i}: Code differs")
                # Show first 100 chars of difference
                if len(orig_source) < 100:
                    mismatches.append(f"    Original: {orig_source[:100]}")
                    mismatches.append(f"    Translated: {trans_source[:100]}")

        if mismatches:
            self.issues.append(f"❌ Code cell mismatches:\n" + "\n".join(mismatches))
            return False
        return True

    def validate_markdown_translated(self):
        """Check that markdown cells are actually translated (not identical)"""
        identical_count = 0
        total_markdown = 0

        for i, (orig_cell, trans_cell) in enumerate(zip(self.original['cells'], self.translated['cells'])):
            if orig_cell.get('cell_type') != 'markdown':
                continue

            total_markdown += 1
            orig_source = ''.join(orig_cell.get('source', []))
            trans_source = ''.join(trans_cell.get('source', []))

            # Skip empty cells
            if not orig_source.strip():
                continue

            if orig_source == trans_source:
                identical_count += 1

        if total_markdown > 0 and identical_count == total_markdown:
            self.issues.append(f"⚠️  Warning: All {total_markdown} markdown cells are identical (not translated?)")
            return False

        return True

    def validate_outputs_present(self):
        """Check that code cells with outputs in original also have outputs in translated"""
        missing_outputs = []
        for i, (orig_cell, trans_cell) in enumerate(zip(self.original['cells'], self.translated['cells'])):
            if orig_cell.get('cell_type') != 'code':
                continue

            orig_outputs = orig_cell.get('outputs', [])
            trans_outputs = trans_cell.get('outputs', [])

            if len(orig_outputs) > 0 and len(trans_outputs) == 0:
                missing_outputs.append(f"  Cell {i}: {len(orig_outputs)} outputs missing")

        if missing_outputs:
            self.issues.append(f"⚠️  Missing outputs:\n" + "\n".join(missing_outputs))
            return False
        return True

    def validate_metadata(self):
        """Check that important metadata is preserved"""
        # Check kernel info
        orig_kernel = self.original.get('metadata', {}).get('kernelspec', {}).get('name')
        trans_kernel = self.translated.get('metadata', {}).get('kernelspec', {}).get('name')

        if orig_kernel and trans_kernel and orig_kernel != trans_kernel:
            self.issues.append(f"⚠️  Kernel mismatch: {orig_kernel} vs {trans_kernel}")

    def run_all_validations(self):
        """Run all validation checks"""
        validations = [
            ("Cell count", self.validate_cell_count),
            ("Cell types", self.validate_cell_types),
            ("Code cells", self.validate_code_cells),
            ("Markdown translation", self.validate_markdown_translated),
            ("Outputs present", self.validate_outputs_present),
            ("Metadata", self.validate_metadata),
        ]

        results = {}
        for name, validation_func in validations:
            try:
                results[name] = validation_func()
            except Exception as e:
                self.issues.append(f"❌ Error in {name} validation: {e}")
                results[name] = False

        return results

def main():
    notebooks_dir = Path("notebooks")
    translated_dir = Path("translated")

    patterns = ["10*.ipynb", "13*.ipynb"]

    all_results = {}
    total_files = 0
    files_with_issues = 0

    print("="*80)
    print("NOTEBOOK TRANSLATION VALIDATION REPORT")
    print("="*80)
    print()

    for pattern in patterns:
        for original_path in sorted(notebooks_dir.glob(pattern)):
            translated_path = translated_dir / original_path.name

            if not translated_path.exists():
                print(f"⚠️  SKIP: {original_path.name} - No translation found")
                continue

            total_files += 1
            validator = NotebookValidator(original_path, translated_path)
            results = validator.run_all_validations()

            all_results[original_path.name] = {
                'results': results,
                'issues': validator.issues
            }

            # Print results for this file
            all_passed = all(results.values())
            status = "✅ PASS" if all_passed and not validator.issues else "⚠️  ISSUES"

            print(f"{status}: {original_path.name}")

            if validator.issues:
                files_with_issues += 1
                for issue in validator.issues:
                    print(f"  {issue}")

            # Show validation details
            failed_checks = [name for name, passed in results.items() if not passed]
            if failed_checks and not validator.issues:
                print(f"  Failed checks: {', '.join(failed_checks)}")

            print()

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total files validated: {total_files}")
    print(f"Files with issues: {files_with_issues}")
    print(f"Files passed: {total_files - files_with_issues}")

    if files_with_issues == 0:
        print("\n✅ All notebooks passed validation!")
    else:
        print(f"\n⚠️  {files_with_issues} notebook(s) have issues that need attention")

    print("="*80)

if __name__ == "__main__":
    main()
