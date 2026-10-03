# ⚡ MiniBPETokenizer

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python Version" />
  <img src="https://img.shields.io/badge/Streamlit-App-FF4B4B?style=for-the-badge&logo=streamlit" alt="Streamlit" />
  <img src="https://img.shields.io/badge/Algorithm-Byte--Level%20BPE-purple?style=for-the-badge" alt="Algorithm" />
  <img src="https://img.shields.io/badge/Vocab%20Size-10%2C000-green?style=for-the-badge" alt="Vocab Size" />
  <img src="https://img.shields.io/badge/Author-Raj%20Kumar%20Gupta-orange?style=for-the-badge" alt="Author" />
</p>

A custom **Byte-Level Byte Pair Encoding (BPE) Tokenizer** built completely from scratch in Python, inspired by **GPT-2 pre-tokenization** and Andrej Karpathy's `minbpe`. Features a high-performance interactive web visualizer modeled after **Tiktokenizer**.

---

## 🌟 Key Features

- **Built from Scratch:** Pure Python implementation of the BPE merge algorithm, frequency statistics counting, and vocabulary building.
- **GPT-2 Style Pre-Tokenization:** Regex-based pre-tokenization splitting punctuation, alphanumeric words, contractions (`'s`, `'ll`, etc.), and whitespace.
- **10,000 Token Vocabulary:** 256 base UTF-8 byte tokens + 9,744 learned iterative merges saved as serialized artifacts.
- **⚡ Instant Real-Time Typing:** Custom Streamlit Component v2 input with debounced keystrokes — updates tokens live without needing `Ctrl+Enter` or clicking away.
- **🎨 Tiktokenizer-Style Visualizer:**
  - Distinct pastel token badges that sit flush against each other.
  - Middle dots (`·`) for space characters.
  - Explicit `\n` indicators for linebreaks.
  - Safe hexadecimal byte representation (`<0x..>`) for out-of-vocabulary UTF-8 fallback.
  - Real-time token count and comma-separated token ID sequences.

---

## 📊 Training Corpus & Domain Specialization

The tokenizer was trained on **~18,900 lines** (~866,000 characters) of curated technical and domain-specific text:

| Domain | Content Description |
| :--- | :--- |
| **English Natural Language** | Dialogues, questions & answers, academic prose, contractions, and conversational sentences. |
| **Mathematics & Calculus** | Derivatives, differential equations, powers ($x^n$, $\omega^2$), and Greek letters ($\alpha, \beta, \omega, \nabla, \Sigma$). |
| **Operators & Arithmetic** | Arithmetic expressions ($+$, $-$, $\times$, $\div$, $=$, $\neq$, $\le$, $\ge$, $\pm$). |
| **Code & Databases** | Python functions, loops (`for`, `range()`), SQL database queries (`SELECT`, `WHERE`, `JOIN`). |

> *Note: Scripts outside the Latin alphabet (such as Devanagari/Hindi) decompose into individual UTF-8 byte tokens.*

---

## 📁 Project Structure

```
MiniBPETokenizer/
├── app.py                         # Streamlit Web App with live visualizer
├── tokenizer.pkl                  # Serialized trained tokenizer model
├── requirements.txt               # Dependencies for local and cloud deployment
├── custom_tokenizer (1).ipynb     # Jupyter Notebook containing scratch training logic
├── tokenizer_training_corpus.txt  # Training dataset (~18.9k lines)
└── my_tokenizer/                  # Saved JSON tokenizer artifacts
    ├── config.json                # Metadata (vocab size, merges, encoding)
    ├── merges.json                # 9,744 learned BPE merge rules
    └── vocab.json                 # 10,000 base64-encoded byte token mappings
```

---

## 🚀 Getting Started Locally

### 1. Clone the Repository
```bash
git clone https://github.com/MR-ROGUE01/MiniBPETokenizer.git
cd MiniBPETokenizer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit App
```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`.

---

## 🧠 How the BPE Algorithm Works

1. **Pre-tokenization:** Input text is broken into sub-chunks using the GPT-2 regex pattern:
   ```python
   pat = re.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""")
   ```
2. **Byte Conversion:** Text chunks are converted into raw UTF-8 byte sequences ($0 \dots 255$).
3. **Iterative Merging:** In each iteration, the most frequent consecutive pair $(p_0, p_1)$ across the corpus is merged into a new token ID ($256 \dots 9999$).
4. **Encoding:** At inference time, unknown text is converted to bytes and greedily compressed using the priority order of learned merges.

---

## 👨‍💻 Author

**Raj Kumar Gupta**  
GitHub: [@MR-ROGUE01](https://github.com/MR-ROGUE01)

---

## 📜 License

Distributed under the MIT License. Feel free to use and adapt this project for educational and research purposes.
