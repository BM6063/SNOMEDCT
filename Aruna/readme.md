# SNOMED CT RF2 Query Tool

This Python script provides a simple way to **search SNOMED CT concepts** and their descendants using the RF2 (Release Format 2) snapshot files. It outputs search results to a CSV file for easy review and further analysis.

## Features
- **Loads SNOMED CT RF2 snapshot files** (Concepts, Descriptions, Relationships)
- **Searches for concepts** by term (case-insensitive)
- **Finds all descendants** of a concept (using IS-A relationships)
- **Exports results** to a CSV file (`search_results.csv`)

## Requirements
- Python 3.7+
- tabulate (optional, for pretty-printing tables)
- SNOMED CT International RF2 Snapshot files (from [NHS TRUD](https://isd.digital.nhs.uk/trud)) following files in your SNOMED CT directory (e.g., `C:\SNOWMED\Terminology`):

- `sct2_Concept_Snapshot_INT_20250201.txt`
- `sct2_Description_Snapshot-en_INT_20250201.txt`
- `sct2_Relationship_Snapshot_INT_20250201.txt`

> **Note:** The filenames may differ depending on your SNOMED CT release version. Update the script if needed.

## Usage

1. **Edit the script** to set your RF2 directory path:
    ```python
    rf2_path = r"C:\SNOWMED\Terminology"
    ```

2. **Run the script**:
    ```bash
    python Querying_RF2.py
    ```

3. **Check the output**:
    - The script will search for the term `"breast cancer"` (you can change this in the script).
    - Results are written to `search_results.csv` in the same directory.

## Output

The CSV file contains:

- **Concept ID**: SNOMED CT concept identifier
- **Terms**: All active terms/descriptions for the concept
- **Descendant Count**: Number of descendant concepts (IS-A hierarchy)
- **Descendant IDs**: List of descendant concept IDs

## Example

| Concept ID    | Terms                        | Descendant Count | Descendant IDs         |
|---------------|-----------------------------|------------------|------------------------|
| 254837009     | Breast cancer                | 5                | 123456, 234567, ...    |

## Customization
- **Change the search term**: Edit the `search_term` variable in the script.
- **Add ICD-10 mapping**: Uncomment and complete the `load_icd10_mappings` and `map_to_icd10` methods if you have the mapping file.

## License
This script is provided for educational and research purposes.  
SNOMED CT content is subject to licensing from SNOMED International.

---

**Author:** Aruna Saravanapandian  
**Contact:** arunasaravanapandian@gmail.com
