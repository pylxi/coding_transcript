"""
Gradio Web Interface for Transcript Processor

A beautiful, responsive web UI for uploading and analyzing transcript CSVs
with real-time validation, analytics, and optional AI-powered summarization.
"""

import os
import pandas as pd
import gradio as gr
from typing import Tuple, Optional
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from dialogue_episode_annotator.app.analytics import compute_analytics
    from dialogue_episode_annotator.app.file_checker import check_csv_format
    from dialogue_episode_annotator.app.summarizer import summarize_transcript
except ImportError:
    try:
        from app.analytics import compute_analytics
        from app.file_checker import check_csv_format
        from app.summarizer import summarize_transcript
    except ImportError:
        # Fallback for development
        compute_analytics = lambda df: {"messages": "Analytics module not found"}
        check_csv_format = lambda df: (True, "Format check passed")
        summarize_transcript = lambda df, **kw: "Summary not available"


def process_transcript(
    csv_file,
    enable_summary: bool = False,
    max_summary_words: int = 150
) -> Tuple[str, str, str]:
    """
    Process uploaded transcript CSV file and return analytics + optional summary.
    
    Args:
        csv_file: Uploaded CSV file
        enable_summary: Whether to generate AI summary
        max_summary_words: Max words in summary
        
    Returns:
        Tuple of (analytics_html, summary_text, status_message)
    """
    try:
        if csv_file is None:
            return "", "", "❌ No file uploaded"
        
        # Load CSV
        df = pd.read_csv(csv_file.name)
        
        # Validate format
        is_valid, validation_msg = check_csv_format(df)
        if not is_valid:
            return "", "", f"❌ Validation Error: {validation_msg}"
        
        # Compute analytics
        analytics = compute_analytics(df)
        
        # Build analytics display
        analytics_html = f"""
        <div style="background: #f0f4f8; padding: 20px; border-radius: 8px; margin: 10px 0;">
            <h3>📊 Analytics Results</h3>
            <pre style="background: white; padding: 15px; border-radius: 6px; overflow-x: auto;">
{analytics.get('messages', 'No analytics available')}
            </pre>
        </div>
        """
        
        # Generate summary if requested
        summary_text = ""
        if enable_summary:
            try:
                summary_text = summarize_transcript(
                    df,
                    max_words=max_summary_words
                )
                summary_html = f"""
                <div style="background: #e8f5e9; padding: 20px; border-radius: 8px; margin: 10px 0;">
                    <h3>✨ AI Summary</h3>
                    <p style="line-height: 1.6; font-size: 16px;">{summary_text}</p>
                </div>
                """
                analytics_html += summary_html
            except Exception as e:
                analytics_html += f'<div style="background: #fff3cd; padding: 10px;">⚠️ Summary failed: {str(e)}</div>'
        
        status = "✅ Processing complete!"
        return analytics_html, summary_text, status
        
    except Exception as e:
        return "", "", f"❌ Error: {str(e)}"


def create_interface():
    """Create and return the Gradio interface."""
    
    with gr.Blocks(title="Transcript Processor", theme=gr.themes.Soft()) as interface:
        gr.Markdown("""
        # 📝 Transcript Processor
        
        Upload your CSV transcript and get instant analytics with optional AI-powered summarization.
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Upload File")
                csv_file = gr.File(
                    label="📤 Upload CSV",
                    file_types=[".csv"],
                    type="filepath"
                )
                
                gr.Markdown("### Options")
                enable_summary = gr.Checkbox(
                    label="✨ Enable AI Summarization",
                    value=False
                )
                max_words = gr.Slider(
                    label="📏 Max Summary Words",
                    minimum=50,
                    maximum=500,
                    value=150,
                    step=10
                )
                
                process_btn = gr.Button(
                    "🚀 Process Transcript",
                    variant="primary",
                    size="lg"
                )
            
            with gr.Column(scale=2):
                gr.Markdown("### Results")
                status_msg = gr.Textbox(
                    label="Status",
                    interactive=False,
                    lines=1
                )
                
                analytics_output = gr.HTML(
                    value="<p style='color: #999;'>Upload a CSV and click Process</p>",
                    label="Analytics & Summary"
                )
                
                summary_output = gr.Textbox(
                    label="Summary Text (for copying)",
                    interactive=False,
                    lines=5,
                    visible=True
                )
        
        # Connect button
        process_btn.click(
            fn=process_transcript,
            inputs=[csv_file, enable_summary, max_words],
            outputs=[analytics_output, summary_output, status_msg]
        )
        
        gr.Markdown("""
        ---
        
        ### 📋 CSV Format Requirements
        
        Your CSV should have these columns:
        - `speaker`: Name of the speaker
        - `text`: What they said
        - `timestamp`: When they spoke (optional)
        
        ### Features
        - ✅ Real-time CSV validation
        - 📊 Analytics computation (speakers, duration, words)
        - ✨ Optional AI summarization
        - 📱 Mobile-friendly interface
        - 🔒 No data stored on servers
        """)
    
    return interface


if __name__ == "__main__":
    interface = create_interface()
    interface.launch(share=False)
