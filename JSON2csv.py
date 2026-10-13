import demistomock as demisto
from CommonServerPython import *
from CommonServerUserPython import *
import csv
import io
import json

def flatten_json(nested_json, separator='.'):
    """
    Recursively flattens a nested JSON object/list into a single-level dictionary.
    Example: {'user': {'name': 'Alice'}} -> {'user.name': 'Alice'}
    """
    out = {}
    
    def flatten(x, name=''):
        if isinstance(x, dict):
            for a in x:
                flatten(x[a], name + a + separator)
        elif isinstance(x, list):
            for i, a in enumerate(x):
                flatten(a, name + str(i) + separator)
        else:
            out[name[:-1]] = x

    flatten(nested_json)
    return out

def main():
    try:
        # Retrieve the JSON data from script arguments
        args = demisto.args()
        raw_data = args.get('json_data', '{}')
        
        # Parse JSON string if passed as a string
        if isinstance(raw_data, str):
            parsed_data = json.loads(raw_data)
        else:
            parsed_data = raw_data

        # Normalize data into a list of flattened dictionaries
        if isinstance(parsed_data, dict):
            data_list = [flatten_json(parsed_data)]
        elif isinstance(parsed_data, list):
            data_list = [
                flatten_json(item) if isinstance(item, dict) else {'value': item} 
                for item in parsed_data
            ]
        else:
            raise ValueError("Input JSON must be a valid JSON object (dictionary) or array (list).")

        if not data_list:
            return_results("The provided JSON is empty. No CSV file was generated.")
            return

        # Extract all unique headers across all objects to ensure no keys are missed
        headers = sorted(list(set(key for row in data_list for key in row.keys())))

        # Write data to an in-memory CSV buffer
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        for row in data_list:
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()

        # Return the CSV file as an XSOAR War Room entry/attachment
        return_results(fileResult('converted_output.csv', csv_content))

    except Exception as ex:
        return_error(f"Failed to convert JSON to CSV: {str(ex)}")

if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
