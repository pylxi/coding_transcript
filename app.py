import gradio as gr
import pandas as pd
from utils import read_excel_utterances, create_episode_dataframe, export_annotated_data
from segmentation import segment_by_similarity

# ============================================================================
# State Management
# ============================================================================

class AnnotationState:
    """Manages application state"""
    def __init__(self):
        self.episodes_df = None
        self.original_df = None
    
    def load_file(self, file, threshold):
        """Process uploaded file"""
        self.original_df = read_excel_utterances(file)
        utterances = self.original_df['utterance'].tolist()
        boundaries = segment_by_similarity(utterances, threshold)
        self.episodes_df = create_episode_dataframe(self.original_df, boundaries)
        return self.episodes_df
    
    def get_episode_choices(self):
        """Get dropdown choices"""
        if self.episodes_df is None:
            return []
        return [
            (str(row['episode_id']), f"Episode {row['episode_id']}: {row['speakers']}")
            for _, row in self.episodes_df.iterrows()
        ]
    
    def get_episode_content(self, episode_id):
        """Get episode text content"""
        if self.episodes_df is None or not episode_id:
            return ""
        try:
            ep = self.episodes_df[self.episodes_df['episode_id'] == int(episode_id)]
            return ep.iloc[0]['utterances'] if len(ep) > 0 else ""
        except:
            return ""
    
    def save_annotation(self, episode_id, metacog_type, notes):
        """Save annotation"""
        if self.episodes_df is None:
            return "Error: No data loaded"
        try:
            idx = self.episodes_df[self.episodes_df['episode_id'] == int(episode_id)].index
            if len(idx) > 0:
                self.episodes_df.loc[idx[0], 'metacognition_type'] = metacog_type
                self.episodes_df.loc[idx[0], 'notes'] = notes
                return f"✓ Saved Episode {episode_id}"
            return "Error: Episode not found"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def export(self):
        """Export to Excel"""
        if self.episodes_df is None:
            raise ValueError("No data to export")
        return export_annotated_data(self.episodes_df)


state = AnnotationState()

# ============================================================================
# Metacognition Types
# ============================================================================

METACOG_TYPES = [
    "Planning",
    "Monitoring",
    "Evaluation",
    "Regulation",
    "None"
]

# ============================================================================
# Gradio Interface
# ============================================================================

with gr.Blocks(title="Dialogue Episode Annotator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# Dialogue Episode Annotator")
    gr.Markdown("Upload dialogue data, segment into episodes, and annotate.")
    
    # Upload Section
    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="Upload Excel", file_types=[".xlsx", ".xls"])
            threshold = gr.Slider(0.3, 0.8, 0.5, label="Sensitivity", step=0.05)
            process_btn = gr.Button("Segment", variant="primary")
        with gr.Column(scale=2):
            preview = gr.Dataframe(label="Preview")
    
    # Annotation Section
    gr.Markdown("---")
    with gr.Row():
        with gr.Column(scale=1):
            episode_select = gr.Dropdown(label="Episode", choices=[])
            metacog_select = gr.Dropdown(label="Type", choices=METACOG_TYPES)
            notes = gr.Textbox(label="Notes", lines=2)
            save_btn = gr.Button("Save", variant="secondary")
            status = gr.Textbox(label="Status", interactive=False)
        with gr.Column(scale=2):
            content = gr.Textbox(label="Content", lines=10, interactive=False)
    
    # Export Section
    gr.Markdown("---")
    with gr.Row():
        export_btn = gr.Button("Export", variant="primary")
        download = gr.File(label="Download")
    
    # ========================================================================
    # Event Handlers
    # ========================================================================
    
    def process_file(file, thresh):
        try:
            df = state.load_file(file, thresh)
            preview_cols = ['episode_id', 'num_utterances', 'speakers']
            choices = state.get_episode_choices()
            return df[preview_cols].head(10), gr.Dropdown(choices=choices)
        except Exception as e:
            return gr.DataFrame(), gr.Dropdown(choices=[])
    
    process_btn.click(
        process_file,
        inputs=[file_input, threshold],
        outputs=[preview, episode_select]
    )
    
    def show_content(ep_id):
        return state.get_episode_content(ep_id)
    
    episode_select.change(
        show_content,
        inputs=[episode_select],
        outputs=[content]
    )
    
    def save_anno(ep_id, mc_type, note):
        return state.save_annotation(ep_id, mc_type, note)
    
    save_btn.click(
        save_anno,
        inputs=[episode_select, metacog_select, notes],
        outputs=[status]
    )
    
    def do_export():
        return state.export()
    
    export_btn.click(
        do_export,
        inputs=[],
        outputs=[download]
    )

if __name__ == "__main__":
    demo.launch()