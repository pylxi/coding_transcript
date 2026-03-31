---
title: Dialogue Episode Annotator
emoji: 🎙️
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
---

# Dialogue Episode Annotator

A Gradio web app for segmenting dialogue transcripts into episodes with two advanced methods:
1. **Similarity-based** (fast, local, no API required)
2. **Discourse stack analysis** (GPT-4 powered, detailed discourse structure)

## Features

- 📁 Load CSV files with dialogue data (flexible column names)
- 🔄 **Two segmentation methods**:
  - Similarity-based: Fast topic shift detection with embeddings
  - Discourse stack: LLM-based Grosz & Sidner analysis with 9 collaboration dimensions
- 📊 Episode metadata: duration, participants, topics, DSP labels
- 🎙️ Monologue detection and summarization
- 📋 Collaboration dimension classification
- 🔄 On-demand episode extraction (reads file progressively)

## Quick Start

### Installation

```bash
# Clone or setup workspace
cd your-workspace

# Install dependencies
pip install -r requirements.txt

# For discourse stack method (optional):
pip install openai>=1.0.0
export OPENAI_API_KEY="your-key-here"
```

### Run

```bash
python app.py
```

Open `http://localhost:7860` in your browser.

### Input Format

CSV file with columns:
- `speaker`: Speaker name (required)
- `start`: Start time in seconds or MM:SS (required for discourse method)
- `end`: End time in seconds or MM:SS (required for discourse method)
- `utterance` OR `text`: Dialogue text (required)

Example:
```csv
speaker,start,end,utterance
Alice,0.5,2.3,Hi Bob, how are you?
Bob,2.5,4.1,I'm good! How about you?
```

## Methods Comparison

| Feature | Similarity-Based | Discourse Stack |
|---------|-----------------|-----------------|
| Speed | ~1s for 100 utterances | ~5-10s (API dependent) |
| API Required | No | Yes (GPT-4) |
| Cost | Free | $0.01-0.05 per transcript |
| Episode Detection | Embedding similarity + heuristics | Discourse structure analysis |
| Output Detail | Duration, speakers, topics | DSP labels, stack operations, collaboration dimensions |

## Configuration

See [DISCOURSE_SEGMENTATION.md](DISCOURSE_SEGMENTATION.md) for detailed parameter documentation and advanced usage.

### Similarity-Based Parameters
- `similarity_threshold`: 0.5
- `min_episode_utterances`: 5
- `max_episode_utterances`: 30
- Duration: 60-300 seconds

### Discourse Stack Parameters
- `chunk_duration_sec`: 600 (10 minutes)
- Collaboration dimensions: 9 detailed categories
   - Lower = more episodes
   - Higher = fewer episodes
3. **Segment**: Click "Segment" to split dialogue into episodes
4. **Annotate**: 
   - Select an episode from the dropdown
   - Choose a metacognition type
   - Add notes if needed
   - Click "Save"
5. **Export**: Click "Export" to download annotated data as Excel

## Excel Format

Input Excel file should have these columns:

| speaker | utterance | (optional line_number) |
|---------|-----------|------------------------|
| Alice   | Hello... | 1 |
| Bob     | Hi... | 2 |

## Metacognition Types

- **Planning** - Setting goals and strategies
- **Monitoring** - Checking progress and understanding
- **Evaluation** - Assessing outcomes and quality
- **Regulation** - Adjusting approach or strategy
- **None** - No metacognitive content

## Files

- `app.py` - Main Gradio application
- `segmentation.py` - Episode segmentation logic using BERT
- `utils.py` - Data reading/writing utilities
- `requirements.txt` - Python dependencies

## Deploy to Hugging Face Spaces

### Method 1: Git Push (Recommended)

1. Create a new Space on Hugging Face: https://huggingface.co/new-space
   - Name: `dialogue-episode-annotator`
   - License: Choose any
   - Space SDK: `Gradio`

2. Clone the space repo:
   ```bash
   git clone https://huggingface.co/spaces/YOUR_USERNAME/dialogue-episode-annotator
   cd dialogue-episode-annotator
   ```

3. Copy your files:
   ```bash
   cp ../app.py .
   cp ../segmentation.py .
   cp ../utils.py .
   cp ../requirements.txt .
   ```

4. Commit and push:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push
   ```

Hugging Face will automatically build and deploy your app! 🚀

### Method 2: Upload via UI

1. Go to https://huggingface.co/spaces
2. Click "Create new Space"
3. Choose "Gradio" as SDK
4. Upload all files directly in the UI
5. HF automatically deploys

## Requirements for HF Spaces

- **Python 3.8+** ✓
- All dependencies in `requirements.txt` ✓
- `app.py` as main file ✓
- Uses Gradio interface ✓

## Environment Variables (Optional)

For HF Spaces, you might want to add:
- GPU enabled (if needed for BERT models)
- Custom timeouts

Go to Space Settings → Advanced Settings to configure.

## Troubleshooting

**Issue**: Module not found errors
- Solution: Make sure all files are in the space directory

**Issue**: BERT model loading is slow
- Solution: Increase space timeout or use a smaller model

**Issue**: Large file uploads fail
- Solution: HF Spaces has upload limits; consider compression

## License

MIT License

---

Built with ❤️ using Gradio and Hugging Face
