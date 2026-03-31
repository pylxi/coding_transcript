"""
╔══════════════════════════════════════════════════════════════════════════════╗
║         🎙️  DIALOGUE EPISODE ANNOTATOR - MAIN APPLICATION                   ║
╚══════════════════════════════════════════════════════════════════════════════╝

ARCHITECTURE OVERVIEW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This application has three main layers:

1. DATA LAYER (src/csv_loader.py)
   └─ Handles CSV file loading with encoding fallbacks
   └─ Parses timestamps (MM:SS or HH:MM:SS format)
   └─ Validates required columns: speaker, start, end, text
   └─ Output: Normalized DataFrame with time columns in seconds

2. EXTRACTION LAYER (src/discourse_segmenter.py)
   └─ LLM-powered discourse analysis using Grosz & Sidner stack model
   └─ Uses GPT-4 for semantic analysis
   └─ Classifies 9 collaboration dimensions
   └─ Detects monologues and speaker overlaps
   └─ Returns: episodes with DSP labels, stack operations, dimensions
   └─ Handles large transcripts with bookmarking system

3. PRESENTATION LAYER (this file: app.py)
   └─ Gradio web interface
   └─ Episode display with analysis tabs
   └─ Monologue summaries
   └─ Collaboration dimension analysis
   └─ Status messages and error handling
   └─ Session state management

FILE DEPENDENCY FLOW:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    User CSV File
         ↓
    src/csv_loader.load_csv_file()  ← Validates & parses timestamps
         ↓
    DataFrame (normalized: speaker, start, end, text)
         ↓
    src/discourse_segmenter.segment_dialogue()
         ↓
         ├─ detect_monologues_without_content()
         ├─ detect_overlaps_without_content()
         ├─ summarize_monologues() [GPT-4 calls]
         ├─ call_llm_for_chunk() [GPT-4 calls]
         └─ Format episodes with DSP, dimensions, stack ops
         ↓
    List of Episode objects
         ↓
    app.py (display_episode)  ← Formats for UI display
         ↓
    Gradio UI  ← User sees formatted episodes with analysis

"""

import gradio as gr
from src.csv_loader import load_csv_file
from src.discourse_segmenter import segment_dialogue


# ════════════════════════════════════════════════════════════════════════════
# STATE MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════
# This class manages the entire user session, keeping track of:
# - Loaded CSV data (DataFrame)
# - Current episode index
# - All extracted episodes (pre-computed)
# - Session annotations

class AnnotationSession:
    """Manages dialogue annotation session state and episode navigation."""
    
    def __init__(self):
        """Initialize an empty session. Called once when app starts."""
        self.df = None
        self.episodes = []  # Pre-extracted episodes using discourse segmentation
        self.current_idx = 0
        self.annotations = []
    
    def load_csv(self, file):
        """
        Load CSV and segment into episodes using discourse model.
        
        PROCESS:
        1. Read CSV file (csv_loader validates and parses)
        2. Call segment_dialogue() to extract episodes
        3. Initialize navigation counters
        
        Args:
            file: Uploaded file object with .name attribute
            
        Returns:
            Status message for UI display
        """
        try:
            # Load CSV
            self.df = load_csv_file(file.name)
            self.current_idx = 0
            self.annotations = []
            
            # Segment using discourse model (requires GPT-4)
            print(f"🔄 Segmenting {len(self.df)} utterances using discourse model...")
            self.episodes = segment_dialogue(self.df)
            
            return f"✅ Loaded {len(self.df)} utterances - {len(self.episodes)} episodes extracted using Grosz & Sidner discourse model"
        
        except ValueError as e:
            return f"❌ Validation Error: {str(e)}"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def get_next_episode(self):
        """
        Get next episode from list.
        
        Returns:
            Episode dict or None if finished
        """
        if self.df is None or self.current_idx >= len(self.episodes):
            return None
        
        episode = self.episodes[self.current_idx]
        return episode
    
    def move_to_next(self):
        """Advance session to next episode."""
        self.current_idx += 1


