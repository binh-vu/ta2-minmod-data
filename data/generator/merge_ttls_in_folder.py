from rdflib import Graph
import sys
import os


def combine_graphs(infiles: list[str], outfile: str):
    g = Graph()
    for infile in infiles:
        g.parse(infile, format="turtle")

    g.serialize(outfile, format="turtle")
    return g


def get_files_in_folder(folder_path):
    try:
        # Get a list of all files in the specified folder
        files_list = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file))]
        return files_list
    except Exception as e:
        print(f"Error: {e}")
        return []

folder_path = sys.argv[1]

# Get the array of file paths in the specified folder
files_array = get_files_in_folder(folder_path)

merged_json_file = sys.argv[2] if len(sys.argv) > 2 else "merged_inferlink.ttl"

with open(merged_json_file, "w") as file:
    file.write("")

print(files_array)
print(merged_json_file)

combine_graphs(files_array, merged_json_file)

