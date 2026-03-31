# 🎙️ Dialogue Episode Annotator

Professional dialogue segmentation system with two analysis methods.

## 📁 Project Structure

```
Coder_script/
├── 📄 app.py                      ← START HERE: Main application (run this!)
├── 📄 requirements.txt            ← Dependencies
│
├── 📂 src/                        ← SOURCE CODE
│   ├── __init__.py
│   ├── app.py                     (moved here in organized setup)
│   ├── csv_loader.py              ← CSV file handling & validation
│   ├── episode_extractor.py       ← Similarity-based segmentation (default)
│   ├── discourse_segmenter.py     ← LLM-based discourse analysis (optional)
│   └── test_integration.py        ← Integration tests
│
└── 📂 docs/                       ← DOCUMENTATION
    ├── README.md                  ← Feature overview
    ├── QUICKSTART.md              ← 1-minute setup guide
    ├── DISCOURSE_SEGMENTATION.md  ← Feature documentation
    ├── IMPLEMENTATION.md          ← Technical details
    ├── VERIFICATION.md            ← Quality checklist
    ├── DISCOURSE_COMPLETE.md      ← Complete summary
    ├── DELIVERY.md                ← What was delivered
    ├── EPISODE_DEFINITIONS.md     ← Episode rules
    └── INDEX.md                   ← Documentation index
```

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Set API key for GPT-4 method
export OPENAI_API_KEY="sk-..."

# 3. Run the app
python app.py

# 4. Open browser to http://localhost:7860
```

## 📚 Code Structure Explained

### Layer 1: Data Input (`csv_loader.py`)
```
Your CSV File
    ↓
load_csv_file(path)
    ↓
Validates: speaker, timestamp, utterance columns
Handles: UTF-8, latin-1, iso-8859-1 encodings
Parses: MM:SS → seconds conversion
    ↓
Clean DataFrame with timestamp_seconds column
```

### Layer 2: Episode Extraction (Two Methods)

**Method A: Similarity-Based** (`episode_extractor.py`)
```
DataFrame → extract_next_episode(idx)
    ↓
Uses: sentence-transformers embeddings
Detects: Topic shifts (similarity < 0.5)
Identifies: Monologues (>90s single speaker)
Returns: Episode with duration, speakers, topics, reasons
```

**Method B: Discourse Stack** (`discourse_segmenter.py`)
```
DataFrame → segment_dialogue()
    ↓
Uses: GPT-4 for discourse analysis
Analyzes: 9 collaboration dimensions
Labels: Discourse Segment Purpose (DSP)
Tracks: Stack operations (push/pop/continue)
Returns: Episodes with detailed discourse metadata
```

### Layer 3: Presentation (`app.py`)
```
Session State (AnnotationSession class)
    ├─ df: Loaded DataFrame
    ├─ extractor: Similarity extractor
    ├─ discourse_episodes: Pre-segmented list
    └─ current_idx: Position in file
        ↓
    Event Handlers (respond to user clicks)
        ├─ load_file_handler()
        ├─ display_episode()
        └─ next_episode_handler()
        ↓
    Gradio UI (web interface)
        ├─ File upload + method selection
        ├─ Transcript display
        └─ Analysis modal (2 tabs)
```

## 🔀 Data Flow Example

```
User uploads "dialogue.csv" and selects "Similarity-Based"
    ↓
load_file_handler() called
    ↓
session.load_csv("dialogue.csv", "similarity")
    ↓
csv_loader.load_csv_file() validates & parses
    ↓
EpisodeExtractor initialized
    ↓
session.get_next_episode()
    ├─ extractor.extract_next_episode(0)
    ├─ Finds topic shifts
    ├─ Checks duration/utterance limits
    └─ Returns: Episode #0 (turns 0-12)
    ↓
display_episode(episode)
    ├─ Formats metadata
    ├─ Builds transcript
    └─ Creates analysis text
    ↓
Results displayed in UI tabs
    ├─ Left: Full transcript
    └─ Right: Analysis modal
       ├─ 📊 Analysis tab (AI findings)
       └─ ⚙️ Settings tab (parameters)

User clicks "Next Episode"
    ↓
next_episode_handler() called
    ↓
session.get_next_episode()
    ├─ extractor.extract_next_episode(13)
    └─ Returns: Episode #1 (turns 13-25)
    ↓
