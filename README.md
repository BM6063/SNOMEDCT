# Exercise
Query SNOMED-CT for breast cancer SNOMED-CT codes
Refine to find codes for hormone positive breast cancer

-   Submit your all code steps with comments.
-   Provide the data table containing breast cancer-related ICD-10 codes and descriptions derived from SNOMED CT mappings.


# R
Enclosing R code (quatro markdown) using the R package Rdiagnosislist to query SNOMED-CT.  Other R packages that might be useful are snomedizer (R interface to the SNOMED CT Terminology Server REST API) or https://github.com/ropensci/trud. (Inferface to NHS TRUD API to programmatically download SNOMED and other NHS reference data directly ) 



# Python
If you do not wish to use, R.  You can develop similar code in python Libraries and resources include

A Python equivalent for working with SNOMED CT similar to the R repository you have (https://github.com/BM6063/SNOMEDCT) can be built using libraries such as PyMedTermino or Pathling:

**1. PyMedTermino**
Offers Python bindings to access SNOMED CT concepts, relationships, and ontological queries.
Allows you to load SNOMED CT ontologies and search concepts by code or description.
Supports accessing synonyms, parents, children, and associated clinical findings.

Example snippet:

python
from pymedtermino.snomedct import *
SNOMEDCT.load()


concept = SNOMEDCT[254837009]
print(concept)
print(concept.definition)
print(concept.parents)
Documentation: https://pythonhosted.org/PyMedTermino/

**2. Pathling (Python API)**
Library to analyze and group SNOMED CT concepts with a terminology server backend.
Works with Spark for scalable data pipelines.
Allows you to query value sets, explore hierarchies, and display SNOMED terms.

Example snippet:

python
from pathling import PathlingContext

pc = PathlingContext.create()
df = pc.spark.read.csv("snomed_data.csv", header=True)
df = df.withColumn("Snomed Term", pc.snomed.display("concept_column"))
df.show()
Tutorial: https://pathling.csiro.au/docs/libraries/examples/grouping-snomed

**3. Using REST APIs like Snowstorm**
Snowstorm API offers RESTful services to query SNOMED concepts, relationships, and maps.
You can use Python libraries like requests to query and retrieve SNOMED data.

Example snippet:

python
import requests

url = "https://snowstorm.example.com/fhir/CodeSystem/$lookup?code=254837009"
response = requests.get(url)
print(response.json())

GitHub project: https://github.com/AberystwythSystemsBiology/SCTTSRApy


