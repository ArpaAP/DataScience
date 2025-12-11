# Translation Plan: Chapters 14-17 Notebooks

## Overview
Translate 25 notebooks (chapters 14-17) from English to Korean, preserving code execution results and structure.

## Scope
- **Source**: `notebooks/` directory (chapters 14-17)
- **Destination**: `translated/` directory
- **Total work**: 25 notebooks, 376 markdown cells
- **Challenge**: Notebooks are too large (up to 1MB) to read/translate in one pass due to token limits

## Translation Requirements
✅ **Translate**: Markdown cell content (text, headings, explanations)
✅ **Preserve**: All code cells, execution outputs, images, tables
✅ **Don't translate**: Code comments, variable names, LaTeX math expressions
✅ **Modify paths**: Change Google Drive paths from `/content/gdrive/MyDrive/DataScience/data/` to `data/`

## Strategy: Extract-Translate-Inject Workflow

To handle token limits, I'll create a three-stage automated workflow:

### Stage 1: Extract Markdown (Python Script)
Create `extract_markdown.py`:
- Read each notebook's JSON structure
- Extract only markdown cell sources with cell indices
- **Apply path modifications during extraction** (Google Drive → local paths)
- Initialize `translation` field as `null` for each cell
- Save to intermediate file: `{notebook_stem}_extracted.json`
- Extracted JSON format (~5-15KB per notebook):
```json
{
  "notebook_name": "14. Why_the_Mean_Matters.ipynb",
  "extraction_metadata": {
    "total_cells": 39,
    "markdown_cells": 18,
    "code_cells": 21
  },
  "markdown_cells": [
    {
      "cell_index": 0,
      "source_lines": ["# Why the Mean Matters\n", "..."],
      "translation": null
    }
  ]
}
```

**Note**: This structure is identical to `_translated.json` - the only difference is that `translation` fields remain `null` until AI fills them.

### Stage 2: Translate (AI) - Iterative Editing Approach
For each extracted JSON file:
1. **Copy**: First copy `{notebook}_extracted.json` to `{notebook}_translated.json`
2. **Edit iteratively**: AI reads and modifies `_translated.json` multiple times, filling `translation` fields progressively
3. **No single-pass generation**: AI doesn't create the entire translated file at once, reducing memory pressure
4. **Resume capability**: If interrupted, can continue from where it left off

**Unified JSON Structure**: Both `_extracted.json` and `_translated.json` use identical structure:
```json
{
  "notebook_name": "14. Why_the_Mean_Matters.ipynb",
  "extraction_metadata": {...},
  "markdown_cells": [
    {
      "cell_index": 0,
      "source_lines": ["# Why the Mean Matters\n", "..."],
      "translation": null  // AI fills this field iteratively
    }
  ]
}
```

