import pandas as pd
import tempfile
import os
from typing import List, Tuple, Optional


def read_excel_utterances(excel_file) -> pd.DataFrame:
    """
    Read dialogue utterances from an Excel file.
    
    Expected columns: 'speaker', 'utterance', 'line_number'
    (Can also work with partial columns - will use available ones)
    
    Args:
        excel_file: File-like object with .name attribute (Gradio UploadedFile)
        
    Returns:
        pd.DataFrame: Dialogue data with speaker and utterance columns
        
    Raises:
        ValueError: If required columns are missing
        FileNotFoundError: If file doesn't exist
    """
    try:
        df = pd.read_excel(excel_file.name)
        
        # Validate required columns
        required_cols = {'speaker', 'utterance'}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"Excel must contain columns: {required_cols}. Found: {set(df.columns)}")
        
        # Add line_number if not present
        if 'line_number' not in df.columns:
            df['line_number'] = range(len(df))
        
        # Clean up: remove rows with missing speaker or utterance
        df = df.dropna(subset=['speaker', 'utterance'])
        df.reset_index(drop=True, inplace=True)
        
        return df
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Excel file not found: {excel_file.name}")
    except Exception as e:
        raise ValueError(f"Error reading Excel file: {str(e)}")


def create_episode_dataframe(
    df: pd.DataFrame, 
    episode_boundaries: List[Tuple[int, int]]
) -> pd.DataFrame:
    """
    Create a dataframe with episode grouping for annotation.
    
    Groups utterances by episode boundaries and creates metadata for each episode.
    
    Args:
        df: DataFrame with utterances (columns: 'speaker', 'utterance')
        episode_boundaries: List of (start_idx, end_idx) tuples defining episode ranges
        
    Returns:
        pd.DataFrame: One row per episode with aggregated utterance data
    """
    if not episode_boundaries:
        raise ValueError("Episode boundaries cannot be empty")
    
    episodes_data = []
    
    for ep_id, (start, end) in enumerate(episode_boundaries):
        # Validate boundary indices
        if start < 0 or end > len(df) or start >= end:
            raise ValueError(f"Invalid boundary for episode {ep_id}: ({start}, {end})")
        
        episode_utterances = df.iloc[start:end]
        
        # Aggregate speakers, handling duplicates
        unique_speakers = episode_utterances['speaker'].unique()
        speaker_list = ', '.join(unique_speakers)
        
        # Join utterances with clear separators
        joined_utterances = ' | '.join(
            f"{row['speaker']}: {row['utterance']}" 
            for _, row in episode_utterances.iterrows()
        )
        
        episodes_data.append({
            'episode_id': ep_id,
            'start_line': start,
            'end_line': end,
            'utterances': joined_utterances,
            'num_utterances': len(episode_utterances),
            'speakers': speaker_list,
            'metacognition_type': '',  # To be filled by annotator
            'confidence': 0.0,  # Model confidence score
            'notes': ''
        })
    
    episodes_df = pd.DataFrame(episodes_data)
    return episodes_df


def export_annotated_data(
    df_episodes: pd.DataFrame, 
    original_file_name: Optional[str] = None
) -> str:
    """
    Export annotated episodes to an Excel file.
    
    Creates a temporary Excel file with the annotated episode data.
    The file is preserved after function returns (caller should clean up).
    
    Args:
        df_episodes: DataFrame with annotated episode data
        original_file_name: Original filename (for reference, not used in output)
        
    Returns:
        str: Path to the output Excel file
        
    Raises:
        IOError: If file writing fails
    """
    try:
        output_file = tempfile.NamedTemporaryFile(
            delete=False, 
            suffix='.xlsx',
            prefix='annotated_episodes_'
        )
        
        # Write with formatting
        with pd.ExcelWriter(output_file.name, engine='openpyxl') as writer:
            df_episodes.to_excel(writer, index=False, sheet_name='Annotated Episodes')
            
            # Adjust column widths for readability
            worksheet = writer.sheets['Annotated Episodes']
            for column in worksheet.columns:
                max_length = max(len(str(cell.value)) for cell in column)
                worksheet.column_dimensions[column[0].column_letter].width = min(max_length + 2, 50)
        
        return output_file.name
        
    except Exception as e:
        raise IOError(f"Error exporting annotated data: {str(e)}")


def validate_episode_annotations(df_episodes: pd.DataFrame) -> Tuple[bool, str]:
    """
    Validate that all required annotations are filled.
    
    Args:
        df_episodes: DataFrame with episode annotations
        
    Returns:
        Tuple[bool, str]: (is_valid, message)
    """
    required_fields = {'metacognition_type'}
    
    # Check for empty required fields
    for field in required_fields:
        if field not in df_episodes.columns:
            return False, f"Missing required column: {field}"
        
        empty_count = df_episodes[field].isna().sum() + (df_episodes[field] == '').sum()
        if empty_count > 0:
            return False, f"{empty_count} episodes missing '{field}' annotation"
    
    return True, "All annotations valid"