"""
Discourse Segmentation Module - Grosz & Sidner Stack Model with Bookmarking

Implements Grosz & Sidner (1986) intentional stack model for episode segmentation.
Uses GPT-4 for discourse analysis with collaboration dimension classification.
Includes bookmarking system for handling large transcripts across chunks.
"""

import os
import json
import pandas as pd
from openai import OpenAI
from typing import List, Tuple, Dict, Any, Optional


# ================================================================================
# 1. PREPROCESSING (time & speaker patterns only - no content analysis)
# ================================================================================

def split_by_time(df: pd.DataFrame, chunk_duration: float = 600.0) -> List[Tuple[int, int]]:
    """
    Split the dialogue into chunks of approximately chunk_duration seconds.
    Returns list of (start_idx, end_idx) inclusive.
    
    Args:
        df: DataFrame with 'start' and 'end' columns (in seconds)
        chunk_duration: Target duration per chunk in seconds
        
    Returns:
        List of (start_idx, end_idx) tuples for each chunk
    """
    chunks = []
    start_idx = 0
    current_duration = 0.0
    
    for i in range(len(df)):
        turn_dur = df.loc[i, 'end'] - df.loc[i, 'start']
        if current_duration + turn_dur > chunk_duration and i > start_idx:
            chunks.append((start_idx, i-1))
            start_idx = i
            current_duration = turn_dur
        else:
            current_duration += turn_dur
    
    if start_idx < len(df):
        chunks.append((start_idx, len(df)-1))
    
    return chunks


def detect_monologues_without_content(df: pd.DataFrame, min_duration: float = 30.0) -> List[Tuple[int, int, float]]:
    """
    Returns list of (start_idx, end_idx, total_duration) for monologues,
    based only on speaker and timestamps (no content analysis).
    
    Args:
        df: DataFrame with 'speaker', 'start', 'end' columns
        min_duration: Minimum monologue duration in seconds
        
    Returns:
        List of (start_idx, end_idx, duration) tuples
    """
    monologues = []
    current_speaker = None
    start_idx = None
    accum_duration = 0.0

    for i, row in df.iterrows():
        speaker = row['speaker']
        turn_duration = row['end'] - row['start']

        if speaker == current_speaker:
            accum_duration += turn_duration
        else:
            if current_speaker is not None and accum_duration >= min_duration:
                monologues.append((start_idx, i-1, accum_duration))
            current_speaker = speaker
            start_idx = i
            accum_duration = turn_duration

    if current_speaker is not None and accum_duration >= min_duration:
        monologues.append((start_idx, len(df)-1, accum_duration))

    return monologues


def detect_overlaps_without_content(df: pd.DataFrame, overlap_threshold: float = 0.5) -> List[Tuple[int, int, float]]:
    """
    Returns overlaps based only on timestamps.
    
    Args:
        df: DataFrame with 'start' and 'end' columns
        overlap_threshold: Minimum overlap duration in seconds
        
    Returns:
        List of (turn_i, turn_j, overlap_duration) tuples
    """
    overlaps = []
    for i in range(len(df)-1):
        cur_end = df.loc[i, 'end']
        next_start = df.loc[i+1, 'start']
        if next_start < cur_end:
            overlap_duration = cur_end - next_start
            if overlap_duration >= overlap_threshold:
                overlaps.append((i, i+1, overlap_duration))
    return overlaps


def summarize_monologues(df: pd.DataFrame, monologues: List[Tuple[int, int, float]], api_key: Optional[str] = None) -> List[Dict]:
    """
    Summarize each monologue using GPT-4.
    Returns list of summaries with metadata.
    
    Args:
        df: DataFrame with 'text' column containing utterances
        monologues: List of (start_idx, end_idx, duration) tuples
        api_key: OpenAI API key (uses env var if not provided)
        
    Returns:
        List of dicts with keys: start_turn, end_turn, duration, summary
    """
    summaries = []
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
    
    client = OpenAI(api_key=api_key)
    
    for (start, end, duration) in monologues:
        text = " ".join(df.loc[start:end, 'text'].tolist())
        prompt = f"Summarize the following monologue in a few sentences, keeping only key information relevant to the collaborative task:\n\n{text}"
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            summaries.append({
                "start_turn": start,
                "end_turn": end,
                "duration": duration,
                "summary": response.choices[0].message.content
            })
        except Exception as e:
            print(f"Error summarizing monologue {start}-{end}: {e}")
    
    return summaries


# ================================================================================
# 2. COLLABORATION DIMENSION RULES
# ================================================================================

