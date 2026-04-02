import csv
import io

def validate_csv_file(file):
    if not file.filename.endswith('.csv'):
        return False, 'File must be a CSV file (.csv)', {}
    
    try:
        stream = io.TextIOWrapper(file.stream, encoding='utf-8')
        csv_reader = csv.reader(stream)
        rows = list(csv_reader)
        
        if len(rows) == 0:
            return False, 'CSV file is empty', {}
        
        if len(rows) > 0:
            columns = len(rows[0])
            row_count = len(rows) - 1
            
            return True, f'Valid CSV file with {columns} columns', {
                'rows': row_count,
                'columns': columns
            }
        
    except Exception as e:
        return False, f'Error reading CSV file: {str(e)}', {}
    
    return False, 'Unknown error validating file', {}