session = AnnotationSession()


# ════════════════════════════════════════════════════════════════════════════
# EVENT HANDLERS
# ════════════════════════════════════════════════════════════════════════════
# These functions respond to user interactions (button clicks, file uploads).
# Gradio calls them automatically when users interact.
#
# Flow:
# 1. User uploads file
# 2. load_file_handler() called
# 3. Session loads CSV and segments episodes
# 4. First episode displayed via display_episode()
# 5. User clicks "Next"
# 6. next_episode_handler() called
# 7. display_episode() shows next episode

def load_file_handler(file):
    """
    Handle file upload button click.
    
    STEPS:
    1. Call session.load_csv() to load file and extract episodes
    2. If successful, get first episode
    3. Call display_episode() to format for display
    4. Return all outputs to UI
    
    Args:
        file: Uploaded file object
        
    Returns:
        Tuple of (status_msg, transcript, analysis, metadata)
    """
    status = session.load_csv(file)
    
    if "✅" in status:
        # Load first episode
        episode = session.get_next_episode()
        if episode:
            transcript, analysis, metadata = display_episode(episode)
            return status, transcript, analysis, metadata
    
    return status, "", "", ""


def display_episode(episode):
    """
    Format episode data for UI display.
    
    Handles discourse-based episodes with:
    - DSP (Discourse Segment Purpose) labels
    - Collaboration dimensions analysis
    - Stack operations
    - Monologue summaries
    - Speaker information
    
    Args:
        episode: Episode dict from discourse_segmenter
        
    Returns:
        Tuple of (transcript_text, analysis_text, metadata_text)
    """
    if episode is None:
        return "", "", ""
    
    if session.df is None:
        return "", "", ""
    
    # ─────────────────────────────────────────────────────────────────────────
    # 1. BUILD TRANSCRIPT (dialogue turns with speaker changes)
    # ─────────────────────────────────────────────────────────────────────────
    
    transcript = ""
    last_speaker = None
    
    # Build dialogue text from episode turn range
    start_turn = episode.get('start_turn', 0)
    end_turn = episode.get('end_turn', 0)
    
    for i in range(start_turn, end_turn + 1):
        if i < len(session.df):
            row = session.df.iloc[i]
            speaker = row.get('speaker', 'Unknown')
            text = row.get('text', '')
            start_time = row.get('start', 0)
            end_time = row.get('end', 0)
            
            # Add speaker header when speaker changes
            if speaker != last_speaker:
                transcript += f"\n[{speaker}]\n"
                last_speaker = speaker
            
            # Add turn with timestamp
            duration = end_time - start_time
            transcript += f"[{start_time:.1f}s-{end_time:.1f}s] {text}\n"
    
    # ─────────────────────────────────────────────────────────────────────────
    # 2. BUILD ANALYSIS (discourse information)
    # ─────────────────────────────────────────────────────────────────────────
    
    analysis = ""
    
    # Discourse Segment Purpose
    dsp = episode.get('dsp', 'Unknown')
    analysis += f"📍 **Discourse Segment Purpose (DSP)**: {dsp}\n\n"
    
    # Stack Operation
    stack_op = episode.get('stack_operation', 'continue')
    analysis += f"🔗 **Stack Operation**: {stack_op}\n\n"
    
    # Collaboration Dimensions
    dimensions = episode.get('dimensions', [])
    if dimensions:
        analysis += f"🤝 **Collaboration Dimensions**:\n"
        for dim in dimensions:
            analysis += f"  • {dim}\n"
    else:
        analysis += f"🤝 **Collaboration Dimensions**: Not specified\n"
    
    # ─────────────────────────────────────────────────────────────────────────
    # 3. BUILD METADATA (episode statistics)
    # ─────────────────────────────────────────────────────────────────────────
    
    metadata = ""
    
    # Episode duration
    duration_min = episode.get('duration_minutes', 0)
    duration_sec = episode.get('duration_seconds', 0)
    metadata += f"⏱️  **Duration**: {duration_min:.1f} min ({duration_sec:.0f}s)\n\n"
    
    # Utterance count
    utt_count = episode.get('utterance_count', 0)
    metadata += f"📢 **Utterances**: {utt_count}\n\n"
    
    # Speakers
    speakers = episode.get('speakers', 'Unknown')
    num_speakers = episode.get('num_speakers', 0)
    metadata += f"👥 **Speakers** ({num_speakers}): {speakers}\n\n"
    
    # Episode ID
    episode_id = episode.get('episode_id', 0)
    metadata += f"🆔 **Episode ID**: {episode_id}\n"
    metadata += f"📍 **Turn Range**: {start_turn} - {end_turn}\n"
    
    return transcript, analysis, metadata


