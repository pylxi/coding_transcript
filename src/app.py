"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         🎙️  DIALOGUE EPISODE ANNOTATOR - MAIN APPLICATION                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

ARCHITECTURE OVERVIEW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This application has three main layers:

1. DATA LAYER (csv_loader.py)
   └─ Handles CSV file loading with encoding fallbacks
   └─ Parses timestamps (MM:SS or HH:MM:SS format)
   └─ Validates required columns: speaker, timestamp, utterance
   └─ Output: Normalized DataFrame with timestamp_seconds column

2. EXTRACTION LAYER (two methods available)
   ├─ Similarity-Based (episode_extractor.py) [DEFAULT]
   │  └─ Fast, local, free
   │  └─ Uses sentence-transformers for embeddings
   │  └─ Detects topic shifts via cosine similarity
   │  └─ Identifies monologues (>90s single speaker)
   │  └─ Returns: episodes with duration, speakers, topics, reasons
   │
   └─ Discourse Stack (discourse_segmenter.py) [OPTIONAL - requires GPT-4]
      └─ LLM-powered, detailed discourse analysis
      └─ Implements Grosz & Sidner discourse model
      └─ Classifies 9 collaboration dimensions
      └─ Returns: episodes with DSP labels, stack operations, dimensions

3. PRESENTATION LAYER (this file: app.py)
   └─ Gradio web interface
   └─ Episode display with two analysis tabs
   └─ Method selection (Similarity vs Discourse)
   └─ Status messages and error handling
   └─ Session state management

FILE DEPENDENCY FLOW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    User CSV File
         ↓
    csv_loader.load_csv_file()  ← Validates & parses timestamps
         ↓
    DataFrame (normalized)
         ↓
    ┌────────────────────────────┐
    ↓                            ↓
episode_extractor.py      discourse_segmenter.py
(Similarity method)        (Discourse Stack method)
    ↓                            ↓
    └────────────────────────────┘
         ↓
    Episode objects
         ↓
    app.py (display_episode)  ← Formats for UI
         ↓
    Gradio UI  ← User sees formatted episodes