**Translation Rules**:
- Translate text content only
- Keep LaTeX math expressions unchanged
- Keep code blocks (` ``` `) unchanged
- Maintain line-by-line structure (newlines must match)
- Preserve HTML tags and image embeds
- **Technical terms**: Translate to Korean equivalents (e.g., 'bootstrap' → '부트스트랩', 'mean' → '평균')
- Match existing translation style from chapters 10-13

### Stage 3: Inject Translation (Python Script)
Create `inject_translation.py`:
- Read original notebook JSON
- Read translated markdown JSON
- Replace markdown cell `source` at matching `cell_index`
- Validate structure matches (cell count, indices, line counts)
- Save to `translated/` directory

### Stage 4: Sync & Validate
Use existing scripts (updated for chapters 14-17):
- Run `sync_outputs.py` to copy all execution results from originals
- Run `validate_translation.py` to verify structure and translation quality
- Perform manual spot-checks on 3-4 notebooks

## Critical Files to Create/Modify

**New files** (will be created):
- `extract_markdown.py` - Extract markdown cells to lightweight JSON (~150 lines)
- `inject_translation.py` - Inject translations back into notebooks (~120 lines)
- `validate_extracted_translation.py` - Pre-injection validation (~80 lines)
- `translation_workspace/` - Directory for intermediate JSON files

**Modify** (existing scripts):
- `sync_outputs.py` - Update chapter patterns to include 14-17
- `validate_translation.py` - Update chapter patterns to include 14-17

**Reference files** (for understanding translation style):
- `translated/13.2. Bootstrap.ipynb` - Korean terminology and style guide
- `notebooks/14. Why_the_Mean_Matters.ipynb` - Smallest test case (1 markdown cell)
- `notebooks/15.1. Correlation.ipynb` - Largest test case (32 markdown cells)

## Edge Cases & Error Handling

### LaTeX Math Expressions
- **Detection**: Look for `$...$` (inline) or `$$...$$` (display math)
- **Handling**: Keep LaTeX unchanged, translate surrounding text only
- **Example**: `The mean $\mu$ represents...` → `평균 $\mu$는 나타냅니다...`

### HTML in Markdown
- **Types**: Image embeds (`<img>`), formatting tags (`<h2>`, `<br>`), data URIs
- **Handling**: Keep ALL HTML tags unchanged, translate only visible text content

### Multi-line Cells
- **Structure**: Cells stored as arrays of strings (each ending with `\n`)
- **Validation**: Ensure line count matches, newline characters preserved
- **Example**: `["Line 1\n", "\n", "Line 3\n"]` → same 3-element structure in Korean

### Cell Index Mismatches
- **Problem**: Translation adds/removes cells accidentally
- **Detection**: Compare cell_index arrays before injection
- **Solution**: Reject translation and retry with clearer instructions

### Missing Translations
- **Problem**: `translation` field is `null` or empty
- **Detection**: Check all cells have non-null translations before injection
- **Solution**: Identify missing cells, re-translate only those cells

## Execution Plan

### Phase 1: Build Infrastructure (Scripts)
1. Create `extract_markdown.py` with path modification logic
2. Create `inject_translation.py` with structure validation
3. Create `validate_extracted_translation.py` for pre-injection checks
4. Update `sync_outputs.py` to add patterns: `"14*.ipynb"`, `"15*.ipynb"`, `"16*.ipynb"`, `"17*.ipynb"`
5. Update `validate_translation.py` similarly
6. Test scripts on one notebook (14. Why_the_Mean_Matters.ipynb)

### Phase 2: Extract All Notebooks
```bash
python extract_markdown.py --notebooks-dir notebooks --output-dir translation_workspace --chapters 14 15 16 17
```
- Output: 25 JSON files in `translation_workspace/`
- Verify each extraction successful

### Phase 3: Translate Notebooks (One-by-One, Iterative)
For each of 25 notebooks:
1. **Copy** `{notebook}_extracted.json` to `{notebook}_translated.json`
2. **Read** the copied `_translated.json` file (~5-15KB)
3. **Edit iteratively**: Modify the file multiple times, filling `translation` fields progressively
4. AI can work on 5-10 cells at a time, saving progress after each batch
5. **Validate** translation completeness (check all `translation` fields are non-null)
6. Run pre-injection validation
7. If validation fails, continue editing `_translated.json` to fix issues

**Advantages**:
- AI can pause and resume without losing progress
- Reduces token usage per operation (incremental edits vs. full generation)
- Easier debugging (can inspect partial translations)
- Same file structure from extraction to injection

**Order**: Process by chapter (14 → 15 → 16 → 17)

### Phase 4: Inject All Translations
```bash
python inject_translation.py --original-dir notebooks --translations-dir translation_workspace --output-dir translated --chapters 14 15 16 17
```
- Output: 25 notebooks in `translated/` directory
- Verify injection count for each notebook

### Phase 5: Sync Outputs & Validate
```bash
python sync_outputs.py
python validate_translation.py
```
- Ensure all code outputs copied from originals
- Verify structure, code preservation, translation completeness
- Manual spot-check 3-4 notebooks (small, medium, large)

### Phase 6: Git Commit (Single Commit Strategy)
After all translations validated:
```bash
git add translated/14*.ipynb translated/15*.ipynb translated/16*.ipynb translated/17*.ipynb
git commit -m "Add Korean translations for chapters 14-17

- Translated 25 notebooks (chapters 14-17)
- 809 total cells, 376 markdown cells translated
- Translated technical terms to Korean
- Preserved all code execution results and outputs
- Modified Google Drive paths to local data/ paths"
```

## Advantages of This Approach
✅ **Token efficient**: Extract only markdown text (90% size reduction)
✅ **Preserves structure**: Automated injection prevents JSON corruption
✅ **Reusable**: Same scripts work for all 25 notebooks
✅ **Validated**: Existing validation scripts ensure quality
✅ **Recoverable**: If translation fails, can retry individual notebooks
✅ **Parallel-ready**: Can extract all first, then translate in any order
✅ **Iterative translation**: AI edits files incrementally, reducing single-operation burden
✅ **Resume capability**: Can pause/resume translation without losing progress
✅ **Unified structure**: Same JSON format from extraction to translation simplifies workflow

## Estimated Timeline
- **Phase 1** (Infrastructure): 30-45 minutes - Script development and testing
- **Phase 2** (Extraction): 2-3 minutes - Automated, one command
- **Phase 3** (Translation): 90-120 minutes - 25 notebooks × 4-5 min each (main effort)
- **Phase 4** (Injection): 2-3 minutes - Automated, one command
- **Phase 5** (Validation): 10-15 minutes - Automated + manual spot-checks
- **Phase 6** (Git commit): 2 minutes

**Total**: ~2.5-3 hours

## Summary

This plan efficiently handles the token limit challenge by:
1. **Extracting** markdown to lightweight JSON files (~90% size reduction)
2. **Copying** extracted JSON to create translation workspace files
3. **Translating** iteratively by editing files multiple times (reduces AI burden)
4. **Injecting** translations back automatically (error-proof)
5. **Validating** using existing infrastructure (ensures quality)

The approach is systematic, automatable, recoverable at each stage, and supports incremental progress with resume capability.

