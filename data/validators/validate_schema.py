import json
from jsonschema import validate

schema = {
    "type": "object",
    "properties" : {
        "MineralSite": {
            "type": "array",
            "items": {
                "type": "object",
                "properties" : {
                    "id" : {"type" : "number"},
                    "name" : {"type" : "string"},
                    "location_info": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "country": {"type": "string"},
                            "state_or_province": {"type": "string"},
                            "location_source_record_id": {"type": "string"},
                            "crs": {"type": "string"},
                            "location_source": {"type": "string"}
                        }
                    },
                    "deposit_type" : {"type" : "string"},
                    "geology_info": {
                        "type": "object",
                        "properties": {
                            "age": {"type": "string"},
                            "unit_name": {"type": "string"},
                            "description": {"type": "string"},
                            "lithology": {"type": "string"},
                            "process": {"type": "string"},
                            "comments": {"type": "string"},
                            "environment": {"type": "string"}
                        }
                    },
                    "MineralInventory": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "number"},
                                "category": {"type": "string"},
                                "contained_metal": {"type": "number"},
                                "reference": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "number"},
                                        "document": {
                                            "type": "object",
                                            "properties": {
                                                "id": {"type": "string"},
                                                "title": {"type": "string"},
                                                "doi": {"type": "string"},
                                                "uri": {"type": "string"},
                                                "journal": {"type": "string"},
                                                "year": {"type": "number"},
                                                "month": {"type": "number"},
                                                "volume": {"type": "number"},
                                                "issue": {"type": "number"},
                                                "description": {"type": "string"},
                                                "authors": {
                                                    "type": "array",
                                                    "items": {"type": "string"}
                                                }
                                            },
                                            "required": ["id"]

                                        },
                                        "page_info": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "page": {"type": "number"},
                                                    "bounding_box": {
                                                        "type": "object",
                                                        "properties": {
                                                            "x_min": {"type": "number"},
                                                            "x_max": {"type": "number"},
                                                            "y_min": {"type": "number"},
                                                            "y_max": {"type": "number"}
                                                        },
                                                        "required": ["x_min", "x_max", "y_min", "y_max"]
                                                    }
                                                },
                                                "required": ["page"]
                                            }

                                        }
                                    },
                                    "required": ["id"]
                                },
                                "date": {"type": "string", "format": "date"},
                                "commodity": {"type": "string"},
                                "ore": {
                                    "type": "object",
                                    "properties": {
                                        "ore_unit": {"type": "string"},
                                        "ore_value": {"type": "number"}
                                    },
                                    "required": ["ore_unit", "ore_value"]
                                },
                                "grade": {
                                    "type": "object",
                                    "properties": {
                                        "grade_unit": {"type": "string"},
                                        "grade_value": {"type": "number"}
                                    }
                                    ,
                                    "required": ["grade_unit", "grade_value"]
                                },
                                "cutoff_grade": {
                                    "type": "object",
                                    "properties": {
                                        "grade_unit": {"type": "string"},
                                        "grade_value": {"type": "number"}
                                    },
                                    "required": ["grade_unit", "grade_value"]
                                }
                            },
                            "required": ["id"]
                        }
                    },
                    "same_as" : {"type" : "string"}
                },
                "required": ["id", "name"]
            }
        }
    }
}

with open('../inferlink/empireState.json') as file:
    json_data = json.load(file)
json_string = json.dumps(json_data)
mineral_site_json = json.loads(json_string)
validate(instance=mineral_site_json, schema=schema)
print(mineral_site_json)