DIMENSION_RULES = """
1. **Sustaining mutual understanding**: Look for explicit requests for feedback ("Did you understand?"), paraphrases, backchannels ("uh-huh"), clarifications. Technical terms explained or avoided.
2. **Dialogue management**: Smooth turn-taking; use of questions or explicit handovers; little overlap; speakers signal turn end (avoid fillers). Look for names or explicit attention-getting.
3. **Information pooling**: Introduction of new information with elaboration; linking to previous facts; eliciting domain knowledge; using partner's expertise.
4. **Reaching consensus**: Critical discussion of alternatives; exchange of arguments; final decision clearly identifiable; not revisiting unless new information.
5. **Task division**: Division into subtasks; systematic progression; individual vs. joint phases; clear role assignment; equal workload.
6. **Time management**: Mentions of time, schedule, remaining time; monitoring deadlines; reminders; setting time limits.
7. **Technical coordination**: References to using tools, copy/paste, shared editor; who writes; parallel work.
8. **Reciprocal interaction**: Respectful, constructive remarks; no personal attacks; equal participation; decisions made cooperatively.
9. **Individual task orientation**: Active engagement, focus on task, expressing interest, mobilizing skills.
"""


# ================================================================================
# 3. LLM-BASED EPISODE SEGMENTATION
# ================================================================================

def format_turns_for_prompt(df_chunk: pd.DataFrame, monologue_summaries: List[Dict], overlaps: List[Tuple[int, int, float]]) -> str:
    """
    Create a string representation of the chunk for LLM analysis.
    
    Args:
        df_chunk: Chunk of dialogue DataFrame
        monologue_summaries: Detected monologue summaries
        overlaps: Detected overlaps
        
    Returns:
        Formatted string for inclusion in LLM prompt
    """
    lines = []
    
    # First, list monologue summaries
    if monologue_summaries:
        lines.append("Monologue summaries:")
        for ms in monologue_summaries:
            lines.append(f"- Turns {ms['start_turn']+1}-{ms['end_turn']+1} ({ms['duration']:.1f}s): {ms['summary']}")
    
    # List overlaps
    if overlaps:
        lines.append("Overlaps detected at turn boundaries:")
        for (i, j, dur) in overlaps:
            lines.append(f"- Between turns {i+1} and {j+1} ({dur:.1f}s overlap)")
    
    # List dialogue turns
    lines.append("\nDialogue turns (with speaker and text):")
    for i, row in df_chunk.iterrows():
        lines.append(f"T{i+1}: {row['speaker']}: {row['text']}")
    
    return "\n".join(lines)


