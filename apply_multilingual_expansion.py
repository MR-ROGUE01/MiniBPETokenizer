import base64
import json
import os
import pickle
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 1. Load original tokenizer
base_dir = r"c:\Users\ACER\Downloads\Build_GPT"
with open(os.path.join(base_dir, "my_tokenizer", "merges.json"), "r", encoding="utf-8") as f:
    orig_merge_data = json.load(f)
merges = {(p0, p1): idx for p0, p1, idx in orig_merge_data}

with open(os.path.join(base_dir, "my_tokenizer", "vocab.json"), "r", encoding="utf-8") as f:
    orig_vocab_data = json.load(f)
vocab = {int(idx): base64.b64decode(tb) for idx, tb in orig_vocab_data.items()}

# Reset to strictly original 10,000 vocab if previously expanded
orig_vocab_items = {k: v for k, v in vocab.items() if k < 10000}
orig_merges_items = {k: v for k, v in merges.items() if v < 10000}
vocab = orig_vocab_items
merges = orig_merges_items

print(f"Base tokenizer loaded: {len(vocab)} vocab tokens, {len(merges)} merges.")

next_id = [10000]


def register_single_char(ch, merges, vocab, next_id):
    """Registers an atomic UTF-8 character (1-4 bytes) so it always decodes cleanly."""
    b = ch.encode("utf-8")
    cur = list(b)
    while len(cur) >= 2:
        pair = (cur[0], cur[1])
        if pair not in merges:
            idx = next_id[0]
            next_id[0] += 1
            merges[pair] = idx
            vocab[idx] = vocab[pair[0]] + vocab[pair[1]]
        else:
            idx = merges[pair]
        cur = [idx] + cur[2:]
    return cur[0]


def register_full_string(s, merges, vocab, next_id):
    """Registers a multi-character word on top of atomic characters."""
    char_tokens = [register_single_char(c, merges, vocab, next_id) for c in s]
    cur = list(char_tokens)
    while len(cur) >= 2:
        pair = (cur[0], cur[1])
        if pair not in merges:
            idx = next_id[0]
            next_id[0] += 1
            merges[pair] = idx
            vocab[idx] = vocab[pair[0]] + vocab[pair[1]]
        else:
            idx = merges[pair]
        cur = [idx] + cur[2:]
    return cur[0] if cur else None


# ==========================================
# 2. ALL DEVANAGARI CHARACTERS (0x0900 - 0x097F)
# ==========================================
print("Registering all Devanagari characters, matras, and digits...")
for codepoint in range(0x0900, 0x097F):
    try:
        ch = chr(codepoint)
        register_single_char(ch, merges, vocab, next_id)
        register_full_string(" " + ch, merges, vocab, next_id)
    except Exception:
        pass

# ==========================================
# 3. POPULAR HINDI WORDS
# ==========================================
print("Registering common Hindi words...")
hindi_words = [
    "नमस्ते", "भारत", "राज", "धन्यवाद", "स्वागत", "दोस्त", "भाई",
    "है", "हैं", "था", "थी", "थे", "हूँ", "हो", "गा", "गी", "गे",
    "का", "की", "के", "को", "से", "में", "पर", "ने", "और", "या",
    "यह", "वह", "ये", "वे", "इस", "उस", "इन", "उन", "कि", "जो",
    "आप", "हम", "तुम", "मैं", "मेरा", "मेरी", "मेरे", "तुम्हारा",
    "क्या", "क्यों", "कैसे", "कहाँ", "कब", "कितना", "कौन",
    "अच्छा", "बढ़िया", "मस्त", "शानदार", "खुशी", "प्यार", "शांति",
    "जिंदगी", "समय", "काम", "दिन", "रात", "बात", "नाम", "देश",
    "भाषा", "ज्ञान", "विज्ञान", "तकनीक", "शिक्षा", "पुस्तक",
    "आर्टिफिशियल", "इंटेलिजेंस", "मशीन", "लर्निंग", "मॉडल", "टोकन"
]

for w in hindi_words:
    register_full_string(w, merges, vocab, next_id)
    register_full_string(" " + w, merges, vocab, next_id)

# ==========================================
# 4. POPULAR EMOJIS
# ==========================================
print("Registering popular emojis...")
emojis = [
    "🚀", "⚡", "🔥", "✨", "❤️", "🤖", "👍", "😂", "🎉", "💡",
    "💯", "🎯", "🌟", "💻", "🧠", "📈", "✅", "🇮🇳", "👏", "🙌",
    "🐍", "☕", "📊", "🏆", "🌍", "🔒", "🛠️", "🎨", "⭐", "💪",
    "🙏", "👀", "🥳", "😎", "🤩", "👌"
]

for em in emojis:
    register_single_char(em, merges, vocab, next_id)
    register_full_string(" " + em, merges, vocab, next_id)

# Combined common emoji pairs
register_full_string("🚀⚡🔥", merges, vocab, next_id)
register_full_string("🤖✨", merges, vocab, next_id)

