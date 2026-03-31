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
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        DataFrame with columns [timestamp, speaker, utterance, timestamp_seconds]
        
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
    cols_lower = [c.lower().strip() for c in df.columns]
    required = {'timestamp', 'speaker', 'utterance'}
    
    if not all(req in cols_lower for req in required):
        available = ', '.join(df.columns)
        raise ValueError(
            f"Missing required columns\n\n"
            f"You have: {available}\n\n"
            f"Required: timestamp, speaker, utterance"
        )
    
    # Rename columns to lowercase for consistency
    col_mapping = {}
    for col in df.columns:
        lower = col.lower().strip()
        if lower in required:
            col_mapping[col] = lower
    df = df.rename(columns=col_mapping)
    
    # Remove rows with empty cells in required columns
    df = df.dropna(subset=['timestamp', 'speaker', 'utterance'])
    
    if len(df) == 0:
        raise ValueError("No valid rows (all have empty cells in required columns)")
    
    # Parse timestamps and add timestamp_seconds column
    df['timestamp_seconds'] = df['timestamp'].apply(parse_timestamp)
    
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
