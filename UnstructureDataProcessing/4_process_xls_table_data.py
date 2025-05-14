import re
from unstructured.partition.xlsx import partition_xlsx

input_filepath = "data.xlsx"

elements = partition_xlsx(filename=input_filepath)

table_data = []

for element in elements:
    print(f"-------------------------------------------------------------------")
    print(f"Processing element of type: {type(element).__name__}")

    if type(element).__name__ == "Table":
        print(f"Element.text:\n{element.text}\n")
        
        raw_text = element.text.strip()
        cells = [c.strip() for c in raw_text.split("\t") if c.strip()]
        print(f"Cells: {cells}")

        # Find first numeric cell
        data_start_index = -1
        for idx, cell in enumerate(cells):
            if cell.isdigit():
                data_start_index = idx
                break

        if data_start_index == -1:
            print("⚠️ Could not detect data rows.")
            continue

        headers = cells[:data_start_index]
        data_cells = cells[data_start_index:]
        
        print(f"Headers: {headers}")
        print(f"Data cells: {data_cells}")

        # Group data_cells into chunks of len(headers)
        for i in range(0, len(data_cells), len(headers)):
            chunk = data_cells[i:i+len(headers)]
            if len(chunk) != len(headers):
                print(f"⚠️ Skipping incomplete row: {chunk}")
                continue
            row = {headers[j]: chunk[j] for j in range(len(headers))}
            table_data.append(row)
    else:
        print("Skipping non-table element.")

if table_data:
    print("\n✅ Extracted table data:")
    for row in table_data:
        print(row)
else:
    print("\n⚠️ No valid table data extracted.")
