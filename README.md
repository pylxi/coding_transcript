# Coder_script - Project Root

Quick reference for the main project location.

## 📁 Where to Work

**Primary Project Directory:**
```
dialogue-episode-annotator/
```

This is where all the active development happens.

---

## 🚀 Quick Start

### 1. Go to Main Project
```bash
cd dialogue-episode-annotator
```

### 2. View Documentation
```bash
cat docs/INDEX.md          # Quick navigation
cat STRUCTURE.md           # Project structure
cat REORGANIZATION_SUMMARY.md  # What was reorganized
```

### 3. Read Guides
```bash
cat docs/NLP_QUICK_START.md        # Getting started
cat docs/NLP_LIBRARY_GUIDE.md      # Development
```

### 4. Run the App
```bash
python main.py
```

### 5. Verify Setup
```bash
python verify_nlp_setup.py
```

---

## 📂 Directory Layout

```
Coder_script/ (ROOT)
│
├── 📂 dialogue-episode-annotator/    ⭐ MAIN PROJECT
│   ├── docs/                         📚 All documentation
│   ├── nlp_lib/                      🧠 NLP library code
│   ├── static/                       🎨 Web assets
│   ├── templates/                    🌐 Web templates
│   ├── main.py                       🐍 Flask app
│   ├── STRUCTURE.md                  📖 Project structure
│   └── ... (code & config files)
│
├── 📂 static/                        (Legacy - consider removing)
├── 📂 templates/                     (Legacy - consider removing)
└── .git/                             Git repository
```

---

## 📚 Documentation

All documentation is in `dialogue-episode-annotator/docs/`:

- **INDEX.md** - Navigation guide
- **README_NLP.md** - Master index
- **NLP_QUICK_START.md** - Getting started
- **NLP_LIBRARY_GUIDE.md** - Development reference
- **NLP_SETUP_COMPLETE.md** - Setup info
- **NLP_FILES_SUMMARY.md** - File details

---

## 🐍 Main Files

Located in `dialogue-episode-annotator/`:

- `main.py` - Flask application
- `csv_validator.py` - CSV validation
- `csv_analyzer.py` - CSV analysis
- `verify_nlp_setup.py` - Setup verification
- `requirements.txt` - Python dependencies

---

## 🧠 NLP Library

Located in `dialogue-episode-annotator/nlp_lib/`:

- `__init__.py` - Package initialization
- `config.py` - Configuration
- `error_handler.py` - Error handling & logging
- 6 skeleton modules for implementation

---

## ✨ Key Points

✅ **All files are in dialogue-episode-annotator/**
- This is the single source of truth
- No duplicates at root level

✅ **Documentation is organized**
- All .md files in docs/ folder
- Easy to find and navigate

✅ **Clean structure**
- Ready for development
- Well documented

---

## 🔗 Quick Links

### Documentation
```bash
cd dialogue-episode-annotator
# Read quick start
cat docs/NLP_QUICK_START.md

# View all docs
ls -lh docs/

# See project structure
cat STRUCTURE.md
```

### Code
```bash
cd dialogue-episode-annotator
# Run app
python main.py

# Verify setup
python verify_nlp_setup.py

# Access NLP library
python -c "from nlp_lib import get_logger; print('OK')"
```

---

## ❓ FAQs

**Q: Where do I make changes?**
A: Work in `dialogue-episode-annotator/` directory

**Q: Where are the docs?**
A: `dialogue-episode-annotator/docs/`

**Q: How do I start?**
A: Read `dialogue-episode-annotator/docs/INDEX.md`

**Q: Can I delete the root-level static/ and templates/?**
A: Yes, they're duplicates. The real ones are in dialogue-episode-annotator/

**Q: Where's main.py?**
A: In `dialogue-episode-annotator/main.py`

---

## 🎯 Next Steps

1. Change to main directory:
   ```bash
   cd dialogue-episode-annotator
   ```

2. Read the documentation index:
   ```bash
   cat docs/INDEX.md
   ```

3. Follow the setup instructions

---

**Status:** ✅ Organized and Ready
**Last Updated:** April 2, 2026