def next_episode_handler():
    """
    Handle "Next Episode" button click.
    
    STEPS:
    1. Advance session to next episode
    2. Get the new episode
    3. Call display_episode() to format it
    4. Return outputs to UI
    
    Returns:
        Tuple of (transcript, analysis, metadata, current_info)
    """
    session.move_to_next()
    episode = session.get_next_episode()
    
    if episode is None:
        return "", "", "", f"✅ Finished! Annotated {len(session.episodes)} episodes"
    
    transcript, analysis, metadata = display_episode(episode)
    current_info = f"Episode {session.current_idx + 1} of {len(session.episodes)}"
    
    return transcript, analysis, metadata, current_info


# ════════════════════════════════════════════════════════════════════════════
# GRADIO UI - LAYOUT & INTERACTION
# ════════════════════════════════════════════════════════════════════════════
# Defines the web interface structure:
#
# ┌─────────────────────────────────────────────────────────────────┐
# │  FILE INPUT SECTION                                             │
# │  ┌────────────────┐  ┌──────────────────────────────────────┐  │
# │  │ Upload CSV     │  │ Status Message                       │  │
# │  └────────────────┘  └──────────────────────────────────────┘  │
# ├─────────────────────────────────────────────────────────────────┤
# │  EPISODE DISPLAY (Two Tabs)                                     │
# │  ┌──────────────────────────────────────────────────────────┐   │
# │  │ TAB 1: TRANSCRIPT                                        │   │
# │  │ ┌──────────────────────────────────────────────────────┐ │   │
# │  │ │ [Speaker]                                            │ │   │
# │  │ │ [timestamp]: utterance text...                       │ │   │
# │  │ └──────────────────────────────────────────────────────┘ │   │
# │  ├──────────────────────────────────────────────────────────┤   │
# │  │ TAB 2: ANALYSIS                                          │   │
# │  │ ┌──────────────────────────────────────────────────────┐ │   │
# │  │ │ DSP: Clarify deadline                               │ │   │
# │  │ │ Stack Op: PUSH                                       │ │   │
# │  │ │ Dimensions: Sustaining mutual understanding         │ │   │
# │  │ └──────────────────────────────────────────────────────┘ │   │
# │  └──────────────────────────────────────────────────────────┘   │
# │  ┌──────────────────────────────────────────────────────────┐   │
# │  │ TAB 3: METADATA                                          │   │
# │  │ Duration: 2.5 min  |  Speakers: Alice, Bob             │   │
# │  └──────────────────────────────────────────────────────────┘   │
# ├─────────────────────────────────────────────────────────────────┤
# │  NAVIGATION BUTTONS                                             │
# │  ┌──────────────────┐  ┌──────────────────┐                    │
# │  │ ⬅️  Previous      │  │  Next ➡️         │                    │
# │  └──────────────────┘  └──────────────────┘                    │
# │  Episode 1 of 15                                                │
# └─────────────────────────────────────────────────────────────────┘

