#!/usr/bin/env python3

import argparse
import json
from INFERENCEMODULE import run_llama_inference
from FILTER import parse_cuckoo_json
from huggingface_hub import login

import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning)




def main():
    parser = argparse.ArgumentParser(description="Real-Time Malware Report Inference Tool")
    parser.add_argument("--i", type=str, required=True, help="Path to the raw input JSON file")
    # parser.add_argument("--output", type=str, required=True, help="Path to the output TXT file")
    parser.add_argument("--m", type=str, default="meta-llama/Llama-3.1-8B-Instruct",
                        help="Specify the Hugging Face model name to use for inference")
    parser.add_argument("--q", action="store_true", help="Enable 4-bit quantization for faster inference")
    parser.add_argument("--hf", type=str, required=True, help="Hugging Face authentication token")
    args = parser.parse_args()

    try:
        # Step 1: Authenticate with Hugging Face
        from huggingface_hub import login
        print("Authenticating with Hugging Face...")
        login(args.hf)

        # Step 2: Filter the raw JSON input
        print(f"Pre-processing the raw input JSON: {args.i}")
        filtered_data = parse_cuckoo_json(args.i)
        # print("Filtering complete.")

        # Step 3: Convert filtered data to a string for inference
        malware_data_str = json.dumps(filtered_data)

        # Step 4: Run LLaMA inference
        print(f"Running inference using model {args.m}...")
        summary = run_llama_inference(args.m, malware_data_str, quantization=args.q)

        print(f"\nGenerated Summary:\n{summary}")

        # Step 5: Save the summary to the output file
        # with open(args.output, "w") as f:
        #     f.write(summary)

        # print(f"Inference complete! Summary saved to {args.output}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
