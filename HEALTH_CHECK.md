# 🔍 CODE HEALTH CHECK - Senior Programmer Review

**Date**: March 31, 2026  
**Status**: ⚠️ **ISSUES FOUND** - 7 Critical & Important Items

---

## Executive Summary

**Code Quality**: 6/10 - Functional but with significant issues
**Error Handling**: 5/10 - Many edge cases not covered
**Performance**: 4/10 - Several bottlenecks and inefficiencies
**Maintainability**: 7/10 - Good documentation but structural issues

---

## 🔴 CRITICAL ISSUES

### 1. **Missing Error Handling in segment_dialogue()**
**File**: `src/discourse_segmenter.py`, line 298  
**Severity**: CRITICAL

**Problem**: The `segment_dialogue()` function calls `call_llm_for_chunk()` without ANY error handling for API failures.

```python
# Current code (NO ERROR HANDLING):
result = call_llm_for_chunk(
    chunk_df,
    monologue_summaries,
    overlaps,
    stack,
    bookmark,
    api_key
)
```

**What happens if GPT-4 fails?**
- ❌ API times out → Entire app crashes
- ❌ Invalid JSON response → json.loads() fails
- ❌ Rate limited → No retry logic
- ❌ No API key → Cryptic error

**Fix Required**:
```python
# SHOULD BE:
try:
    result = call_llm_for_chunk(
        chunk_df,
        monologue_summaries,
        overlaps,
        stack,
        bookmark,
        api_key
    )
except json.JSONDecodeError as e:
    print(f"⚠️ Warning: Invalid LLM response for chunk {chunk_start}-{chunk_end}: {e}")
    # Skip this chunk or return empty episodes
    continue
except Exception as e:
    print(f"❌ Error calling LLM: {e}")
    raise
```

---

### 2. **No Validation of Episode Turn Ranges**
**File**: `src/discourse_segmenter.py`, line 362-363  
**Severity**: CRITICAL

**Problem**: After converting local to global indices, no bounds checking:

```python
global_start = chunk_start + ep["local_start"] - 1
global_end = chunk_start + ep["local_end"] - 1
```

**What if LLM returns invalid indices?**
- ❌ `global_end > len(df)` → IndexError when accessing df
- ❌ `global_start > global_end` → Negative range
- ❌ `global_start < 0` → Negative indexing

**Fix Required**:
```python
global_start = chunk_start + ep["local_start"] - 1
global_end = chunk_start + ep["local_end"] - 1

# Validate
if global_start < 0 or global_end >= len(df) or global_start > global_end:
    print(f"⚠️ Warning: Invalid episode range {global_start}-{global_end}, skipping")
    continue

# Safe operation
episode_utterances = df.iloc[global_start:global_end+1]
```

---

### 3. **Global Session State - Not Thread Safe**
**File**: `app.py`, line 148  
**Severity**: CRITICAL

**Problem**: Single global `session` object shared across all users/requests:

```python
session = AnnotationSession()  # ← GLOBAL, shared across all users!
```

**What happens with multiple users?**
- ❌ User A uploads file → User A's episodes in session
- ❌ User B uploads file → Overwrites User A's episodes!
- ❌ User A clicks "Next" → Gets User B's episodes
- ❌ Data corruption & privacy issues

**Fix Required** (Gradio handles this):
```python
# Gradio automatically creates per-session state, but you need to use it:
# ❌ DON'T USE GLOBAL:
# session = AnnotationSession()  # WRONG

# ✅ DO THIS:
def create_ui():
    with gr.Blocks() as demo:
        # Use gr.State() for per-session state
        session_state = gr.State(AnnotationSession())
        # Pass to handlers...
```

OR safer: Store session in Gradio's built-in session management.

---

### 4. **No Validation of CSV Data Quality**
**File**: `src/csv_loader.py`, line 100-110  
**Severity**: HIGH

**Problem**: After loading CSV, no validation of actual data:

