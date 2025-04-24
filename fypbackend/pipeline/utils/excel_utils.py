import pandas as pd
import json

def convert_excel_to_json(excel_file_path, json_file_path):
    """
    Converts Excel file to JSON format.
    """
    df = pd.read_excel(excel_file_path)
    data_list = df.to_dict(orient='records')

    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(data_list, json_file, indent=4, ensure_ascii=False)

    return f"Data successfully written to {json_file_path}"
