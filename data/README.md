# MinMod Knowledge Graph - Data Format

In order to deploy data to the knowledge graph in minmod, the ttl file needs to be in a specific format that follows our data schema design. In order to generate this ttl file, we would be requiring our stakeholders to submit data in a specific json format, that follow a certain structure, data types, domain and ranges for the values.
This documentation is to highlight the requirements for any data json being sent

The json files should be uploaded to the following folders:

1. [UMN](umn)
2. [SRI](sri)
3. [Inferlink](inferlink)

Commodities, deposit types, and unit names URI's need to match minmod URI's. The list of currently added entities:

1. [Commodities](https://github.com/DARPA-CRITICALMAAS/ta2-minmod-data/blob/main/data/entities/commodities/minmod_commodities.csv)
2. [Deposit Types](https://github.com/DARPA-CRITICALMAAS/ta2-minmod-data/blob/main/data/entities/depositTypes/minmod_deposit_types.csv)
3. [Units](https://github.com/DARPA-CRITICALMAAS/ta2-minmod-data/blob/main/data/entities/units/minmod_units.csv)

New entities can be added by TA2 Minmod group if required.

#### Structure of the file

The structure of the file will be similar to the example file - [example_json_file](example_mine.json)

#### Required Fields and Data types
The data types and required fields in the json are highlighted in [schema_file](datatypes.json)

#### Domain and Ranges

The domain and ranges of the json keys are highlighted as follows

- Mineral Site
  * id: ---decide---
  * name: Any valid mineral site name
  * same_as: 
    * source: source of the mineral site
    * record_id: the record id of the mineral site in the source
  * date: Date, in the 'dd-mm-YYYY' format
  * location_info
    * location: latitude longitude represented as 'POINT (Lat Long)' in EPSG:4326 format
    * country: valid name of a country
    * state_or_province: valid state or province
    * location_source_record_id: the id of the location in the source being referred to extract location
    * location_source: valid data source, eg MRDS, MINDAT etc
    * crs: 
  * geology_info:
    * age: 
    * process: 
    * lithology: 
    * comments: comments on the geology info of mineral site
    * description: description of the geology info of mineral site
    * environment:
    * unit_name: 
  * deposit_type: URI of deposit types in minmod, eg "id": "https://minmod.isi.edu/resource/Q24". List of possible deposit types and their minmod ids are defined in [deposit types](https://github.com/DARPA-CRITICALMAAS/ta2-minmod-data/blob/main/data/entities/depositTypes/minmod_deposit_types.csv)
  * MineralInventory
    * id: ---decide---
    * commodity: URI of commodity in minmod, eg "id": "https://minmod.isi.edu/resource/Q589". List of possible commodities and their minmod ids are defined in [commodities](https://github.com/DARPA-CRITICALMAAS/ta2-minmod-data/blob/main/data/entities/commodities/minmod_commodities.csv)
    * ore
      * ore_unit: URI of ore unit in minmod, eg "id": "https://minmod.isi.edu/resource/Q200". List of possible unit names and their minmod ids are defined in [unit names](https://github.com/DARPA-CRITICALMAAS/ta2-minmod-data/blob/main/data/entities/units/minmod_units.csv)
      * ore_value: Value of ore in units, decimal value
    * grade
      * grade_unit: URI of grade unit in minmod, eg "id": "https://minmod.isi.edu/resource/Q201". List of possible unit names and their minmod ids are defined in [unit names](https://github.com/DARPA-CRITICALMAAS/ta2-minmod-data/blob/main/data/entities/units/minmod_units.csv)
      * grade_value: Value of grade in units, decimal value
    * cutoff_grade
      * grade_unit: URI of grade unit in minmod, eg "id": "https://minmod.isi.edu/resource/Q201". List of possible unit names and their minmod ids are defined in [unit names](https://github.com/DARPA-CRITICALMAAS/ta2-minmod-data/blob/main/data/entities/units/minmod_units.csv)
      * grade_value: Value of grade in units, decimal value
    * reference
      * id: ---decide---
      * document
        * id: ---decide---
        * title: Title of the document 
        * doi: doi of the document 
        * uri: URI of the document, if it does not have a doi
        * authors: list of the authors of the document, list of strings
        * journal: journal document belongs to
        * year: Published year of the document, in YYYY
        * month: Published month of the document, in m/mm
        * volume: Volume of the document, integer
        * issue: Issue number of the document, integer
        * description: Description of the document
      * page_info: Information about the page where reference of inventory is taken from
        * page: Page number of the document
        * bounding_box
          * x_min: x axis, minimum value, decimal value
          * x_max: x axis, maximum value, decimal value
          * y_min: y axis, minimum value, decimal value
          * y_max: y axis, maximum value, decimal value
     