# 📋 Quick Reference Guide

## 🎯 Where Everything Is

```
📂 Coder_script/
│
├─ 🚀 app.py (ENTRY POINT - Start here!)
│  └─ 150+ lines of comments explaining architecture
│
├─ 📄 requirements.txt
│  └─ All dependencies
│
├─ 📂 src/ (PYTHON CODE)
│  ├─ __init__.py
│  ├─ csv_loader.py ........................ CSV validation & parsing
│  ├─ episode_extractor.py ................ Similarity segmentation
│  ├─ discourse_segmenter.py ............. Discourse stack analysis
│  └─ test_integration.py ................. Integration tests
│
├─ 📂 docs/ (DOCUMENTATION)
│  ├─ QUICKSTART.md ....................... 1-minute setup
│  ├─ README.md ........................... Feature overview
│  ├─ DISCOURSE_SEGMENTATION.md ........... Methods explained
│  ├─ IMPLEMENTATION.md ................... Technical details
│  ├─ VERIFICATION.md ..................... Quality checklist
│  ├─ DISCOURSE_COMPLETE.md .............. Complete summary
│  ├─ DELIVERY.md ......................... What was delivered
│  ├─ EPISODE_DEFINITIONS.md ............. Episode rules
│  └─ INDEX.md ............................ Documentation index
│
├─ 📄 README_STRUCTURE.md ................. Code structure explained
└─ 📄 WORKSPACE_TIDY.md .................. What was organized
```

## 🧭 Navigation by Task

### "I want to run the app"
```
1. cd /Users/laramonteagudotubau/Documents/Coder_script
2. pip install -r requirements.txt
3. python app.py
4. Open: http://localhost:7860
```

### "I want to understand the code"
```
1. Read: README_STRUCTURE.md
2. Read: app.py (it has detailed comments!)
3. Read specific modules in src/
4. Experiment with parameters
```

### "I want to learn the features"
```
1. Read: docs/QUICKSTART.md (5 min)
2. Read: docs/README.md (10 min)
3. Read: docs/DISCOURSE_SEGMENTATION.md (15 min)
4. Try both methods in the UI
```

### "I want all documentation"
```
→ See: docs/INDEX.md (navigation guide)
```

### "I want to add a feature"
```
1. Create file in src/
2. Import in app.py
3. Update Gradio UI if needed
4. Add docs in docs/
5. Run tests: python src/test_integration.py
```

## 📖 Reading by Level

### **Beginner (New to project)**
- [ ] README_STRUCTURE.md
- [ ] docs/QUICKSTART.md
- [ ] app.py (read comments)
- Time: 30 minutes

### **Intermediate (Want to use it)**
- [ ] docs/README.md
- [ ] docs/DISCOURSE_SEGMENTATION.md
- [ ] Modify parameters
- [ ] Run app with different settings
- Time: 1 hour

### **Advanced (Want to modify code)**
- [ ] docs/IMPLEMENTATION.md
- [ ] src/csv_loader.py
- [ ] src/episode_extractor.py
- [ ] src/discourse_segmenter.py
- [ ] src/test_integration.py
- Time: 3 hours

### **Expert (Want to understand everything)**
- [ ] All documentation
- [ ] All source code
- [ ] All comments
- [ ] Run tests
- Time: Full day

## 🔑 Key Files & What They Do

| File | Size | Purpose |
|------|------|---------|
| app.py | 500 lines | Gradio UI + session management |
| csv_loader.py | 120 lines | CSV validation & parsing |
| episode_extractor.py | 290 lines | Similarity-based segmentation |
| discourse_segmenter.py | 350 lines | LLM-based discourse analysis |
| test_integration.py | 200 lines | Integration tests |

## 🎓 Code Structure Cheat Sheet

```
ARCHITECTURE:

DATA LAYER
  └─ csv_loader.load_csv_file()
     Validates CSV → Returns DataFrame

EXTRACTION LAYER (Choose one)
  ├─ episode_extractor.extract_next_episode()
  │  Fast, local, free
  └─ discourse_segmenter.segment_dialogue()
     Detailed, GPT-4, costs $

PRESENTATION LAYER
  └─ Gradio UI (app.py)
     Shows results to user
```

