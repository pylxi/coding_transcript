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

A Gradio web app for segmenting dialogue transcripts into episodes and annotating them with metacognitive categories.

## Features

- 📁 Upload Excel files with dialogue data
- 🔄 Automatic episode segmentation using similarity-based algorithms
- ✍️ Annotate episodes with metacognitive types
- 📊 Preview episode content before annotation
- 📥 Export annotated data to Excel

## How to Use

### Local Setup

1. Clone the repository or copy the files
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   python app.py
   ```

The app will open at `http://localhost:7860`

### Using the App

1. **Upload File**: Select an Excel file with columns: `speaker`, `utterance`
2. **Set Sensitivity**: Adjust the threshold slider (0.3-0.8)
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