def create_ui():
    """
    Create and return Gradio interface.
    
    Returns:
        Configured Gradio Blocks object
    """
    with gr.Blocks(title="Dialogue Episode Annotator") as demo:
        
        gr.Markdown("# 🎙️ Dialogue Episode Annotator")
        gr.Markdown("*Using Grosz & Sidner Discourse Stack Model for episode segmentation*")
        
        # ─────────────────────────────────────────────────────────────────────
        # INPUT SECTION
        # ─────────────────────────────────────────────────────────────────────
        
        with gr.Row():
            file_input = gr.File(
                label="📁 Upload Transcript CSV",
                file_types=[".csv"],
                file_count="single"
            )
            status_output = gr.Textbox(
                label="Status",
                interactive=False,
                lines=2
            )
        
        # Load button
        load_btn = gr.Button("📂 Load & Segment Transcript", variant="primary")
        
        # ─────────────────────────────────────────────────────────────────────
        # EPISODE DISPLAY SECTION (Multiple Tabs)
        # ─────────────────────────────────────────────────────────────────────
        
        gr.Markdown("## 📖 Episode Display")
        
        with gr.Tabs():
            # Tab 1: Transcript
            with gr.TabItem("💬 Transcript"):
                transcript_output = gr.Textbox(
                    label="Dialogue",
                    interactive=False,
                    lines=12,
                    max_lines=20
                )
            
            # Tab 2: Analysis
            with gr.TabItem("📊 Analysis"):
                analysis_output = gr.Textbox(
                    label="Discourse Analysis",
                    interactive=False,
                    lines=10,
                    max_lines=15
                )
            
            # Tab 3: Metadata
            with gr.TabItem("📋 Metadata"):
                metadata_output = gr.Textbox(
                    label="Episode Information",
                    interactive=False,
                    lines=8,
                    max_lines=12
                )
        
        # ─────────────────────────────────────────────────────────────────────
        # NAVIGATION SECTION
        # ─────────────────────────────────────────────────────────────────────
        
        gr.Markdown("## ⏭️ Navigation")
        
        with gr.Row():
            prev_btn = gr.Button("⬅️ Previous Episode", variant="secondary")
            next_btn = gr.Button("Next Episode ➡️", variant="secondary")
        
        current_info = gr.Textbox(
            label="Progress",
            interactive=False,
            value="No file loaded"
        )
        
        # ─────────────────────────────────────────────────────────────────────
        # EVENT BINDINGS - Link UI elements to handlers
        # ─────────────────────────────────────────────────────────────────────
        # When user clicks buttons, these handlers execute and update UI outputs.
        #
        # Load Button Flow:
        #   User clicks → load_file_handler() runs
        #   → Returns (status, transcript, analysis, metadata)
        #   → Updates 4 outputs in UI
        #
        # Next Button Flow:
        #   User clicks → next_episode_handler() runs
        #   → Returns (transcript, analysis, metadata, progress)
        #   → Updates 4 outputs in UI
        
        load_btn.click(
            fn=load_file_handler,
            inputs=[file_input],
            outputs=[status_output, transcript_output, analysis_output, metadata_output]
        )
        
        next_btn.click(
            fn=next_episode_handler,
            outputs=[transcript_output, analysis_output, metadata_output, current_info]
        )
        
        prev_btn.click(
            fn=lambda: ("Not yet implemented", "", "", ""),
            outputs=[transcript_output, analysis_output, metadata_output, current_info]
        )
    
    return demo


# ════════════════════════════════════════════════════════════════════════════
# APPLICATION LAUNCH
# ════════════════════════════════════════════════════════════════════════════
# When this file is run directly (python app.py):
# 1. create_ui() generates the Gradio interface
# 2. demo.launch() starts the web server
# 3. Gradio prints the URL (usually http://localhost:7860)
# 4. User opens URL in browser
# 5. Application is ready for use
#
# The session object persists across all user interactions in a single browser tab.
# Each new browser session gets a new AnnotationSession instance.

if __name__ == "__main__":
    demo = create_ui()
    demo.launch(share=False)
