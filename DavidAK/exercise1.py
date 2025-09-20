import os
from typing import List, Set, Dict, Any

import owlready2 as owl
import pandas as pd
from dotenv import load_dotenv
import argparse
from database import run_setup

class SnomedIcd10Mapper:
    """
    A class to find and map SNOMED CT concepts to their corresponding ICD-10 codes.

    This class encapsulates the logic for connecting to an ontology database,
    searching for medical terms, filtering them based on specific criteria,
    and generating a structured DataFrame of the mappings.

    Attributes:
        snomedct (owl.Ontology): The SNOMED CT ontology object.
        icd10 (owl.Ontology): The ICD-10 ontology object.
    """

    def __init__(self, db_path: str):
        """
        Initializes the mapper by loading the medical terminology ontology database.

        Args:
            db_path (str): The file path to the SQLite database containing the ontology.
        """
        # Set up the backend to use the specified SQLite database file.
        owl.default_world.set_backend(filename=db_path)

        # Load the PyMedTermino ontology, which contains SNOMED CT and ICD-10.
        pym_ontology = owl.get_ontology("http://PYM/").load()

        # Store references to the SNOMED CT (US edition) and ICD-10 terminologies.
        self.snomedct: owl.Ontology = pym_ontology['SNOMEDCT_US']
        self.icd10: owl.Ontology = pym_ontology['ICD10']

    def _search_snomed_concepts(self, search_term: str) -> List[owl.ThingClass]:
        """
        Searches for SNOMED CT concepts that match a given search term.

        More like a helper method that searches within the 'Clinical finding'
        branch of SNOMED CT for better-targeted results.

        Args:
            search_term (str): The term to search for (e.g., "breast cancer").

        Returns:
            List[owl.ThingClass]: A list of matching SNOMED CT concept objects.
        """
        from owlready2.pymedtermino2.model import TerminologySearcher
        # Initialize the searcher within the clinical finding branch of SNOMED CT.
        # SNOMED CT code 404684003 corresponds to the concept "Clinical finding".
        clinical_finding_concept = self.snomedct[404684003]
        searcher = TerminologySearcher([clinical_finding_concept])

        # Perform the search and return the results, we just strip any extra whitespace. Not sure if it matters.
        return searcher.search(search_term.strip())

    def _get_all_descendants(self, concepts: List[owl.ThingClass]) -> Set[owl.ThingClass]:
        """
        Finds all unique descendant concepts for a given list of parent concepts.

        This private helper method iterates through a list of concepts and
        recursively gathers all of their sub-concepts (children, grandchildren, etc.).

        Args:
            concepts (List[owl.ThingClass]): A list of SNOMED CT concept objects.

        Returns:
            Set[owl.ThingClass]: A set containing all unique descendant concepts.
        """
        all_descendants: Set[owl.ThingClass] = set()
        for concept in concepts:
            # update the set with descendants of the current concept
            all_descendants.update(concept.descendant_concepts())
        return all_descendants

    def map_concepts_to_icd10(self, primary_term: str, refining_term: str) -> pd.DataFrame:
        """
        Performs a refined search for SNOMED CT concepts and maps them to ICD-10.

        The process follows these logical steps:
        1. Finds all concepts related to the `primary_term`.
        2. Gathers all descendants of those initial concepts.
        3. Filters the descendants to only include those whose labels contain the `refining_term`.
        4. Gathers all descendants of this smaller, refined set of concepts.
        5. Maps the final list of concepts to their ICD-10 equivalents.

        Args:
            primary_term (str): The main medical condition to search for (e.g., "breast cancer").
            refining_term (str): A keyword to narrow down the search (e.g., "Hormone receptor positive").

        Returns:
            pd.DataFrame: A DataFrame with columns ['snomed_code', 'snomed_term',
                          'icd10_code', 'icd10_term'].
        """

        # Find initial concepts based on the primary search term.
        initial_concepts = self._search_snomed_concepts(primary_term)
        if not initial_concepts:
            return pd.DataFrame()

        # Get all descendants of the initial concepts.
        all_descendants = self._get_all_descendants(initial_concepts)

        # print all the descendants found for debugging
        print(all_descendants, "<-- all descendants found for primary term")
        print(f"Total descendants found for '{primary_term}': {len(all_descendants)}")

        # Filter these descendants for concepts containing the refining term in their label.
        # we are filtering based on the English label (label.en)

        refined_concepts = [
            concept for concept in all_descendants
            if refining_term in str(concept.label.en)
        ]

        if not refined_concepts:
            # just return an empty dataframe if nothing found.
            return pd.DataFrame()
        
        # Get all descendants of the newly refined list of concepts.
        final_descendants = self._get_all_descendants(refined_concepts)
        # Build a list of records for each SNOMED-to-ICD10 mapping.
        # This approach correctly handles cases where one SNOMED code maps to multiple ICD codes.
        records: List[Dict[str, Any]] = []
        for concept in final_descendants:
            # The '>>' operator in owlready2 is used to find mappings between ontologies.
            icd_variants = concept >> self.icd10
            snomed_term = str(concept.label.en[0]) if concept.label.en else "N/A"

            # Create a record for each SNOMED-ICD10 pair.
            for icd in icd_variants:
                icd_term = str(icd.label.en[0]) if icd.label.en else "N/A"
                records.append({
                    'snomed_code': concept.name,
                    'snomed_term': snomed_term,
                    'icd10_code': icd.name,
                    'icd10_term': icd_term,
                })

        if not records:
            return pd.DataFrame()
        # Convert the list of dictionary records into a pandas DataFrame.
        
        df = pd.DataFrame(records)
        # Remove any duplicate rows and reset the index for a clean output.
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df