"""

# ════════════════════════════════════════════════════════════════════════════
# IMPORTS
# ════════════════════════════════════════════════════════════════════════════

import gradio as gr
from csv_loader import load_csv_file
from episode_extractor import EpisodeExtractor
try:
    from discourse_segmenter import segment_dialogue
    DISCOURSE_AVAILABLE = True
except ImportError:
    DISCOURSE_AVAILABLE = False


# ════════════════════════════════════════════════════════════════════════════
# STATE MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════
# This class manages the entire user session, keeping track of:
# - Loaded CSV data (DataFrame)
# - Current episode index (position in file)
# - Extraction method (similarity or discourse)
# - Pre-extracted episodes (for discourse method)

class AnnotationSession:
    def __init__(self):
        """Initialize an empty session. Called once when app starts."""
        self.df = None
        self.extractor = None
        self.discourse_episodes = None  # For discourse-based segmentation
        self.current_idx = 0
        self.annotations = []
        self.segmentation_method = "similarity"  # or "discourse"
    
    def load_csv(self, file, method="similarity"):
        """
        Load CSV and initialize extraction.
        
        PROCESS:
        1. Read CSV file (csv_loader handles validation)
        2. Choose extraction method (similarity or discourse)
        3. Initialize appropriate extractor
        
        Returns:
            Status message for UI display
        """
        try:
            self.df = load_csv_file(file.name)
            # Normalize method name
            method_normalized = "discourse" if "discourse" in method.lower() else "similarity"
            self.segmentation_method = method_normalized
            self.current_idx = 0
            self.annotations = []
            
            if method_normalized == "discourse":
                if not DISCOURSE_AVAILABLE:
                    return "❌ Discourse segmenter not available. Install openai package."
                # Pre-segment using discourse model
                try:
                    self.discourse_episodes = segment_dialogue(self.df)
                    return f"✅ Loaded {len(self.df)} utterances - {len(self.discourse_episodes)} episodes extracted"
                except ValueError as e:
                    return f"❌ Error: {str(e)}"
            else:
                # Use similarity-based extraction
                self.extractor = EpisodeExtractor()
                return f"✅ Loaded {len(self.df)} utterances"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def get_next_episode(self):
        """
        Get next episode from file.
        
        METHOD DIFFERENCES:
        - Similarity: Extracts on-demand (slower per call, faster startup)
        - Discourse: Returns pre-extracted episode (fast, all upfront)
        
        Returns:
            Episode dict or None if finished
        """
        if self.df is None:
            return None
        
        if self.segmentation_method == "discourse":
            if self.discourse_episodes is None or self.current_idx >= len(self.discourse_episodes):
                return None
            return self.discourse_episodes[self.current_idx]
        else:
            if self.extractor is None:
                return None
            return self.extractor.extract_next_episode(self.df, self.current_idx)
    
    def move_to_next(self, episode):
        """
        Advance session to next episode.
        
        Different methods advance differently:
        - Discourse: Just increment counter (fixed list)
        - Similarity: Jump to next_idx (variable step size)
        """
        if self.segmentation_method == "discourse":
            self.current_idx += 1
        else:
            if episode:
                self.current_idx = episode['next_idx']


session = AnnotationSession()


# ════════════════════════════════════════════════════════════════════════════
# EVENT HANDLERS
# ════════════════════════════════════════════════════════════════════════════
# These functions respond to user button clicks and update the UI.
# Gradio calls them automatically when users interact.
#
# Flow:
# 1. User uploads file + selects method
# 2. load_file_handler() called
# 3. Session loads CSV
# 4. Session extracts/loads first episode
# 5. display_episode() formats it
# 6. Results shown in UI
#
# 7. User clicks "Next"
# 8. next_episode_handler() called
# 9. Session advances to next episode
# 10. display_episode() formats it
# 11. Results shown in UI

def load_file_handler(file, method="similarity"):
    """
    Handle file upload button click.
    
    STEPS:
    1. Call session.load_csv() to load and validate file
    2. If successful, get first episode
    3. Call display_episode() to format for display
    4. Return all outputs to UI
    
    Returns:
        Tuple of (status_msg, transcript, prompt, settings)
    """
    status = session.load_csv(file, method)
    
    if "✅" in status:
        # Load first episode
        episode = session.get_next_episode()
        if episode:
            transcript, prompt, settings = display_episode(episode)
            return status, transcript, prompt, settings
    
    return status, "", "", ""


def display_episode(episode):
    """
    Format episode data for UI display.
    
    Handles two different episode formats:
    1. Similarity-based: has 'utterances' list
    2. Discourse-based: has 'dsp', 'dimensions', 'stack_operation'
    
    Returns:
        Tuple of (transcript_with_summary, analysis_tab, settings_tab)
    
    The transcript includes:
    - Episode metadata (duration, speakers, etc)
    - Full dialogue turns with speaker changes
    - Monologue summaries (if any)
    """
    if episode is None:
        return "", "", ""
    
    # Check if this is a discourse-based episode
    if 'dsp' in episode:  # Discourse-based
        # Build transcript from utterances in the range
        transcript = ""
        last_speaker = None
        
        # Get utterances from start_turn to end_turn
        for i in range(episode['start_turn'], episode['end_turn'] + 1):
            if i < len(session.df):
                utt = session.df.iloc[i]
                if utt['speaker'] != last_speaker:
                    transcript += f"\n[{utt['speaker']}]\n"
                    last_speaker = utt['speaker']
                timestamp = utt.get('timestamp', f"{utt['start']:.1f}s")
                transcript += f"{timestamp}: {utt['utterance']}\n"
        
        # Build episode summary
        summary = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EPISODE #{episode.get('start_turn', '?')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 Discourse Segment Purpose (DSP): {episode.get('dsp', 'N/A')}
📚 Stack Operation: {episode.get('stack_operation', 'N/A')}
📊 Collaboration Dimensions: {', '.join(episode.get('dimensions', []))}
🔄 Turns: {episode.get('start_turn', '?')} - {episode.get('end_turn', '?')}
"""
        
        # AI Settings for modal
        ai_settings = f"""
🤖 DISCOURSE ANALYSIS

Method: Grosz & Sidner Stack Model
Model: GPT-4

📋 DISCOURSE SEGMENT PURPOSE:
{episode.get('dsp', 'N/A')}

📚 COLLABORATION DIMENSIONS:
{chr(10).join('  ✓ ' + d for d in episode.get('dimensions', ['N/A']))}

🔄 STACK OPERATION:
{episode.get('stack_operation', 'N/A')}

Turn Range: {episode.get('start_turn', '?')} - {episode.get('end_turn', '?')}
"""
        
        return summary + f"\n{transcript}", ai_settings, ai_settings
    
    else:  # Similarity-based (legacy)
        # Build transcript (without monologues - they have summaries)
        transcript = ""
        last_speaker = None
        
        for utt in episode['utterances']:
            # Add speaker change indicator
            if utt['speaker'] != last_speaker:
                transcript += f"\n[{utt['speaker']}]\n"
                last_speaker = utt['speaker']
            
            transcript += f"{utt['timestamp']}: {utt['utterance']}\n"
        
        # Build episode summary
        summary = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EPISODE #{episode['episode_id']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏱️  Duration: {episode['duration_minutes']:.1f} minutes