```python
df['start'] = df['start'].astype(float)
df['end'] = df['end'].astype(float)
# ← No checks after conversion!
```

**What if data is invalid?**
- ❌ `start >= end` → Negative duration
- ❌ `start < 0` or `end < 0` → Invalid timestamps
- ❌ `start == end` → Zero-length turns
- ❌ Speakers missing from data

**Fix Required**:
```python
# After conversion:
# 1. Check time validity
invalid_rows = df[df['start'] >= df['end']]
if len(invalid_rows) > 0:
    raise ValueError(f"{len(invalid_rows)} rows have start >= end")

# 2. Check non-negative
if (df['start'] < 0).any() or (df['end'] < 0).any():
    raise ValueError("Timestamps cannot be negative")

# 3. Check for duplicate consecutive speakers
# (optional, but useful for data quality)
```

---

## 🟠 IMPORTANT ISSUES

### 5. **Inefficient DataFrame Indexing in Loop**
**File**: `src/discourse_segmenter.py`, line 365-370  
**Severity**: HIGH (Performance)

**Problem**: Using `.iloc[]` and `.tolist()` inefficiently:

```python
episode_utterances = df.iloc[global_start:global_end+1]
duration_sec = episode_utterances.iloc[-1]['end'] - episode_utterances.iloc[0]['start']
speakers = list(set(episode_utterances['speaker'].tolist()))  # ← Inefficient
```

**Why it's slow:**
- Creates intermediate Series objects
- `.tolist()` materializes entire column
- For 1000+ episodes, this adds up

**Better approach**:
```python
# Use direct indexing
start_time = df.loc[global_start, 'start']
end_time = df.loc[global_end, 'end']
duration_sec = end_time - start_time

speakers = df.loc[global_start:global_end, 'speaker'].unique().tolist()
```

---

### 6. **API Key Hardcoded in Error Messages**
**File**: `src/discourse_segmenter.py`, multiple locations  
**Severity**: MEDIUM (Security)

**Problem**: While API key isn't hardcoded in code, error messages might expose it:

```python
try:
    client = OpenAI(api_key=api_key)
    # If client creation fails, traceback might show api_key
except Exception as e:
    print(f"❌ Error: {e}")  # Might include API key!
```

**Better practice**:
```python
if not api_key:
    raise ValueError(
        "OpenAI API key not found. "
        "Set OPENAI_API_KEY environment variable."
    )

try:
    client = OpenAI(api_key=api_key)
except Exception as e:
    # Log without exposing key
    raise ValueError("Failed to authenticate with OpenAI API")
```

---

### 7. **Missing "Previous Episode" Implementation**
**File**: `app.py`, line 449-452  
**Severity**: MEDIUM (Feature)

**Problem**: Previous button is stubbed out:

```python
prev_btn.click(
    fn=lambda: ("Not yet implemented", "", "", ""),
    outputs=[transcript_output, analysis_output, metadata_output, current_info]
)
```

**Issue**: Users can't go back. Limited to forward navigation.

**Fix**: Implement previous functionality:
```python
def prev_episode_handler():
    """Go to previous episode."""
    if session.current_idx > 0:
        session.current_idx -= 1
    
    episode = session.get_next_episode()
    if episode:
        transcript, analysis, metadata = display_episode(episode)
        current_info = f"Episode {session.current_idx + 1} of {len(session.episodes)}"
    else:
        current_info = "Already at first episode"
    
    return transcript, analysis, metadata, current_info

prev_btn.click(
    fn=prev_episode_handler,
    outputs=[transcript_output, analysis_output, metadata_output, current_info]
)
```

---

## 🟡 WARNINGS (Best Practices)

### 8. **No Logging Strategy**
Using `print()` instead of `logging`:

```python
# Current:
print(f"🔄 Segmenting {len(self.df)} utterances...")  # ← Not ideal

# Better:
import logging
logger = logging.getLogger(__name__)
logger.info(f"Segmenting {len(self.df)} utterances...")
```

---

