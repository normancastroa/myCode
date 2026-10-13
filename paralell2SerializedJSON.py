import json

def main():
    try:
        # Grab our input parameter from XSOAR arguments
        parallel_data = demisto.args().get('paralellJSON')
        
        if not parallel_data:
            return_error("⚠️ Oops! The 'paralellJSON' parameter is missing or empty. Please provide some data to convert.")

        records = []
        
        # Let's break down the input text line-by-line (handling line-delimited/NDJSON format)
        print("Reading through the parallel JSON lines...")
        for line_num, line in enumerate(parallel_data.splitlines(), 1):
            cleaned_line = line.strip()
            
            # Skip any empty lines so they don't break our parser
            if not cleaned_line:
                continue
            
            try:
                # Parse each line independently as its own JSON object
                record = json.loads(cleaned_line)
                records.append(record)
            except json.JSONDecodeError as err:
                print(f"⚠️ Heads up: Malformed JSON on line {line_num}. Skipping it! Error: {err}")

        # Serialize the collected records into a clean, standard JSON string array
        print(f"Successfully processed {len(records)} records. Serializing...")
        serialized_output = json.dumps(records, indent=4, ensure_ascii=False)

        # Return the result back to Cortex XSOAR so it populates 'serializedJSON'
        return_results(
            CommandResults(
                outputs_prefix='JSONSerializer',
                outputs_key_field='',
                outputs={'serializedJSON': serialized_output},
                readable_output=f"### ✅ Successfully serialized {len(records)} records into standard JSON!"
            )
        )

    except Exception as ex:
        return_error(f"❌ Well, that didn't go as planned. Error: {str(ex)}")

if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
