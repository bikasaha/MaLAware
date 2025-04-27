<p align="center">
<img src="fig/MALWARE_LOGO.png" alt="MaLAware Logo" width="700" height="300">
</p>

**MaLAware** is a tool designed to analyze and explain the behavior of malware using advanced large language models (LLMs). It leverages state-of-the-art language models to generate comprehensive, actionable, and human-readable explanations of malicious software behavior. This tool aims to assist cybersecurity analysts in understanding and interpreting complex malware actions.

---
## Features
---
- Generates detailed explanations of malware behavior.
- Provides actionable insights for cybersecurity professionals.
- Uses multiple large language models (LLMs) for performance comparison.
- Supports 4-bit quantization for faster inference with lower resource usage.
---
## Project Structure
```
MaLAware/
├── Data/
│   ├── GROUND_TRUTH/    # Ground truth of the prepared dataset
│   │   ├── 1nj..vd.json # Ground truth of 1nj..vd malware
│   │   ├── rgj..ol.json # Ground truth of rgj..ol malware
│   │   └── wfj..vd.json # Ground truth of wfj..vd malware
│   │
│   ├── SANDBOX_REPORT/  # Input sandbox report
│   │   ├── 17j..vd.json # Sandbox report of 17j..vd malware
│   │   ├── plj..sd.json # Sandbox report of plj..sd malware
│   │   ├── hsy..er.json # Sandbox report of hsy..er malware
│   │   └── 4bc..9i.json # Sandbox report of 4bc..9i malware
│   │
└── fig/                 # Figures
│   └── MALWARE_LOGO.png # MaLAware logo image
│ 
├── Dockerfile           # Dockerfile to run using docker
├── FILTER.py            # Pre-processing module
├── INFERENCEMODULE.py   # Inference module
├── LICENSE              # License of the project
├── MALAWARE.py          # Main script to run the project
├── README.md            # ReadMe file
├── requirement.txt      # Requirement file
└── test.json            # Test input file (This is provided as a sample. The sandbox reports can be found in the DATASET/SANDBOX_REPORT/ directory)

```
---
## Installation

### Prerequisites

Before using **MaLAware**, ensure that you have the following installed:

- Python 3.8
- `pip` (Python package installer)
- Required libraries (listed below)


### **Note**:
To ensure smooth performance, please make sure of the following:

- **CUDA Support**: For faster inference with GPU, **CUDA-enabled GPUs** are recommended. Ensure that the appropriate **NVIDIA drivers** and **CUDA toolkit** are installed for your GPU, with at least 15 GB of RAM (for quantized models). This will accelerate the execution of models that utilize GPU processing. This is also needed when using quantization feature.
- RAM usage may increase in certain cases, such as with large JSON files, increased context length, and similar scenarios.

---

## Usage

This repository provides two different ways to use the **MaLAware** tool: 

- directly using a Python script.
- via Docker

Instructions for using the tool through each of these methods are explained in this section.


### Available Models

**MaLAware** supports the following models:

- Qwen/Qwen2.5-7B-Instruct
- meta-llama/Llama-2-7b-hf
- meta-llama/Llama-3.1-8B-Instruct
- mistralai/Mistral-7B-Instruct-v0.3
- tiiuae/falcon-7b

You can choose the model that best suits your needs based on the task at hand.

**Note:** Ensure you have your Hugging Face token for access to gated repositories.

---

## Running MaLAware using python script

#### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/bikasaha/MaLAware.git
   cd MaLAware
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   conda create -n malware python=3.8 -y
   conda activate malware
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

To run **MaLAware**, use the following command:

```bash
python MALAWARE.py --i <path_to_input_json_file> --m <model_name> --q --hf <hugging_face_token>
```

- **`--i`** argument: The path to the raw input JSON file is now mentioned as required.
- **`--m`** argument: Specifies the model name with a default value (`meta-llama/Llama-3.1-8B-Instruct`).
- **`--q`** argument: Optional flag for enabling 4-bit quantization for faster inference. (CUDA support needed)
- **`--hf`** argument: Hugging Face authentication token is required.

Example:

```bash
python MALAWARE.py --i /path/to/input.json --m meta-llama/Llama-3.1-8B-Instruct --q --hf <your_hugging_face_token>
```

### Generating Explanations

Once the malware sample is processed, **MaLAware** will generate a detailed explanation of the detected malicious behavior. This explanation will include insights into the potential actions of the malware, what behavior is considered suspicious, and possible mitigations.

Example output:

```
- <b>Behavioral Analysis:</b> The malware allocates memory segments multiple times using `NtAllocateVirtualMemory`, which is common in many types of malware to execute code in memory. It also creates and deletes files, and writes to the registry, indicating that it attempts to persist and modify system settings. The malware also repeatedly searches for specific processes (`mobsync.exe`), which could be an attempt to avoid detection by hiding behind legitimate processes. Additionally, the malware makes multiple attempts to communicate over UDP with multicast addresses, suggesting it might be part of a botnet or attempting to join one.
- <b>Network Analysis:</b> The malware sends numerous UDP packets to broadcast addresses such as `192.168.56.255` and multicast addresses like `224.0.0.252`. These communications could be used for command-and-control purposes or for spreading to other hosts within the local network. The variety of ports used (137, 138, 5355) indicates that the malware is probing for open services on the network.
- <b>Functional Intelligence:</b> The malware is designed to create and delete files, especially those related to temporary and system folders.

```

### Example Output

After processing a sample, the output will be displayed under the heading **`Generated Summary:`**, providing a comprehensive explanation of the malware's actions and highlighting key behaviors.

---

## Running MaLAware via Docker


#### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/bikasaha/MaLAware.git
   cd MaLAware
   ```
2. Ensure you have docker installed and running
3. Run `docker build -t malaware .` command
4. Run command:

    ```bash
    docker run --rm -v $(pwd):/app/data malaware --i /app/data/</path/to/input.json> --m meta-llama/Llama-3.1-8B-Instruct --q --hf <your_hugging_face_token>
    ```
- **`--i`** argument: The path to the raw input JSON file is now mentioned as required.
- **`--m`** argument: Specifies the model name with a default value (`meta-llama/Llama-3.1-8B-Instruct`).
- **`--q`** argument: Optional flag for enabling 4-bit quantization for faster inference. (CUDA support needed)
- **`--hf`** argument: Hugging Face authentication token is required.

---

## 📢 Contribute & Collaborate  
We welcome contributions! Feel free to:  

- 📌 Report issues in the **[Issues tab](../../issues)**  
- 🚀 Submit enhancements via **[Pull Requests](../../pulls)**  

---

## 📜 License  
This project is licensed under the **Apache 2.0 License**.  

---

### Note: This tool has been accepted in the Dataset Tool Track at the [MSR 2025 conference](https://2025.msrconf.org/). The published paper details will be updated on the tool's GitHub repository after publication, available at: [MaLAware](https://github.com/bikasaha/MaLAware) . If you use this tool in any capacity, please provide a citation. 

### The paper is available on arXiv at: https://arxiv.org/abs/2504.01145

---
## Contact

For any questions or issues, please open an issue on the GitHub repository or contact us at [bikash@cse.iitk.ac.in] or [nandarani@cse.iitk.ac.in].

---
