import json
import jsonschema
import sys
import requests
import uuid
import os
import generate_uris
import base64
import subprocess
import validate_pyshacl

def get_sha(repo, path, branch):

    url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={branch}"
    print(url)
    response = requests.get(url)

    if response.status_code == 200:
        content = response.json()
        return content['sha']
    else:
        print(f"Error: {response.status_code}")
        return None

    sha = None

    # Check if the request was successful
    if response.status_code == 200:
        # File exists, update it
        sha = response.json()['sha']
        return sha
    else:
        # File doesn't exist, create it
        sha = None
    return sha

def is_json_file(file_path):
    path, file_extension = os.path.splitext(file_path)
    print(str(path))
    split_path = path.split('/')
    is_under_data_folder = False
    if len(split_path) == 2 and split_path[0] == 'inferlink':
        print('This is under data folder')
        is_under_data_folder = True

    return is_under_data_folder and file_extension.lower() == '.json'

def file_datasource(file_path):
    path, file_extension = os.path.splitext(file_path)
    split_path = path.split('/')
    if len(split_path) == 2 and split_path[0] == 'inferlink':
        print('This is under data folder')
        return split_path[0]
    return ''


def run_drepr_on_file(datasource):
    destination = 'generated_files/ttl_files/'
    model_file = 'data/generator/model.yml'
    command = f' python -m drepr -r {model_file} -d default="{datasource}"'
    print('Running ... ', command)

    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        output_lines = result.stdout.splitlines()[2:]  # Skip the first two lines
        return '\n'.join(output_lines)
    except subprocess.CalledProcessError as e:
        print("Error executing command:", e)
        print("Command output (if any):", e.output)
        return ''

def create_drepr_update_github(file_path, filename):
    file_content = run_drepr_on_file(file_path)
    pull_request_number = os.environ.get('GITHUB_REF').split('/')[-2]
    github_token = os.environ.get('GITHUB_TOKEN')
    print(github_token)
    print(os.environ.get('GITHUB_REF'))

    generated_ttl_path = f'generated_files/ttl_files/{filename}.ttl'
    headers = {
        'Authorization': f'Bearer {github_token}',
        'Content-Type': 'application/json',
    }
    # owner, repo, path, branch
    repo = os.environ["GITHUB_REPOSITORY"]
    branch = os.environ["GITHUB_HEAD_REF"]
    url = f'https://api.github.com/repos/{os.environ["GITHUB_REPOSITORY"]}/contents/{generated_ttl_path}'
    print(url)

    # TODO: Implement getting existing auto generated files, Does not currently work
    # existing_sha = get_sha(repo, file_path, branch)

    validated_drepr = validate_pyshacl.validate_using_shacl(file_content)

    if not validated_drepr:
        print('Validation failed for pyshacl')
        raise

    encoded_content = base64.b64encode(file_content.encode()).decode()
    payload = {
        'message': 'Update file via GitHub Actions',
        'content': encoded_content,
        'branch': branch,
        'sha':None
    }

    # Make the API request to update the file
    response = requests.put(url, headers=headers, json=payload)

    if response.status_code == 200 or response.status_code == 201:
        print(f'Successfully updated file in pull request #{pull_request_number}')
    else:
        print(f'Failed to update file. Status code: {response.status_code}, Response: {response.text}')

    return

def create_drepr_from_workflow1(file_path, filename):
    print('In the 2nd file', file_path, filename)
    generated_json_path = f'generated_files/json_files/{filename}.json'

    with open(file_path, 'r') as file:
        file_contents = file.read()
    print("File Contents After Printing:")
    print(file_contents)

    create_drepr_update_github(file_path, filename)

