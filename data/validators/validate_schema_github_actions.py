import json
import jsonschema
import sys
import requests
import uuid
import os
import generate_uris
import base64
import create_ttl_files
import validators

def is_valid_uri(uri):
    return validators.url(uri)

def get_sha(file_path):
    repository = os.environ["GITHUB_REPOSITORY"]
    url = f'https://api.github.com/repos/{repository}/contents/{file_path}'
    headers = {
        'Authorization': f'Bearer {os.environ["GITHUB_TOKEN"]}',
        'Accept': 'application/vnd.github.v3+json',
    }
    response = requests.get(url, headers=headers)
    sha = None
    print(url)
    if response.status_code == 200:
        sha = response.json()['sha']
        return sha
    else:
        sha = None
    return sha


def mineral_site_uri(data):
    response = generate_uris.mineral_site_uri(data)
    uri = ''
    print(response)
    uri = response['result']
    return uri

def document_uri(data):
    response = generate_uris.document_uri(data)
    uri = ''
    print(response)
    uri = response['result']
    return uri

def mineral_inventory_uri(param1):
    response = generate_uris.mineral_inventory_uri(param1)
    uri = ''
    print(response)
    uri = response['result']
    return uri

def is_json_file_under_data(file_path):
    path, file_extension = os.path.splitext(file_path)
    print(str(path), file_path)
    split_path = path.split('/')
    is_under_data_folder = False
    print(split_path[-3], split_path[-2])
    if len(split_path) > 0:
        if (len(split_path) > 3 and split_path[-4] == 'data' and split_path[-3] == 'inferlink' and split_path[-2] == 'extractions') \
                or (len(split_path) > 2 and split_path[-2] == 'umn'):
            print('This is under data folder')
            is_under_data_folder = True

    return is_under_data_folder and file_extension.lower() == '.json'

def get_filename(file_path):
    path, file_extension = os.path.splitext(file_path)
    split_path = path.split('/')
    if len(path) > 0:
        return split_path[-1]

def file_datasource(file_path):
    path, file_extension = os.path.splitext(file_path)
    split_path = path.split('/')
    if len(split_path) == 2 and split_path[0] == 'inferlink':
        print('This is under data folder')
        return split_path[0]
    return ''



def update_pull_request(file_content, file_path):
    pull_request_number = os.environ.get('GITHUB_REF').split('/')[-2]
    github_token = os.environ.get('GITHUB_TOKEN')

    print(github_token)
    print(os.environ.get('GITHUB_REF'))

    url = f'https://api.github.com/repos/{os.environ["GITHUB_REPOSITORY"]}/pulls/{pull_request_number}/files/{file_path}'
    url2 = "https://api.github.com/repos/:owner/:repo/pulls/:number"
    headers = {
        'Authorization': f'Bearer {github_token}',
        'Content-Type': 'application/json',
    }
    # owner, repo, path, branch
    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ["GITHUB_HEAD_REF"]
    existing_sha = get_sha(file_path)

    path, file_extension = os.path.splitext(file_path)
    split_path = path.split('/')
    filename = split_path[-1]

    generated_json_path = f'generated_files/json_files/{filename}.json'

    print(branch, existing_sha)
    url = f'https://api.github.com/repos/{os.environ["GITHUB_REPOSITORY"]}/contents/{generated_json_path}'
    print(url)
    encoded_content = base64.b64encode(file_content.encode()).decode()
    payload = {
        'message': 'Update file via GitHub Actions',
        'content': encoded_content,
        'sha': existing_sha,
        'branch': branch
    }

    # Make the API request to update the file
    response = requests.put(url, headers=headers, json=payload)

    if response.status_code == 200 or response.status_code == 201:
        print(f'Successfully updated file in pull request #{pull_request_number}')
    else:
        print(f'Failed to update file. Status code: {response.status_code}, Response: {response.text}')

