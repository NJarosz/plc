import json
EMPLOYEE_INFO_FILE = "/home/pi/Documents/employee_info.txt"
PRODUCTION_INFO_FILE = "/home/pi/Documents/production_info.txt"
TOTALCOUNT_FILE = "/home/pi/Documents/totalcount.txt"

def convert_to_json(input_file, output_file):
    data = {}
    with open(input_file, 'r') as f:
        for line in f:
            print(line)
            # Strip whitespace and split by comma
            key, value = line.split(',')
            # Create dictionary for each line
            data[key.strip()]=value.strip()

    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    input_files = [PRODUCTION_INFO_FILE, EMPLOYEE_INFO_FILE, TOTALCOUNT_FILE]
    output_files = ["./data/production.json", "./data/employees.json", "./data/totalcount.json"]
    for i in range(len(input_files)):
        convert_to_json(input_files[i], output_files[i])
