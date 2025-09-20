import os
from typing import List
from owlready2 import default_world
from owlready2.pymedtermino2.umls import import_umls
from dotenv import load_dotenv

def setup_umls_ontology(umls_data_dir: str, db_path: str, terminologies: List[str] = None, build: bool = True):
    """
    Initializes and builds a medical ontology database from UMLS data files.

    This function configures owlready2 to use an SQLite backend, imports specified
    medical terminologies (like SNOMED CT and ICD-10) from the UMLS Release
    Format (RRF) files, and saves the resulting ontology to the database file.

    Args:
        umls_data_dir (str): The file path to the directory containing the UMLS
                             'META' sub-directory.
        db_path (str): The desired file path for the output SQLite database.
        terminologies (List[str], optional): A list of terminology names to import.
                                             Defaults to ['SNOMEDCT_US', 'ICD10', 'CUI'].
        build (bool, optional): If True, builds the ontology from UMLS data.

    Raises:
        FileNotFoundError: If the umls_data_dir does not exist or is not a valid directory.
    """
    # Set default terminologies if none are provided by the user.
    if terminologies is None:
        terminologies = ['SNOMEDCT_US', 'ICD10', 'CUI']

    # Validate that the UMLS data directory exists before proceeding.
    if not os.path.isdir(umls_data_dir):
        raise FileNotFoundError(
            f"The specified UMLS data directory does not exist: {umls_data_dir}"
        )

    print(f"Setting up ontology database at: {db_path}")
    # Set the backend for owlready2 to use the specified SQLite file for storage.
    default_world.set_backend(filename=db_path)
    # Import the UMLS data. This core function from PyMedTermino reads the
    # UMLS RRF files and constructs the ontology structure in memory.
    import_umls(umls_data_dir, terminologies)

    print("Saving the ontology to the database file...")
    # Persist all the imported data from memory into the SQLite database file.
    default_world.save()
    print(f"Ontology setup complete! Database saved at '{db_path}'.")


# This block runs only when the script is executed directly
def run_setup():
    # Load environment variables from a local .env file.
    # Your .env file should look like this:
    # UMLS_DATA_DIR="path/to/your/2023AB-full/2023AB/META"
    # DATABASE_NAME="umls_ontology.sqlite3"
    load_dotenv()

    # Retrieve the paths from the loaded environment variables.
    # Get the UMLS data directory from the environment variables.
    # downloaded from https://www.nlm.nih.gov/research/umls/licensedcontent/umlsknowledgesources.html
    umls_dir = os.getenv('UMLS_DATA_DIR')
    db_name = os.getenv('DATABASE_NAME')

    # --- Pre-execution Checks ---
    if not umls_dir or not db_name:
        print("UMLS_DATA_DIR or DATABASE_NAME is not set in your .env file.")
        print("Please create a .env file and add these variables before running.")
    # Prevent accidental overwriting of an existing database.
    elif os.path.exists(db_name):
        print(f"Database '{db_name}' already exists. Skipping setup.")
        print("If you need to rebuild it, please delete the file and run this script again.")
    else:
        try:
            # Execute the function to build and save the ontology database.
            setup_umls_ontology(
                umls_data_dir=umls_dir,
                db_path=db_name
                # You can optionally override the default terminologies like this:
                # terminologies=['SNOMEDCT_US', 'ICD10CM', 'RxNorm']
            )
        except FileNotFoundError as e:
            print(f"SETUP FAILED: {e}")
        except Exception as e:
            # Catch any other unexpected errors during the process.
            print(f"An unexpected error occurred: {e}")