def validate_json_schema(filename):
    try:
        with open(filename, 'r') as file:
            data_graph = file.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    schema = {
        "type": "object",
        "properties" : {
            "MineralSite": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties" : {
                        "id" :  {"type": ["string", "number"]},
                        "name" : {"type" : "string"},
                        "source_id" : {"type" : "string"},
                        "record_id" : {"type" : "number"},
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
                        "deposit_type" : {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"}
                                }
                            }
                        },
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
                                    "id": {"type": ["string", "number"]},
                                    "category": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "contained_metal": {"type": "number"},
                                    "reference": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "number"},
                                            "document": {
                                                "type": "object",
                                                "properties": {
                                                    "id":  {"type": ["string", "number"]},
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
                                                }
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
                                                                "x_min": {"type": ["string", "number"]},
                                                                "x_max": {"type": ["string", "number"]},
                                                                "y_min": {"type": ["string", "number"]},
                                                                "y_max": {"type": ["string", "number"]}
                                                            },
                                                            "required": ["x_min", "x_max", "y_min", "y_max"]
                                                        }
                                                    },
                                                    "required": ["page"]
                                                }

                                            }
                                        }
                                    },
                                    "date": {"type": "string", "format": "date"},
                                    "commodity": {"type": "string"},
                                    "ore": {
                                        "type": "object",
                                        "properties": {
                                            "ore_unit": {"type": "string"},
                                            "ore_value": {"type": "number"}
                                        }
                                    },
                                    "grade": {
                                        "type": "object",
                                        "properties": {
                                            "grade_unit": {"type": "string"},
                                            "grade_value": {"type": "number"}
                                        }

                                    },
                                    "cutoff_grade": {
                                        "type": "object",
                                        "properties": {
                                            "grade_unit": {"type": "string"},
                                            "grade_value": {"type": "number"}
                                        }
                                    }
                                },
                                "required": ["reference"]

                            }
                        }
                    },
                    "required": ["name"]
                },
                "required": ["source_id", "record_id"]
            }
        }
    }

    with open(filename) as file:
        json_data = json.load(file)
    json_string = json.dumps(json_data)
    mineral_site_json = json.loads(json_string)

    try:
        jsonschema.validate(instance=mineral_site_json, schema=schema)
        print("Validation succeeded")
    except jsonschema.ValidationError as e:
        print(f"Validation failed: {e}")
        raise  # Raise an exception to indicate failure

    return json_data


changed_files = sys.argv[1]
temp_file = sys.argv[2]

print('Running this')
print(changed_files, temp_file)

file_path = changed_files
if is_json_file_under_data(file_path):
    print(f'{file_path} is a JSON file')
    json_data = validate_json_schema(file_path)
    # json_data=''
    # with open(file_path) as file:
    #     json_data = json.load(file)

    # json_string = json.dumps(json_data)
    # mineral_site_json = json.loads(json_string)

    ms_list = json_data['MineralSite']
    mndr_url = 'https://minmod.isi.edu/resource/'

    for ms in ms_list:
        ms['id'] = mndr_url + mineral_site_uri(ms)
        if "location_info" in ms:
            ll = ms["location_info"]
            if "state_or_province" in ll and ll["state_or_province"] is None:
                ll["state_or_province"] = ""

        if "MineralInventory" in ms:
            mi_list = ms['MineralInventory']
            counter = 0

            for mi in mi_list:
                if "category" in mi:
                    for dp in mi['category']:
                        is_valid_uri(dp)

                if "commodity" in mi:
                    is_valid_uri(mi['commodity'])

                if "ore" in mi:
                    if "ore_unit" in mi['ore']:
                        ore = mi['ore']
                        is_valid_uri(ore['ore_unit'])

                if "grade" in mi:
                    if "grade_unit" in mi['grade']:
                        grade = mi['grade']
                        is_valid_uri(grade['grade_unit'])

                if "cutoff_grade" in mi:
                    if "grade_unit" in mi['cutoff_grade']:
                        cutoff_grade = mi['cutoff_grade']
                        is_valid_uri(cutoff_grade['grade_unit'])

                mi_data = {
                    "site": ms,
                    "id": counter
                }
                mi['id'] = mndr_url + mineral_inventory_uri(mi_data)
                counter += 1

                if "reference" in mi:
                    reference = mi['reference']
                    if "document" in reference:
                        document = reference['document']
                        doc_data = {
                            "document": document
                        }
                        document['id'] = mndr_url + document_uri(doc_data)


    # update_pull_request(json.dumps(json_data, indent=2), file_path)
    print(json.dumps(json_data, indent=2))
    filename = get_filename(file_path)
    with open(file_path, 'w') as file:
        # Write the new data to the file
        file.write(json.dumps(json_data, indent=2) + '\n')

    # with open(temp_file, 'a') as file:
    #     # Write the new data to the file
    #     file.write(json.dumps(json_data, indent=2) + '\n')
    create_ttl_files.create_drepr_from_workflow1(file_path, filename)





else:
    print(f'{file_path} is not a JSON file')


# print(type(json_data))