### 9. **No Input Validation in display_episode()**
**File**: `app.py`, line 236-247

```python
if episode is None:
    return "", "", ""

if session.df is None:
    return "", "", ""

# But what if episode has missing keys?
start_turn = episode.get('start_turn', 0)  # ✅ Good
# But no check if indices are valid
```

**Should validate turn indices are in bounds**.

---

### 10. **Hardcoded Magic Numbers**
**File**: `src/discourse_segmenter.py`, line 306

```python
chunk_duration_sec: float = 600.0  # ← What is this? 10 minutes? Not obvious
```

**Better**:
```python
CHUNK_DURATION_SECONDS = 600.0  # 10 minutes
def segment_dialogue(df: pd.DataFrame, chunk_duration_sec: float = CHUNK_DURATION_SECONDS, ...):
```

---

## ✅ WHAT'S GOOD

1. **Architecture**: Clean separation of concerns (csv_loader, discourse_segmenter, app)
2. **Type Hints**: Good use of type annotations throughout
3. **Documentation**: Excellent docstrings and comments
4. **Error Messages**: User-friendly error messages in csv_loader
5. **Graceful Fallbacks**: Multiple encoding attempts for CSV loading
6. **Gradio Integration**: Clean UI structure and event binding

---

## 📋 PRIORITY FIXES

| Priority | Issue | File | Line | Impact |
|----------|-------|------|------|--------|
| 🔴 P0 | No error handling in LLM calls | discourse_segmenter.py | 298 | App crash on API failure |
| 🔴 P0 | Global session state not thread-safe | app.py | 148 | Data corruption with multiple users |
| 🔴 P0 | No validation of turn indices | discourse_segmenter.py | 362 | IndexError on invalid LLM response |
| 🟠 P1 | No CSV data quality validation | csv_loader.py | 100 | Silent failures with bad data |
| 🟠 P1 | Inefficient DataFrame indexing | discourse_segmenter.py | 365 | Performance issues with large files |
| 🟡 P2 | Missing "Previous" implementation | app.py | 449 | Poor UX |
| 🟡 P2 | No logging strategy | all files | - | Hard to debug in production |

---

## 🔧 RECOMMENDED ACTIONS

### Immediate (This Week)
1. ✅ Add try/catch around `call_llm_for_chunk()` calls
2. ✅ Add bounds checking for converted turn indices
3. ✅ Add CSV data validation (start < end, non-negative, etc.)
4. ✅ Implement previous episode button
5. ✅ Add basic logging

### Short Term (Next 2 Weeks)
1. Fix global session state → use Gradio's state management
2. Optimize DataFrame operations
3. Add unit tests for edge cases
4. Add integration tests for API failures

### Medium Term (This Month)
1. Add comprehensive error recovery
2. Implement caching for large files
3. Add monitoring/observability
4. Create runbook for common errors

---

## 🚀 QUICK WIN: Add Basic Error Handling

This one change would solve 3 critical issues:

```python
# In segment_dialogue(), line 298:
try:
    result = call_llm_for_chunk(
        chunk_df,
        monologue_summaries,
        overlaps,
        stack,
        bookmark,
        api_key
    )
except json.JSONDecodeError as e:
    print(f"⚠️ LLM returned invalid JSON for chunk {chunk_start}-{chunk_end}")
    print(f"   Skipping this chunk. Error: {e}")
    # Return empty episodes for this chunk
    current_turn = chunk_end + 1
    continue
except Exception as e:
    print(f"❌ Unexpected error processing chunk {chunk_start}-{chunk_end}: {e}")
    raise ValueError(f"Failed to process dialogue: {str(e)}")
```

---

## Summary

Your code is **well-structured and well-documented**, but needs **production hardening** before deployment to Hugging Face.

**Next steps**:
1. Fix the 3 🔴 critical issues
2. Push fixes to HF Space
3. Test with edge cases (bad data, API failures, multiple users)
4. Add the improvements for robustness

Want me to implement these fixes? 🚀
