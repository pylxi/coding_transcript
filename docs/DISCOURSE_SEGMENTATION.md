# Discourse Segmentation Integration

## Overview

The episode annotator now supports two segmentation methods:

### 1. **Similarity-Based Segmentation** (Default)
- **Model**: Sentence-Transformers (all-MiniLM-L6-v2)
- **Approach**: Detects topic shifts using embeddings and cosine similarity
- **Requires**: No API key
- **Speed**: Fast (local processing)
- **Output**: Episodes with duration, utterance count, participants, and topic extraction

### 2. **Discourse Stack Segmentation** (NEW)
- **Model**: GPT-4 with Grosz & Sidner (1986) intentional stack model
- **Approach**: Analyzes dialogue structure, collaboration dimensions, and discourse segment purposes (DSPs)
- **Requires**: OpenAI API key (`OPENAI_API_KEY` environment variable)
- **Speed**: Slower (API calls required)
- **Output**: Episodes with DSP labels, stack operations, and 9 collaboration dimensions

## Installation

### For Similarity-Based Only:
```bash
pip install -r requirements.txt
```

### For Discourse Stack Support:
```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

1. **Start the app**:
   ```bash
   python app.py
   ```

2. **Select segmentation method**:
   - Choose "Similarity-Based" or "Discourse Stack (GPT-4)"
   - Upload your CSV file

3. **Expected CSV format**:
   - `speaker`: Speaker name
   - `start`: Start time (seconds or MM:SS)
   - `end`: End time (seconds or MM:SS)
   - `utterance`: Dialogue text

   Alternative column names supported: `timestamp`, `text`, `turn`

## Collaboration Dimensions (Discourse Stack Method)

The discourse segmenter analyzes episodes using these 9 dimensions:

1. **Sustaining mutual understanding**: Feedback requests, paraphrases, clarifications
2. **Dialogue management**: Turn-taking, questions, overlap avoidance
3. **Information pooling**: New information, elaboration, expertise use
4. **Reaching consensus**: Alternative discussion, arguments, decision clarity
5. **Task division**: Subtasks, progression, role assignment
6. **Time management**: Time mentions, deadline monitoring
7. **Technical coordination**: Tool use, shared editing, parallel work
8. **Reciprocal interaction**: Respect, equal participation, cooperative decisions
9. **Individual task orientation**: Engagement, focus, skill mobilization

## Configuration

### Similarity-Based Parameters (in `episode_extractor.py`):
- `similarity_threshold`: 0.5 (topic shift detection)
- `min_episode_utterances`: 5
- `max_episode_utterances`: 30
- `min_episode_seconds`: 60
- `max_episode_seconds`: 300
- `monologue_threshold_seconds`: 90
- `min_speakers`: 2

### Discourse Stack Parameters (in `discourse_segmenter.py`):
- `chunk_duration_sec`: 600.0 (10 minutes per chunk for LLM processing)
- `monologue_min_duration`: 30.0 seconds

## API Costs

**Discourse Stack method uses GPT-4 API calls:**
- Each 10-minute chunk = 1 API call
- Monologue summaries = 1 API call per monologue (optional)
- Typical cost: $0.01-0.05 per transcript depending on length

Monitor your OpenAI usage to control costs.

## Troubleshooting

### "Discourse segmenter not available"
- Install openai: `pip install openai>=1.0.0`
- Check `OPENAI_API_KEY` is set

### "OPENAI_API_KEY not set"
- Export your key: `export OPENAI_API_KEY="sk-..."`

### Timeout or API errors
- Check OpenAI account quota
- Verify API key is valid
- Check network connection

## Architecture

```
app.py (Gradio UI)
├── csv_loader.py (CSV handling, encoding fallbacks)
├── episode_extractor.py (Similarity-based segmentation)
└── discourse_segmenter.py (LLM-based discourse stack analysis)
    ├── split_by_time() - Chunk dialogue
    ├── detect_monologues_without_content() - Find long monologues
    ├── detect_overlaps_without_content() - Find timing overlaps
    ├── summarize_monologues() - Summarize monologues with GPT-4
    ├── call_llm_for_chunk() - Segment chunk with discourse analysis
    └── segment_dialogue() - Main pipeline
```

## Switching Methods

Simply select the radio button in the UI before loading a file. Both methods can be used with the same CSV file.

## Performance Notes

- **Similarity**: 100-1000 utterances in ~1 second
- **Discourse**: 100-300 utterances in ~5-10 seconds (API latency dependent)

For large files (>1000 utterances), discourse segmentation processes in 10-minute chunks automatically.
