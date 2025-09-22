import os
import csv
from collections import defaultdict
csv.field_size_limit(2_000_000) 

class RF2Ontology:
    def __init__(self, rf2_dir):
        self.rf2_dir = rf2_dir
        self.concepts = {}      # conceptId -> active flag
        self.descriptions = {}  # conceptId -> list of terms
        self.children = defaultdict(list)  # conceptId -> list of children conceptIds
        #self.icd10_map = defaultdict(list)  # conceptId -> list of ICD-10 codes
        self.load_concepts()
        self.load_descriptions()
        self.load_relationships()
        # self.load_icd10_mappings()

    def load_concepts(self):
        path = os.path.join(self.rf2_dir,"sct2_Concept_Snapshot_INT_20250201.txt")
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                if row["active"] == "1":
                    self.concepts[row["id"]] = True


    def load_descriptions(self):
        path = os.path.join(self.rf2_dir, "sct2_Description_Snapshot-en_INT_20250201.txt")
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                cid = row["conceptId"]
                if cid in self.concepts and row["active"] == "1":
                    self.descriptions.setdefault(cid, []).append(row["term"])

    def load_relationships(self):
        path = os.path.join(self.rf2_dir, "sct2_Relationship_Snapshot_INT_20250201.txt")
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                if row["active"] == "1" and row["typeId"] == "116680003":  # IS-A
                    source = row["sourceId"]
                    target = row["destinationId"]
                    if target in self.concepts and source in self.concepts:
                        self.children[target].append(source)

    # def load_icd10_mappings(self):
    #     # Replace this with the actual ICD-10 map refset file name
    #     path = os.path.join(self.rf2_dir, "sct2_Map-SimpleSnapshot_INT_20250201.txt")
    #     if not os.path.exists(path):
    #         print("ICD-10 mapping file not found. Skipping ICD-10 load.")
    #         return
    #     with open(path, "r", encoding="utf-8") as f:
    #         reader = csv.DictReader(f, delimiter="\t")
    #         for row in reader:
    #             if row["active"] == "1":
    #                 cid = row["conceptId"]
    #                 icd10 = row["mapTarget"]
    #                 if cid in self.concepts:
    #                     self.icd10_map[cid].append(icd10)

    def search(self, term):
        term_lower = term.lower()
        results = []
        for cid, terms in self.descriptions.items():
            if any(term_lower in t.lower() for t in terms):
                results.append((cid, terms))
        return results

    def descendants(self, concept_id):
        result = set()
        stack = [concept_id]
        while stack:
            current = stack.pop()
            for child in self.children.get(current, []):
                if child not in result:
                    result.add(child)
                    stack.append(child)
        return result

    # def map_to_icd10(self, concept_id):
    #     # Returns ICD-10 codes for this concept and all descendants
    #     codes = set(self.icd10_map.get(concept_id, []))
    #     for desc in self.descendants(concept_id):
    #         codes.update(self.icd10_map.get(desc, []))
    #     return list(codes)


# --- USAGE ---
if __name__ == "__main__":
    rf2_path = r"C:\SNOWMED\Terminology"  # your TRUD folder
    ontology = RF2Ontology(rf2_path)

    search_term = "breast cancer"
    matches = ontology.search(search_term)
    print(f"Found {len(matches)} matching concepts for '{search_term}':\n")

    
    with open("search_results.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Concept ID", "Terms", "Descendant Count", "Descendant IDs"])
        for cid, terms in matches:
            desc = ontology.descendants(cid)
            writer.writerow([
                cid,
                "; ".join(terms),
                len(desc),
                ", ".join(desc) if desc else "-"
            ])

    print("Search results have been written to search_results.csv.")


    # for cid, terms in matches:
    #     print(f"Concept {cid}: {terms}")
    #     desc = ontology.descendants(cid)
    #    print(f"  Descendants ({len(desc)}): {desc}")
        # icd10_codes = ontology.map_to_icd10(cid)
        # print(f"  ICD-10 Codes: {icd10_codes}\n")
