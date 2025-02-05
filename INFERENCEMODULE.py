def run_llama_inference(model_name, malware_data, quantization=False):

    import json
    import torch
    import gc
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig  # For quantization
    import os
    import time
    # from huggingface_hub import login

    # import os
    os.environ["TOKENIZERS_PARALLELISM"] = "false"


    # Check for GPU availability
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    if quantization:

        # Enable 4-bit quantization for faster inference
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,  # Use 4-bit precision
            bnb_4bit_use_double_quant=True,  # Double quantization for improved performance
            bnb_4bit_compute_dtype=torch.float16  # Ensure FP16 precision for computation
        )

        

        # Load model with 4-bit precision and device mapping
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,  # Use the quantization config
            device_map="auto",  # Automatically map model to available GPUs
            torch_dtype=torch.float16  # Use FP16 for faster processing
        )

    else:
        print("No CUDA!!! Running on CPU...")
        # Load model with 4-bit precision and device mapping
        model = AutoModelForCausalLM.from_pretrained(
        model_name,
        # quantization_config=bnb_config,  # Use the quantization config
        device_map="auto",  # Automatically map model to available GPUs
        # torch_dtype=torch.float16  # Use FP16 for faster processing
        )  


    # Check if pad_token_id is set
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Validate malware_data
    if not isinstance(malware_data, str) or len(malware_data.strip()) == 0:
        raise ValueError("Input malware_data must be a non-empty string.")


    # Define the prompt
    prompt = f"""
    You are a cybersecurity expert tasked with analyzing the following malware report provided from the Cuckoo Sandbox.
    Use the JSON details below to provide only a summary paragraph discussing behavioral and network analysis, and functional intelligence.

    Cuckoo Sandbox JSON Details:
    {malware_data}

    ### Summary:
    """

    # print("Prompt:\n", prompt)
    # print("End\n")

    # # Tokenize prompt and truncate if necessary
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True).to(device)
    # print("Length of Tokenized Input: ", len(inputs.input_ids[0]))

    # Generate summary using the model
    outputs = model.generate(
        inputs.input_ids,
        max_new_tokens=256, 
        attention_mask=inputs.attention_mask,
        num_return_sequences=1,
        do_sample=True,  # Enable sampling for diversity
        temperature=0.7,  # Control randomness of generation
        top_k=50,  # Limit top-k tokens for consideration
        top_p=0.9,  # Nucleus sampling for balanced creativity
        pad_token_id=tokenizer.eos_token_id  # Explicitly set the pad_token_id
    )

    # Decode the generated text
    summary_temp = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # print("\n\nGenerated Text:\n", summary_temp)


    # def ensure_complete_sentences(text):
    #     import nltk
    #     nltk.download('punkt_tab')
    #     from nltk.tokenize import sent_tokenize
    #     sentences = sent_tokenize(text)
    #     return " ".join(sentences[:-1]) if not text.endswith(('.', '!', '?')) else text

    def ensure_complete_sentences(text):
        import nltk
        nltk.download('punkt_tab', quiet=True)
        from nltk.tokenize import sent_tokenize

        # Split the input text into paragraphs based on double newlines
        paragraphs = text.split("\n\n")
        processed_paragraphs = []

        for para in paragraphs:
            # Tokenize each paragraph into sentences
            sentences = sent_tokenize(para)
            # If the paragraph doesn't end with valid punctuation, drop the last sentence
            if not para.strip().endswith(('.', '!', '?')):
                sentences = sentences[:-1]
            # Recombine sentences back into a paragraph
            processed_paragraphs.append(" ".join(sentences))
        
        # Recombine paragraphs with double newlines
        return "\n\n".join(processed_paragraphs)


    summary_temp = ensure_complete_sentences(summary_temp)

    # Extract the summary section
    summary_temp = summary_temp.split("### Summary:")[-1].strip()
    # print("\n\nFinal Summary:\n", summary_temp)

    # Calculate total inference time
    # initial_end_time = time.time()
    # print("Total Inference Time: ", initial_end_time - initial_start_time)

    # Clean up memory
    gc.collect()
    torch.cuda.empty_cache()

    return summary_temp

def evaluate_summary(model_summary, human_summary):

    from sentence_transformers import SentenceTransformer, util
    from transformers import GPT2Tokenizer, GPT2LMHeadModel
    import evaluate
    from bert_score import score as bert_score
    import textstat
    from keybert import KeyBERT
    from gensim.models import KeyedVectors
    import pandas as pd

    # Initialize models and metrics
    sentence_model = SentenceTransformer('all-MiniLM-L6-v2')  # For cosine similarity
    keybert_model = KeyBERT()  # For keyphrase extraction
    rouge = evaluate.load("rouge")
    bleu = evaluate.load("bleu")

    # 1. ROUGE
    rouge_scores = rouge.compute(predictions=[model_summary], references=[human_summary])


    # 3. BERTScore
    precision, recall, f1 = bert_score([model_summary], [human_summary], model_type="bert-base-uncased")

    # 4. Cosine Similarity
    embeddings1 = sentence_model.encode(model_summary, convert_to_tensor=True)
    embeddings2 = sentence_model.encode(human_summary, convert_to_tensor=True)
    cosine_similarity = util.pytorch_cos_sim(embeddings1, embeddings2).item()

    # 5. Word Mover's Distance (WMD)
    # Load pre-trained word embeddings (if available locally, otherwise comment out)
    # word_vectors = KeyedVectors.load_word2vec_format("GoogleNews-vectors-negative300.bin", binary=True)
    # wmd_distance = word_vectors.wmdistance(model_summary.split(), human_summary.split())

    # 6. Flesch-Kincaid Readability Score
    readability = textstat.flesch_reading_ease(model_summary)

    # 7. Distinct-N
    def distinct_n_grams(text, n):
        tokens = text.split()
        ngrams = set(zip(*[tokens[i:] for i in range(n)]))
        return len(ngrams) / len(tokens)

    distinct_1 = distinct_n_grams(model_summary, 1)
    distinct_2 = distinct_n_grams(model_summary, 2)

    # 8. Keyphrase Matching
    human_keyphrases = keybert_model.extract_keywords(human_summary, keyphrase_ngram_range=(1, 2), stop_words='english')
    model_keyphrases = keybert_model.extract_keywords(model_summary, keyphrase_ngram_range=(1, 2), stop_words='english')
    human_keyphrases_set = set([kw[0] for kw in human_keyphrases])
    model_keyphrases_set = set([kw[0] for kw in model_keyphrases])
    keyphrase_overlap = len(human_keyphrases_set & model_keyphrases_set) / len(human_keyphrases_set) if human_keyphrases_set else 0

    # Compile Results
    results = {
        "ROUGE-1": rouge_scores["rouge1"],
        "ROUGE-2": rouge_scores["rouge2"],
        "ROUGE-L": rouge_scores["rougeL"],
        "BERTScore Precision": precision.mean().item(),
        "BERTScore Recall": recall.mean().item(),
        "BERTScore F1": f1.mean().item(),
        "Cosine Similarity": cosine_similarity,
        # Uncomment WMD if pre-trained embeddings are available
        # "WMD Distance": wmd_distance,  
        "Flesch-Kincaid Readability": readability,
        "Distinct-1": distinct_1,
        "Distinct-2": distinct_2,
        "Keyphrase Overlap": keyphrase_overlap,
    }
    return results