# ==========================================
# 5. EXTENDED MATH & LOGIC SYMBOLS
# ==========================================
print("Registering math and scientific symbols...")
math_symbols = [
    "∫", "∂", "∇", "∞", "≈", "≠", "≤", "≥", "±", "×", "÷", "√",
    "∈", "∉", "⊂", "⊆", "∪", "∩", "→", "←", "↔", "⇒", "⇔",
    "∀", "∃", "∑", "∏",
    "α", "β", "γ", "δ", "ε", "ζ", "η", "θ", "ι", "κ", "λ", "μ",
    "ν", "ξ", "π", "ρ", "σ", "τ", "υ", "φ", "χ", "ψ", "ω",
    "Γ", "Δ", "Θ", "Λ", "Ξ", "Π", "Σ", "Φ", "Ψ", "Ω"
]

for ms in math_symbols:
    register_single_char(ms, merges, vocab, next_id)
    register_full_string(" " + ms, merges, vocab, next_id)

# ==========================================
# 6. HINGLISH SLANG & DEV TERMS
# ==========================================
print("Registering Hinglish and web terms...")
hinglish_words = [
    "bhai", "yaar", "kya", "chal", "raha", "hai", "theek", "mast",
    "shukriya", "badiya", "dost", "kaise", "kaisa", "kuch", "nahi",
    "acha", "bahut", "sahi", "aisa", "waisa", "sab", "kar", "karo",
    "tokenizer", "bpe", "vocab", "embed", "tensor", "dataset", "train",
    "<div>", "</div>", "<span>", "</span>", "useState", "useEffect"
]

for hw in hinglish_words:
    register_full_string(hw, merges, vocab, next_id)
    register_full_string(" " + hw, merges, vocab, next_id)

final_vocab_size = len(vocab)
final_merges_count = len(merges)
print("\n" + "=" * 55)
print(f"🎉 SUCCESS! Total vocabulary: {final_vocab_size:,} tokens.")
print(f"Total merges: {final_merges_count:,} (added {final_merges_count - len(orig_merges_items)} clean merges).")
print("=" * 55)

# ==========================================
# 7. SAVE TO my_tokenizer AND tokenizer.pkl
# ==========================================
print("Saving updated merges.json and vocab.json...")
merge_data = [[p0, p1, idx] for (p0, p1), idx in merges.items()]
with open(os.path.join(base_dir, "my_tokenizer", "merges.json"), "w", encoding="utf-8") as f:
    json.dump(merge_data, f, indent=2)

vocab_data = {
    str(idx): base64.b64encode(tb).decode("ascii")
    for idx, tb in vocab.items()
}
with open(os.path.join(base_dir, "my_tokenizer", "vocab.json"), "w", encoding="utf-8") as f:
    json.dump(vocab_data, f, indent=2)

config = {
    "tokenizer_type": "ByteLevelBPE",
    "vocab_size": final_vocab_size,
    "base_vocab_size": 256,
    "num_merges": final_merges_count,
    "languages": ["English", "Hindi/Devanagari (हिन्दी)", "Hinglish", "Emojis", "Mathematics", "Code"]
}
with open(os.path.join(base_dir, "my_tokenizer", "config.json"), "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2)

import regex as re
class CustomTokenizer:
    def __init__(self, merges, vocab):
        self.merges = merges
        self.vocab = vocab
        self.pat = re.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""")

    def encode(self, text):
        chunks = re.findall(self.pat, text)
        tokens = [b for c in chunks for b in c.encode("utf-8")]
        while len(tokens) >= 2:
            stats = {p: 0 for p in zip(tokens, tokens[1:])}
            for p in zip(tokens, tokens[1:]): stats[p] += 1
            pair = min(stats, key=lambda p: self.merges.get(p, float("inf")))
            if pair not in self.merges: break
            idx = self.merges[pair]
            newids, i = [], 0
            while i < len(tokens):
                if i < len(tokens) - 1 and (tokens[i], tokens[i+1]) == pair:
                    newids.append(idx); i += 2
                else:
                    newids.append(tokens[i]); i += 1
            tokens = newids
        return tokens

    def get_tokens(self, ids):
        pieces = []
        for i in ids:
            raw = self.vocab[i]
            try:
                pieces.append(raw.decode("utf-8"))
            except UnicodeDecodeError:
                pieces.append("".join(f"<0x{b:02X}>" for b in raw))
        return pieces

print("Saving updated tokenizer.pkl...")
with open(os.path.join(base_dir, "tokenizer.pkl"), "wb") as f:
    pickle.dump(CustomTokenizer(merges, vocab), f)

print("Saved tokenizer.pkl successfully!")

# Verify
test_tok = CustomTokenizer(merges, vocab)
test_cases = [
    "नमस्ते भारत! मेरा नाम राज है 🚀⚡🔥",
    "भारत एक महान देश है। धन्यवाद!",
    "Hello World! This is custom BPE.",
    "f'(x) = 2x + ∫ f(t) dt and ∞",
    "bhai kya haal chaal hai"
]

print("\n--- FINAL TEST SUITE ---")
for tc in test_cases:
    ids = test_tok.encode(tc)
    pieces = test_tok.get_tokens(ids)
    print(f"\nInput: {tc}")
    print(f"Token count: {len(ids)}")
    print(f"Tokens: {pieces}")