# This block ensures the following code only runs when the script is executed directly,
# not when it's imported as a module into another script.
if __name__ == '__main__':

    # use arg parse for search and refine terms (This is optional, you can hardcode them if preferred)
    # see variables below like primary_search and refining_search for where to change them.
    ##########################################################################################
    # just incase we want to change them from the command line. Ops
    # more like  python exercise1.py --search "diabetes" --refine "Type 2"
    # --search is the primary search term (e.g., "breast cancer")
    # --refine is the refining term to narrow down results (e.g., "Hormone receptor positive")
    ##########################################################################################
    parser = argparse.ArgumentParser(description="Map SNOMED CT concepts to ICD-10 codes.")
    parser.add_argument('--search', type=str, required=False, default="breast cancer",
                        help='Primary search term (e.g., "breast cancer").')
    parser.add_argument('--refine', type=str, required=False, default="Hormone receptor positive",
                        help='Refining term to narrow down results (e.g., "Hormone receptor positive").')
    args = parser.parse_args()
    primary_search = args.search
    refining_search = args.refine
    ##########################################################################################

    # Load environment variables from a .env file in the script's directory.
    # The .env file should contain a line like: DATABASE_NAME="your_database.sqlite3"
    load_dotenv()
    db_name = os.getenv('DATABASE_NAME')
    # Check if we need to rebuild the database or build it for the first time.
    rebuild_db = os.getenv('REBUILD_DB')

    # If REBUILD_DB is set to 'True' (case insensitive), we run the setup to create/rebuild the database.
    run_setup() if rebuild_db is True else None

    # Check if the database name is set and if the file actually exists.
    if not db_name or not os.path.exists(db_name):
        print(f"Database file '{db_name}' not found or DATABASE_NAME not set in .env file.")
        print("Please ensure your .env file is configured correctly.")
    else:
        # Instantiate the mapper with the path to the database.
        mapper = SnomedIcd10Mapper(db_path=db_name)

        # Define the search terms.
        primary_search = "breast cancer" if not primary_search else primary_search
        # This is more of refining the code to include search for the hormone receptor positive.
        refining_search = "Hormone receptor positive" if not refining_search else refining_search

        # Call the main method to perform the search and mapping.
        mapped_df = mapper.map_concepts_to_icd10(
            primary_term=primary_search,
            refining_term=refining_search
        )

        # Display the final results.
        print("\n--- Mapping Results ---")
        if mapped_df.empty:
            print("No results to display.")
        else:
            # print it nicely
            print(mapped_df.to_string(index=False))