Display episode #1
```

## 🎯 Key Components

### AnnotationSession (app.py)
- **Purpose**: Manage user session state
- **Stores**: DataFrame, extractors, current position
- **Methods**:
  - `load_csv()`: Load file and initialize
  - `get_next_episode()`: Get current episode
  - `move_to_next()`: Advance to next

### EpisodeExtractor (src/episode_extractor.py)
- **Purpose**: Similarity-based episode segmentation
- **Key Methods**:
  - `extract_next_episode()`: Extract one episode on-demand
  - `_is_topic_shift()`: Detect topic boundaries
  - `_detect_monologue()`: Find long monologues
  - `_summarize_monologue()`: Create monologue summaries

### DiscourseSegmenter (src/discourse_segmenter.py)
- **Purpose**: LLM-based discourse analysis
- **Key Functions**:
  - `segment_dialogue()`: Main pipeline
  - `split_by_time()`: Chunk dialogue
  - `call_llm_for_chunk()`: GPT-4 analysis
  - `summarize_monologues()`: LLM monologue summaries

### CSV Loader (src/csv_loader.py)
- **Purpose**: Robust CSV file handling
- **Features**:
  - Multiple encoding fallbacks
  - Timestamp parsing (MM:SS, HH:MM:SS)
  - Column validation
  - Error handling

## 🧪 Testing

```bash
# Run integration tests
python -m pytest src/test_integration.py

# Or directly:
python src/test_integration.py

# Expected output:
# ✅ PASS: Imports
# ✅ PASS: CSV Loader
# ✅ PASS: Similarity Extractor
# ✅ PASS: Discourse Support
# 🎉 All integration tests passed!
```

## 📖 Documentation Map

| Document | Best For | Read Time |
|----------|----------|-----------|
| **QUICKSTART.md** | Getting started | 5 min |
| **README.md** | Feature overview | 10 min |
| **DISCOURSE_SEGMENTATION.md** | Learning methods | 15 min |
| **IMPLEMENTATION.md** | Technical details | 20 min |
| **VERIFICATION.md** | Quality assurance | 5 min |
| **This file** | Code structure | 10 min |

See `docs/INDEX.md` for complete documentation index.

## 🛠️ Common Tasks

### Add a new extraction method
1. Create `src/new_method.py` with segmentation logic
2. Add import to `app.py`
3. Add radio option in Gradio UI
4. Update `display_episode()` to handle new format

### Modify extraction parameters
- **Similarity**: Edit `EpisodeExtractor.__init__()` in `src/episode_extractor.py`
  - `similarity_threshold = 0.5`
  - `min_episode_utterances = 5`
  - `max_episode_utterances = 30`
  - etc.

- **Discourse**: Edit chunk parameters in `src/discourse_segmenter.py`
  - `chunk_duration_sec = 600.0`
  - `min_duration = 30.0`

### Deploy to HuggingFace Spaces
```bash
# Copy files to HF space
cp app.py src/*.py to-hf-space/
git add . && git commit -m "..." && git push
```

## 🔒 Environment Variables

```bash
# Required only for Discourse method
export OPENAI_API_KEY="sk-your-key-here"

# Optional
export HF_TOKEN="hf_..."  # For HuggingFace Spaces
```

## 📊 Performance

| Operation | Time | Cost |
|-----------|------|------|
| Load CSV (100 utterances) | <1s | Free |
| Similarity segmentation (100 utterances) | ~1s | Free |
| Discourse segmentation (100 utterances) | ~10s | ~$0.01 |
| Discourse segmentation (1000 utterances) | ~100s | ~$0.10 |

Discourse processes in 10-minute chunks automatically.

## 🐛 Troubleshooting

**"Import error: No module named 'src'"**
- Make sure `app.py` is in root directory (not inside src/)
- Python should find `src/` as a package

**"OPENAI_API_KEY not set"**
```bash
export OPENAI_API_KEY="sk-..."
```

**"Gradio server won't start"**
- Check port 7860 isn't in use: `lsof -i :7860`
- Try different port: Edit `demo.launch(server_name="0.0.0.0", server_port=7861)`

**"CSV validation fails"**
- Check columns: speaker, timestamp, utterance (case-insensitive)
- Verify encoding (UTF-8 preferred)
- Check for empty rows

## 📞 Getting Help

1. Check `docs/` folder for detailed documentation
2. Run `python src/test_integration.py` for diagnostics
3. Review error messages - they're descriptive!
4. See `docs/DISCOURSE_SEGMENTATION.md` → Troubleshooting

## 🎓 Learning Path

**Beginner:**
1. Read: QUICKSTART.md
2. Run: `python app.py`
3. Load CSV, try both methods

**Intermediate:**
1. Read: README.md + DISCOURSE_SEGMENTATION.md
2. Review: `src/csv_loader.py` (understand data flow)
3. Review: `src/episode_extractor.py` (understand similarity method)

**Advanced:**
1. Read: IMPLEMENTATION.md + code comments
2. Review: `src/discourse_segmenter.py` (understand discourse model)
3. Modify parameters and test

## 📝 License & Credits

Built with:
- **Gradio**: Web interface
- **Sentence-Transformers**: Embeddings
- **OpenAI**: GPT-4 for discourse analysis
- **Pandas**: Data handling
- **Scikit-learn**: Similarity metrics

---

**Status**: ✅ Production Ready

Start with `python app.py` and explore! 🚀