💬 Utterances: {episode['utterance_count']}
👥 Participants: {episode['num_speakers']} ({episode['speakers']})
"""
        
        # AI Settings for modal
        ai_settings = f"""
🤖 EPISODE EXTRACTION SETTINGS

Model: all-MiniLM-L6-v2
Algorithm: Similarity-based segmentation

⚙️ PARAMETERS:
├─ Similarity Threshold: 0.50
├─ Min Episode Length: 5 utterances
├─ Max Episode Length: 30 utterances
├─ Min Episode Duration: 60 seconds
├─ Max Episode Duration: 300 seconds
├─ Monologue Threshold: 90 seconds
└─ Min Speakers Required: 2

WHY THIS EPISODE?
"""
        for reason in episode['reasons']:
            ai_settings += f"  ✓ {reason}\n"
        
        return summary + f"\n{transcript}", episode['prompt'], ai_settings


def next_episode_handler():
    """
    Handle "Next Episode" button click.
    
    STEPS:
    1. Verify file is loaded
    2. Get next episode from session
    3. If no more episodes, show completion message
    4. Otherwise, display next episode
    
    Returns:
        Tuple of (transcript, prompt, settings)
    """
    if session.df is None:
        return "❌ No file loaded", "", ""
    
    episode = session.get_next_episode()
    if episode is None:
        return "✅ All episodes processed!", "", ""
    
    session.move_to_next(episode)
    transcript, prompt, settings = display_episode(episode)
    return transcript, prompt, settings


# ════════════════════════════════════════════════════════════════════════════
# GRADIO USER INTERFACE
# ════════════════════════════════════════════════════════════════════════════
# This section defines the web interface that users see and interact with.
#
# LAYOUT:
#
#  ┌─────────────────────────────────────────────────────────────────┐
#  │                  🎙️ Dialogue Episode Annotator                   │
#  ├─────────────────────────────────────────────────────────────────┤
#  │                                                                   │
#  │  Step 1: Load CSV File                                          │
#  │  ┌────────────────┬──────────────────┬──────────┐                │
#  │  │ [Browse File]  │ [Similarity ●   ] │ [Load]   │                │
#  │  └────────────────┴──────────────────┴──────────┘                │
#  │  Status: ✅ Loaded 100 utterances                                │
#  │                                                                   │
#  │  Step 2: Review Episodes & Analysis                             │
#  │  ┌──────────────────────────────┬────────────────────────────┐  │
#  │  │      📝 TRANSCRIPT            │   🔍 ANALYSIS MODAL        │  │
#  │  │                              │  ┌──────────────────────┐  │  │
#  │  │ EPISODE #0                   │  │ 📊 Analysis │⚙️ Set │  │  │
#  │  │                              │  ├──────────────────────┤  │  │
#  │  │ Duration: 2.5 min           │  │                      │  │  │
#  │  │ Participants: Alice, Bob    │  │ [AI Analysis Text]   │  │  │
#  │  │                              │  │                      │  │  │
#  │  │ [Alice]                      │  │ [Copy Button]        │  │  │
#  │  │ 0:05: Hello Bob             │  │                      │  │  │
#  │  │                              │  │                      │  │  │
#  │  │ [Bob]                        │  │                      │  │  │
#  │  │ 0:10: Hi there              │  │                      │  │  │
#  │  │                              │  └──────────────────────┘  │  │
#  │  └──────────────────────────────┴────────────────────────────┘  │
#  │                                                                   │
#  │  ┌───────────────────────────────────────────────────────────┐  │
#  │  │             [Next Episode]                                │  │
#  │  └───────────────────────────────────────────────────────────┘  │
#  │                                                                   │
#  └─────────────────────────────────────────────────────────────────┘

with gr.Blocks(title="Dialogue Episode Annotator") as demo:
    gr.Markdown("# 🎙️ Dialogue Episode Annotator")
    gr.Markdown("Extract and annotate coherent episodes from dialogue transcripts")
    
    # ────────────────────────────────────────────────────────────────
    # SECTION 1: FILE UPLOAD & METHOD SELECTION
    # ────────────────────────────────────────────────────────────────
    gr.Markdown("## 📂 Step 1: Load CSV File")
    with gr.Row():
        csv_input = gr.File(label="CSV File", file_types=[".csv"])
        method_radio = gr.Radio(
            choices=["Similarity-Based", "Discourse Stack (GPT-4)"] if DISCOURSE_AVAILABLE else ["Similarity-Based"],
            value="Similarity-Based",
            label="Segmentation Method",
            info="Choose episode detection method"
        )
        load_btn = gr.Button("Load", variant="primary")
    
    load_status = gr.Textbox(label="Status", interactive=False, lines=2)
    
    # ────────────────────────────────────────────────────────────────
    # SECTION 2: EPISODE DISPLAY WITH ANALYSIS MODAL
    # ────────────────────────────────────────────────────────────────
    gr.Markdown("## 📊 Step 2: Review Episodes & Analysis")
    
    with gr.Row():
        # LEFT COLUMN: Transcript (70% width)
        with gr.Column(scale=3):
            episode_display = gr.Textbox(label="📝 Transcript", interactive=False, lines=25)
        
        # RIGHT COLUMN: Analysis Modal with Tabs (30% width)
        with gr.Column(scale=2):
            gr.Markdown("### 🔍 Episode Analysis Modal")
            
            # Two tabs: Analysis & Settings
            with gr.Tabs():
                with gr.TabItem("📊 Analysis"):
                    # Analysis tab shows AI-generated insights
                    prompt_display = gr.Textbox(
                        label="AI Analysis", 
                        interactive=False, 
                        lines=18,
                        show_copy_button=True
                    )
                
                with gr.TabItem("⚙️ Settings"):
                    # Settings tab shows extraction parameters and rationale
                    settings_display = gr.Textbox(
                        label="Extraction Settings & Parameters",
                        interactive=False,
                        lines=18,
                        show_copy_button=True
                    )
    
    # ────────────────────────────────────────────────────────────────
    # BUTTON & EVENT HANDLERS
    # ────────────────────────────────────────────────────────────────
    next_btn = gr.Button("Next Episode", variant="primary", size="lg")
    
    # When user clicks "Load":
    # 1. Pass file and method selection to load_file_handler
    # 2. Handler returns (status, transcript, prompt, settings)
    # 3. Gradio displays outputs in corresponding textboxes
    load_btn.click(
        load_file_handler,
        inputs=[csv_input, method_radio],
        outputs=[load_status, episode_display, prompt_display, settings_display]
    )
    
    # When user clicks "Next Episode":
    # 1. Call next_episode_handler (no inputs needed, uses session state)
    # 2. Handler returns (transcript, prompt, settings)
    # 3. Gradio updates the display
    next_btn.click(
        next_episode_handler,
        outputs=[episode_display, prompt_display, settings_display]
    )


# ════════════════════════════════════════════════════════════════════════════
# APPLICATION LAUNCH
# ════════════════════════════════════════════════════════════════════════════
# This section runs when you execute: python app.py
#
# Gradio will:
# 1. Start a local web server
# 2. Open it at http://localhost:7860
# 3. Keep running until you press Ctrl+C
#
# The 'demo' object contains the entire UI defined above.

if __name__ == "__main__":
    # Launch the Gradio interface
    # share=True would create a public link, but we use default (local only)
    demo.launch()
