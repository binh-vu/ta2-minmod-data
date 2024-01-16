import json
import sys
import os


folders = sys.argv[1].split(',') if len(sys.argv) > 1 else []
merged_json_file = sys.argv[2] if len(sys.argv) > 2 else "merged_inferlink.json"

list_of_jsons = []

# Check if folders are provided
if not folders:
    print("No folders provided. Please pass one or more folder paths.")
    sys.exit(1)

for folder_path in folders:
    print(folder_path)
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

    # Check if the file is a JSON file
        if filename.endswith('.json'):
        # Read JSON from the file
            with open(file_path, 'r') as file:
                json_data = json.load(file)

            if 'MineralSite' in json_data:
                list_of_jsons.extend(json_data['MineralSite'])



merged_json = {'MineralSite': list_of_jsons}
with open(merged_json_file, 'w') as file:
    json.dump(merged_json, file, indent=2)

print(f'Merged JSON written to ' + merged_json_file)
