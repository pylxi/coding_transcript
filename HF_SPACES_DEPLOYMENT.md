# HF Spaces Deployment Guide

## Quick Deploy (5 minutes)

###  Step 1: Verify Files
```bash
ls -la | grep -E "(app_gradio|app\.py|requirements)"
```

Should show:
- ✅ `app_gradio.py` - Gradio interface
- ✅ `app.py` - HF entry point
- ✅ `requirements.txt` - Dependencies

### Step 2: Commit & Push
```bash
git add app_gradio.py app.py GRADIO_QUICKSTART.md README_HF_SPACES.md COMPLETION_SUMMARY.md QUICK_REFERENCE.txt
git commit -m "feat: Add Gradio web UI with HF Spaces integration"
git push origin master
```

### Step 3: Monitor Build
Check build logs: https://huggingface.co/spaces/pylxi/dialogue-episode-annotator?logs=build

Build typically takes 2-5 minutes. Wait for green ✅ checkmark.

### Step 4: Add API Key
Once build is green:
1. Go to Space Settings (⚙️)
2. Click "Variables and secrets"
3. Add Secret: `OPENAI_API_KEY` = your key
4. Restart Space

### Step 5: Test
Open: https://huggingface.co/spaces/pylxi/dialogue-episode-annotator
- Upload `sample_transcript.csv`
- Click "Process Transcript"
- See analytics instantly!

## Troubleshooting

**Build Failed?**
- Check logs at `?logs=build`
- Common: Missing imports or wrong requirements.txt location
- Solution: requirements.txt must be in root, not in app/

**App doesn't load?**
- Check app.py exists in root
- Verify `app_file: app.py` in README.md metadata
- Check Python version compatibility (3.9+)

**Import errors?**
- Verify all relative imports in app_gradio.py
- Check files are actually in HF Space repo (git push worked)
- Look at build logs for specific error

**API key not working?**
- Secret must be named exactly: `OPENAI_API_KEY`
- Verify it's set in Space Settings > Secrets
- Space needs restart after adding secret

## File Checklist

Root directory must contain:
```
✅ app.py                 (HF entry point)
✅ app_gradio.py          (Web interface)
✅ requirements.txt       (Dependencies)
✅ README.md              (With YAML metadata)
✅ sample_transcript.csv  (Test data)
```

Subdirectories:
```
✅ app/                   (Core modules)
   ├── config.py
   ├── utils.py
   ├── analytics.py
   ├── summarizer.py
   └── ...
```

## Need Help?

See:
- `GRADIO_QUICKSTART.md` - Local testing
- `README_HF_SPACES.md` - Using the interface
- `COMPLETION_SUMMARY.md` - Technical details
