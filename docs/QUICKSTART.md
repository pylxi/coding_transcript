# Quick Start Guide - Discourse Segmentation

## 1-Minute Setup

### Option A: Similarity-Based (Default)
```bash
cd /Users/laramonteagudotubau/Documents/Coder_script
pip install -r requirements.txt
python app.py
```
✅ No API key needed
✅ Fast processing (1s for 100 utterances)

### Option B: Discourse Stack (GPT-4)
```bash
cd /Users/laramonteagudotubau/Documents/Coder_script
pip install -r requirements.txt
export OPENAI_API_KEY="sk-your-key-here"
python app.py
```
✅ Advanced discourse analysis
✅ 9 collaboration dimensions
⚠️ Requires OpenAI API key (~$0.01 per transcript)

## Using the App

1. **Open browser**: http://localhost:7860
2. **Choose method**: Select radio button (Similarity or Discourse)
3. **Load CSV**: Click file input and select your CSV
4. **View episode**: See transcript and analysis
5. **Next episode**: Click button to view more

## CSV Format

Minimal example:
```csv
speaker,timestamp,utterance
Alice,00:01,Hello
Bob,00:05,Hi there
Alice,00:10,How are you
```

Required columns:
- `speaker`: Who is speaking
- `timestamp`: Time in MM:SS format (e.g., 00:30)
- `utterance`: What they said

## What You'll See

### Similarity Method
```
━━━━━━━━━━━━━━━━━━━━━━━━
EPISODE #0
━━━━━━━━━━━━━━━━━━━━━━━━

⏱️  Duration: 2.5 minutes
💬 Utterances: 8
👥 Participants: 2 (Alice, Bob)

[Transcript displayed below]
```

Analysis shows:
- Duration and utterance count
- Participants involved
- Topics extracted
- Monologues summarized
- Why episode ended

### Discourse Method
```
━━━━━━━━━━━━━━━━━━━━━━━━
EPISODE #0
━━━━━━━━━━━━━━━━━━━━━━━━

📌 DSP: clarify_timeline
📚 Stack Op: push
📊 Dimensions: Info pooling, Time mgt
🔄 Turns: 0-8
```

Analysis shows:
- Discourse Segment Purpose (DSP) label
- Stack operation (push/pop)
- 1-3 collaboration dimensions
- Turn range analyzed

## Two Analysis Tabs

Both methods provide:

**📊 Analysis Tab**:
- AI-generated explanation
- Key findings
- Why episode ended

**⚙️ Settings Tab**:
- Model used
- Algorithm details
- Parameter values
- Extraction rationale

## Testing

Verify everything works:
```bash
python test_integration.py
```

Should show:
```
✅ PASS: Imports
✅ PASS: CSV Loader
✅ PASS: Similarity Extractor
✅ PASS: Discourse Support

🎉 All integration tests passed!
```

## Troubleshooting

### "Import error: pandas not found"
```bash
pip install pandas>=2.0.0
```

### "Discourse segmenter not available"
```bash
pip install openai>=1.0.0
```

### "OPENAI_API_KEY not set"
```bash
export OPENAI_API_KEY="sk-..."
python app.py
```

### "API Error: Invalid API key"
- Check your key is correct at openai.com
- Make sure it's not expired
- Verify it has credits remaining

## Performance Guide

| Size | Similarity | Discourse |
|------|-----------|-----------|
| 100 utterances | 1s | 5-10s |
| 300 utterances | 2s | 15-30s |
| 1000 utterances | 3-5s | 60s+ |

Discourse processes in 10-minute chunks automatically.

## Cost Estimate

**Similarity**: Free

**Discourse** (per transcript):
- 100 utterances (~10 min): $0.01
- 500 utterances (~50 min): $0.05
- 1000 utterances (~100 min): $0.10

Monitor your usage: openai.com/account/billing

## Next Steps

1. ✅ App is running
2. ✅ Load a CSV file
3. ✅ Try both methods
4. ✅ See which you prefer
5. 📖 Read DISCOURSE_SEGMENTATION.md for details

## Documentation Files

- **README.md**: Overview and features
- **DISCOURSE_SEGMENTATION.md**: Detailed feature docs
- **IMPLEMENTATION.md**: Technical implementation
- **EPISODE_DEFINITIONS.md**: Episode rules
- **DISCOURSE_COMPLETE.md**: Complete summary

## Switching Methods

You can test both methods with the same CSV file:
1. Load with Similarity-Based
2. Review episodes
3. Reload with Discourse Stack
4. Compare results

Each method may segment differently - both are valid!

## Help & Support

- Check test_integration.py output for diagnostics
- See DISCOURSE_SEGMENTATION.md troubleshooting
- Review IMPLEMENTATION.md for technical details

---

**Ready to go!** 🚀

Start with `python app.py` and choose your method.