def call_llm_for_chunk(
    chunk_df: pd.DataFrame,
    monologue_summaries: List[Dict],
    overlaps: List[Tuple[int, int, float]],
    stack: List[str],
    bookmark: Optional[int],
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process one chunk with GPT-4 using discourse stack model.
    
    Args:
        chunk_df: Dialogue chunk DataFrame
        monologue_summaries: Detected monologue summaries
        overlaps: Detected overlaps
        stack: Current discourse stack
        bookmark: Previous bookmark (if continuing unfinished episode)
        api_key: OpenAI API key
        
    Returns:
        Dict with keys: episodes, final_stack, unfinished, bookmark
    """
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
    
    formatted = format_turns_for_prompt(chunk_df, monologue_summaries, overlaps)
    stack_str = "\n".join([f"- {dsp}" for dsp in stack]) if stack else "(empty)"
    bookmark_info = f"Previous chunk ended with an unfinished episode at local turn {bookmark+1}." if bookmark is not None else "No unfinished episode from previous chunk."

    prompt = f"""
You are a discourse analyst applying the Grosz & Sidner (1986) intentional stack model, and also analyzing collaboration quality using the dimensions below.

**Current discourse stack** (most recent on top):
{stack_str}

**Bookmark info**: {bookmark_info}

**Collaboration dimensions** (use these to label episodes):
{DIMENSION_RULES}

Now examine the following chunk of dialogue. This chunk may contain one or more complete episodes. An episode is a contiguous sequence of turns that serves a single Discourse Segment Purpose (DSP) – a sub‑goal or collaborative intention. Episodes can be nested: when a new DSP begins, push it onto the stack; when it ends, pop it.

The chunk may also contain monologue summaries and overlap information to help you.

**Dialogue chunk**:
{formatted}

Your task:
1. Identify the episodes within this chunk.
2. For each episode, output:
   - The start and end local turn numbers (e.g., 1–3).
   - The DSP (a short action label, e.g., "clarify deadline", "brainstorm ideas").
   - The stack operation: "push", "pop", "push+pop", or "continue".
   - The main collaboration dimension(s) from the list above that characterize this episode (choose 1–3 most relevant).
3. Maintain the stack across episodes.
4. If the chunk ends with an unfinished episode (i.e., the DSP continues beyond the chunk), set `unfinished: true` and provide a `bookmark` equal to the local turn number where the episode began (so the next chunk can start from there). If the episode is complete, set `unfinished: false` and `bookmark: null`.

Return JSON only, with the following structure:
{{
  "episodes": [
    {{
      "local_start": 1,
      "local_end": 3,
      "dsp": "...",
      "stack_operation": "...",
      "dimensions": ["...", "..."]
    }},
    ...
  ],
  "final_stack": ["dsp1", "dsp2", ...],
  "unfinished": false,
  "bookmark": null
}}

Do not include any other text.
"""
    
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a precise discourse analysis assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)


# ================================================================================
# 4. MAIN PIPELINE WITH BOOKMARKING
# ================================================================================

def segment_dialogue(df: pd.DataFrame, chunk_duration_sec: float = 600.0, api_key: Optional[str] = None) -> List[Dict]:
    """
    Main function to segment dialogue using discourse stack model.
    Works with already-loaded DataFrame (compatible with app.py).
    
    Args:
        df: DataFrame with columns: speaker, start, end, text
        chunk_duration_sec: Duration of chunks for processing
        api_key: OpenAI API key (uses env var if not provided)
        
    Returns:
        List of episode dicts with keys:
        - start_turn, end_turn: Global turn indices
        - dsp: Discourse Segment Purpose
        - stack_operation: Stack operation type
        - dimensions: Collaboration dimensions
        - duration_seconds: Episode duration
        - duration_minutes: Episode duration in minutes
        - utterance_count: Number of turns
        - speakers: Comma-separated speaker names
        - num_speakers: Number of unique speakers
    """
    if df is None or len(df) == 0:
        return []
    
    if not api_key:
        api_key = os.environ.get("OPENAI_API_KEY")
    
    all_episodes = []
    stack = []
    bookmark = None
    current_turn = 0
    
    while current_turn < len(df):
        # Determine chunk end
        chunk_start = current_turn
        accumulated_time = 0.0
        chunk_end = chunk_start
        
        for i in range(current_turn, len(df)):
            dur = df.loc[i, 'end'] - df.loc[i, 'start']
            if accumulated_time + dur > chunk_duration_sec and i > chunk_start:
                chunk_end = i - 1
                break
            accumulated_time += dur
            chunk_end = i
        else:
            chunk_end = len(df) - 1
        
        # Extract chunk
        chunk_df = df.iloc[chunk_start:chunk_end+1].copy()
        chunk_df.reset_index(drop=True, inplace=True)
        
        # Detect monologues and overlaps
        monologues = detect_monologues_without_content(chunk_df)
        overlaps = detect_overlaps_without_content(chunk_df)
        monologue_summaries = summarize_monologues(chunk_df, monologues, api_key) if monologues else []
        
        # Call LLM for this chunk
        result = call_llm_for_chunk(
            chunk_df,
            monologue_summaries,
            overlaps,
            stack,
            bookmark,
            api_key
        )
        
        # Convert local turn indices to global and format for UI
        for ep in result.get("episodes", []):
            global_start = chunk_start + ep["local_start"] - 1
            global_end = chunk_start + ep["local_end"] - 1
            
            # Get episode metadata
            episode_utterances = df.iloc[global_start:global_end+1]
            duration_sec = episode_utterances.iloc[-1]['end'] - episode_utterances.iloc[0]['start']
            speakers = list(set(episode_utterances['speaker'].tolist()))
            
            all_episodes.append({
                'start_turn': global_start,
                'end_turn': global_end,
                'start_idx': global_start,
                'end_idx': global_end + 1,
                'dsp': ep.get("dsp", "Unknown"),
                'stack_operation': ep.get("stack_operation", "continue"),
                'dimensions': ep.get("dimensions", []),
                'duration_seconds': duration_sec,
                'duration_minutes': duration_sec / 60,
                'utterance_count': global_end - global_start + 1,
                'speakers': ", ".join(sorted(speakers)),
                'num_speakers': len(speakers),
                'episode_id': len(all_episodes)
            })
        
        # Update stack
        stack = result.get("final_stack", stack)
        
        # Handle bookmark
        if result.get("unfinished", False):
            local_bookmark = result.get("bookmark")
            if local_bookmark is not None:
                bookmark = chunk_start + local_bookmark - 1
                current_turn = bookmark
            else:
                current_turn = chunk_end + 1
        else:
            bookmark = None
            current_turn = chunk_end + 1
    
    return all_episodes
