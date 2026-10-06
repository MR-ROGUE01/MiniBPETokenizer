# ⚡ MiniBPETokenizer

<p align="center">
  <a href="https://minibpetokenizer-mr-rogue01.streamlit.app/">
    <img src="https://img.shields.io/badge/Live%20Demo-Streamlit%20Cloud-FF4B4B?style=for-the-badge&logo=streamlit" alt="Live Demo" />
  </a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Algorithm-Byte--Level%20BPE-7928CA?style=for-the-badge" alt="Algorithm" />
  <img src="https://img.shields.io/badge/Vocab%20Size-10%2C000-10B981?style=for-the-badge" alt="Vocab Size" />
  <img src="https://img.shields.io/badge/Author-Raj%20Kumar%20Gupta-F59E0B?style=for-the-badge" alt="Author" />
</p>

<p align="center">
  <strong>A Byte-Level Byte Pair Encoding (BPE) Tokenizer built from scratch in pure Python.</strong><br>
  Trained on technical text, mathematics, and code, paired with a real-time <strong>Tiktokenizer-style visualizer</strong>.
</p>

<p align="center">
  🚀 <strong><a href="https://minibpetokenizer-mr-rogue01.streamlit.app/">Try the Live Web App Here</a></strong> 🚀
</p>

---

## 🌟 Overview

Before an LLM processes text, it splits sentences into numerical tokens. While production models rely on large C/Rust libraries (like HuggingFace Tokenizers or Tiktoken), **MiniBPETokenizer** was built from first principles in Python to understand how tokenization works under the hood:

- **Zero Tokenizer Dependencies:** Pure Python implementation of BPE merge training, pair statistics, and greedy inference encoding.
- **GPT-2 Pre-tokenization:** Uses regex to prevent merges across whitespace, punctuation, and contractions (`'s`, `'t`, `'re`, etc.).
- **10,000 Vocabulary:** 256 base UTF-8 bytes + 9,744 learned merges saved as portable JSON and Pickle artifacts.
- **Interactive Visualizer:** Real-time web visualizer modeled after Tiktokenizer with pastel token badges, middle dots (`·`) for whitespace, `\n` indicators, and hover tooltips for Token IDs.

---

## 📊 Training Corpus & Domain Coverage

Trained on **~18,900 lines** (~866,000 characters) of curated data:

| Domain | Content Details |
| :--- | :--- |
| **English Natural Language** | Technical explanations, conversational prose, contractions, and common vocabulary. |
| **Mathematics & Calculus** | Derivatives ($f'(x)$), integrals, exponents, and Greek variables ($\alpha, \beta, \omega, \nabla, \Sigma$). |
| **Code Syntax** | Python functions, loops (`for`, `range()`), keywords, and SQL queries (`SELECT`, `WHERE`, `JOIN`). |
| **Byte-Level UTF-8** | Base 256 byte vocabulary ensures zero Out-of-Vocabulary (OOV) crashes for any Unicode text. |

---

## 🛠️ Quick Usage in Python

You can load and use the trained tokenizer directly in your own code or notebook:

```python
# Option 1: Direct import (recommended)
from app import model as tokenizer

text = "Hello world! Building GPT from scratch."
token_ids = tokenizer.encode(text)
print("Token IDs:", token_ids)

token_pieces = tokenizer.get_tokens(token_ids)
print("Tokens:", token_pieces)
```

Or load directly from `tokenizer.pkl`:

```python
# Option 2: Using pickle
import pickle
from app import CustomTokenizer

with open("tokenizer.pkl", "rb") as f:
    tokenizer = pickle.load(f)

token_ids = tokenizer.encode("Hello world!")
print(tokenizer.get_tokens(token_ids))
```

---

## 📁 Repository Structure

```
MiniBPETokenizer/
├── app.py                         # Streamlit Web App with live visualizer
├── tokenizer.pkl                  # Serialized trained CustomTokenizer model
├── requirements.txt               # App dependencies
├── custom_tokenizer (1).ipynb     # Jupyter Notebook with full scratch training code
├── tokenizer_training_corpus.txt  # Training dataset (~18.9k lines)
└── my_tokenizer/                  # Exported JSON artifacts
    ├── config.json                # Model config and metadata
    ├── merges.json                # 9,744 learned BPE merge rules
    └── vocab.json                 # 10,000 base64-encoded byte token mappings
```

---

## 🚀 Running the App Locally

### 1. Clone the Repository
```bash
git clone https://github.com/MR-ROGUE01/MiniBPETokenizer.git
cd MiniBPETokenizer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Streamlit
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 👨‍💻 Author

**Raj Kumar Gupta**  
GitHub: [@MR-ROGUE01](https://github.com/MR-ROGUE01)  
Live Demo: [minibpetokenizer-mr-rogue01.streamlit.app](https://minibpetokenizer-mr-rogue01.streamlit.app/)

---

## 📜 License

This project is licensed under the MIT License. Feel free to use and reference it for learning and research!
