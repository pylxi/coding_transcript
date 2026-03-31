"""
CSV Loading Module

Handles CSV file loading with:
- Multiple encoding fallbacks
- Error handling for bad rows
- Timestamp parsing
"""

import pandas as pd


def load_csv_file(file_path):
    """
    Load CSV file with robust error handling
    
    Accepts two formats:
    1. Old format: timestamp, speaker, utterance
    2. New format: speaker, start, end, text
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        DataFrame with columns [speaker, start, end, text]
        (times in seconds, floats)
        
    Raises:
        ValueError: If file cannot be loaded or is invalid
    """
    # Try multiple encodings
    df = None
    for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
        try:
            df = pd.read_csv(
                file_path,
                encoding=encoding,
                on_bad_lines='skip',  # Skip rows with wrong column count
                engine='python'  # More forgiving parser
            )
            break
        except UnicodeDecodeError:
            continue
    
    if df is None:
        raise ValueError("Cannot read file - unsupported encoding")
    
    if len(df) == 0:
        raise ValueError("File is empty or all rows were invalid")
    
    # Check columns (case-insensitive)
    cols_lower = {c.lower().strip(): c for c in df.columns}
    
    # Try new format first: speaker, start, end, text
    new_format_required = {'speaker', 'start', 'end', 'text'}
    old_format_required = {'timestamp', 'speaker', 'utterance'}
    
    has_new_format = all(req in cols_lower for req in new_format_required)
    has_old_format = all(req in cols_lower for req in old_format_required)
    
    if not (has_new_format or has_old_format):
        available = ', '.join(df.columns)
        raise ValueError(
            f"Missing required columns\n\n"
            f"You have: {available}\n\n"
            f"Required (new): speaker, start, end, text\n"
            f"Or (old): timestamp, speaker, utterance"
        )
    
    # Map old columns to new format if needed
    if has_old_format and not has_new_format:
        # Convert old format to new format
        df = df.rename(columns={
            cols_lower['timestamp']: 'timestamp',
            cols_lower['speaker']: 'speaker',
            cols_lower['utterance']: 'text'
        })
        
        # Parse timestamp to seconds
        df['start'] = df['timestamp'].apply(parse_timestamp)
        df['end'] = df['start'] + 1  # Approximate: 1 second per utterance
        df = df[['speaker', 'start', 'end', 'text']]
    else:
        # New format - just rename to lowercase and select columns
        df = df.rename(columns={
            cols_lower['speaker']: 'speaker',
            cols_lower['start']: 'start',
            cols_lower['end']: 'end',
            cols_lower['text']: 'text'
        })
        df = df[['speaker', 'start', 'end', 'text']]
    
    # Remove rows with empty cells
    df = df.dropna(subset=['speaker', 'start', 'end', 'text'])
    
    if len(df) == 0:
        raise ValueError("No valid rows (all have empty cells in required columns)")
    
    # Ensure start and end are floats
    df['start'] = df['start'].astype(float)
    df['end'] = df['end'].astype(float)
    
    return df.reset_index(drop=True)


def parse_timestamp(ts_str: str) -> float:
    """
    Convert timestamp string to seconds
    
    Supports formats:
    - MM:SS (e.g., '00:15', '01:30')
    - HH:MM:SS (e.g., '00:00:15', '01:02:30')
    
    Args:
        ts_str: Timestamp string
        
    Returns:
        float: Total seconds
        
    Raises:
        ValueError: If format is invalid
    """
    try:
        parts = str(ts_str).strip().split(':')
        
        if len(parts) == 3:
            # HH:MM:SS
            h, m, s = map(float, parts)
            return h * 3600 + m * 60 + s
        
        elif len(parts) == 2:
            # MM:SS
            m, s = map(float, parts)
            return m * 60 + s
        
        else:
            raise ValueError(f"Invalid format: {ts_str}")
    
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Cannot parse timestamp '{ts_str}': {str(e)}")
