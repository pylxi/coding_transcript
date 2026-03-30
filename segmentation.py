from transformers import AutoTokenizer, AutoModelForTokenClassification
import torch

def segment_with_bert(utterances, model_name="bert-base-uncased", device="cpu"):
    """
    Segment dialogue utterances using BERT token classification.
    
    How it works:
    1. BERT tokenizes each utterance into subword tokens
    2. The model processes tokens through transformer layers to understand context
    3. Each token gets a classification label (e.g., BEGINNING, CONTINUATION, TOPIC_CHANGE)
    4. We extract boundaries where topic/segment changes occur
    
    Args:
        utterances: List of strings (dialogue turns)
        model_name: Pretrained model name
        device: 'cpu' or 'cuda'
    
    Returns:
        Dictionary with segment boundaries and labels
    """
    # Load tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForTokenClassification.from_pretrained(model_name).to(device)
    model.eval()
    
    segments = []
    
    with torch.no_grad():
        for utterance in utterances:
            # Step 1: Tokenize the text
            # BERT breaks text into subword tokens (e.g., "unbelievable" → ["un", "##be", "##lievable"])
            encoded = tokenizer(
                utterance,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=512
            ).to(device)
            
            # Step 2: Forward pass through BERT
            # BERT processes tokens through 12 layers (for base model) of transformers
            # Each layer learns increasingly abstract features about the text
            outputs = model(**encoded)
            logits = outputs.logits  # Shape: [batch_size, sequence_length, num_labels]
            
            # Step 3: Get predictions by finding the label with highest confidence
            predictions = torch.argmax(logits, dim=2)[0].cpu().numpy()
            
            # Step 4: Decode tokens back to text with their predicted labels
            tokens = tokenizer.convert_ids_to_tokens(encoded["input_ids"][0])
            
            # Step 5: Identify segment boundaries (where predictions change)
            segment_info = {
                "text": utterance,
                "tokens": tokens,
                "predictions": predictions.tolist(),
                "confidence": torch.softmax(logits, dim=2)[0].max(dim=1)[0].cpu().numpy().tolist()
            }
            segments.append(segment_info)
    
    return {
        "segments": segments,
        "boundaries": identify_boundaries(segments)
    }


def identify_boundaries(segments):
    """
    Extract segment boundaries where the predicted label changes
    """
    boundaries = []
    prev_label = None
    
    for idx, segment in enumerate(segments):
        predictions = segment["predictions"]
        
        for token_idx, label in enumerate(predictions):
            # Skip special tokens [CLS], [SEP], [PAD]
            if segment["tokens"][token_idx] in ["[CLS]", "[SEP]", "[PAD]"]:
                continue
            
            if label != prev_label and prev_label is not None:
                boundaries.append({
                    "position": idx,
                    "previous_label": prev_label,
                    "new_label": label,
                    "token": segment["tokens"][token_idx]
                })
            
            prev_label = label
    
    return boundaries