## 💻 Common Commands

```bash
# Run the app
python app.py

# Run tests
python src/test_integration.py

# View source code
cat src/csv_loader.py
cat src/episode_extractor.py
cat src/discourse_segmenter.py

# View documentation
cat docs/QUICKSTART.md
cat docs/DISCOURSE_SEGMENTATION.md

# Check imports
python -c "from src.csv_loader import load_csv_file; print('OK')"

# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY="sk-..."
```

## 📊 Data Flow Summary

```
User uploads CSV
    ↓
csv_loader validates & parses
    ↓
DataFrame created
    ↓
┌─────────────────────────────┐
│  Choose method:              │
│  ├─ Similarity (local, fast) │
│  └─ Discourse (GPT-4, $)     │
└─────────────────────────────┘
    ↓
Extract episodes
    ↓
display_episode() formats
    ↓
Gradio UI shows results
```

## 🧪 Testing

```bash
# Run all tests
python src/test_integration.py

# Expected output:
✅ PASS: Imports
✅ PASS: CSV Loader
✅ PASS: Similarity Extractor
✅ PASS: Discourse Support

# If any fail:
# 1. Check error message
# 2. Review docs/DISCOURSE_SEGMENTATION.md → Troubleshooting
# 3. Check environment variables (OPENAI_API_KEY)
# 4. Check dependencies installed
```

## 🎯 Function Map

```
app.py (Main functions to understand):

1. AnnotationSession.__init__()
   → Initialize empty session

2. AnnotationSession.load_csv()
   → Load file, choose method, initialize extractor

3. AnnotationSession.get_next_episode()
   → Get next episode (from list or on-demand)

4. AnnotationSession.move_to_next()
   → Advance to next episode

5. load_file_handler()
   → Respond to file upload button click

6. display_episode()
   → Format episode for UI display

7. next_episode_handler()
   → Respond to "Next Episode" button click

8. Gradio UI Definition
   → Create web interface
```

## 🔧 Configuration

### Similarity-Based Parameters
File: `src/episode_extractor.py`
```python
similarity_threshold = 0.5
min_episode_utterances = 5
max_episode_utterances = 30
min_episode_seconds = 60
max_episode_seconds = 300
monologue_threshold_seconds = 90
min_speakers = 2
```

### Discourse Parameters
File: `src/discourse_segmenter.py`
```python
chunk_duration_sec = 600.0  # 10 minutes
min_duration = 30.0  # Monologue minimum
```

### Environment Variables
```bash
OPENAI_API_KEY="sk-..."  # Required for discourse method
HF_TOKEN="hf_..."  # Optional, for HuggingFace Spaces
```

## 📞 Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| Import error | Reinstall deps: `pip install -r requirements.txt` |
| API key error | Set: `export OPENAI_API_KEY="sk-..."` |
| CSV error | Check columns: speaker, timestamp, utterance |
| Port 7860 in use | Kill: `lsof -i :7860` or use `server_port=7861` |
| Gradio error | Check Gradio version: `pip install gradio>=4.0.0` |

See `docs/DISCOURSE_SEGMENTATION.md` for detailed troubleshooting.

## 🌟 Highlights

✨ **Clean Architecture**
- Data layer → Extraction layer → Presentation layer
- Clear separation of concerns
- Easy to understand

✨ **Two Methods Available**
- Similarity-based (fast, free, local)
- Discourse stack (detailed, powered by GPT-4)

✨ **Well Documented**
- 150+ lines of comments in app.py
- 10,000+ words in docs/
- Every function explained
- ASCII diagrams

✨ **Organized Files**
- Code in src/
- Docs in docs/
- Entry point in root

✨ **Beginner Friendly**
- Can understand entire codebase in 1 hour
- Step-by-step learning path
- Clear examples

---

**Quick Start**: `python app.py` → Open browser → Load CSV

**Questions?** Check `docs/INDEX.md` for all documentation.

**Want to contribute?** Read `README_STRUCTURE.md` then modify `src/` files.

**All set!** 🚀
