import json
from ..config import EMPLOYEE_INFO_FILE, PRODUCTION_INFO_FILE, TOTAL_COUNT_FILE



def convert_to_json(input_file, output_file):
    data = []
    with open(input_file, 'r') as f:
        for line in f:
            # Strip whitespace and split by comma
            key, value = line.strip().split(',')
            # Create dictionary for each line
            data.append({"key": key.strip(), "value": value.strip()})

    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    input_files = [PRODUCTION_INFO_FILE, EMPLOYEE_INFO_FILE, TOTAL_COUNT_FILE]
    output_files = ["production.json", "employees.json", "totalcount.json"]
    for i in range(len(input_files)):
        convert_to_json(input_files[i], output_files[i])
