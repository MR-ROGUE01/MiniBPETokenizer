import html
import pickle
import logging
import warnings
import regex as re
from functools import lru_cache
import streamlit as st

# Silence Windows asyncio socket reset messages and component re-registration logs
logging.getLogger("asyncio").setLevel(logging.CRITICAL)
logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)
logging.getLogger("streamlit.components.v2").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")


# =========================================================
# 1. MODEL CLASS & SAFE UNPICKLER
# =========================================================
class CustomTokenizer:
    def __init__(self, merges, vocab):
        self.merges = merges
        self.vocab = vocab
        self.pat = re.compile(
            r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+"""
        )

    def encode(self, text):
        chunks = re.findall(self.pat, text)
        tokens = [b for c in chunks for b in c.encode("utf-8")]
        if len(tokens) < 2:
            return tokens

        merges = self.merges
        while len(tokens) >= 2:
            min_rank = float("inf")
            best_pair = None
            for i in range(len(tokens) - 1):
                pair = (tokens[i], tokens[i + 1])
                rank = merges.get(pair)
                if rank is not None and rank < min_rank:
                    min_rank = rank
                    best_pair = pair
                    if rank == 256:  # 256 is the absolute lowest merge rank
                        break

            if best_pair is None:
                break

            idx = merges[best_pair]
            p0, p1 = best_pair
            newids = []
            i = 0
            n = len(tokens)
            while i < n:
                if i < n - 1 and tokens[i] == p0 and tokens[i + 1] == p1:
                    newids.append(idx)
                    i += 2
                else:
                    newids.append(tokens[i])
                    i += 1
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


class SafeUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if name == "CustomTokenizer":
            return CustomTokenizer
        return super().find_class(module, name)


@st.cache_resource
def load_model():
    with open("tokenizer.pkl", "rb") as f:
        return SafeUnpickler(f).load()


model = load_model()

# =========================================================
# 2. BADA REAL-TIME TEXTAREA (STREAMLIT COMPONENT V2 - CACHED)
# =========================================================
_HTML = """
<div class="live-root" id="root">
  <textarea id="input" class="live-input" spellcheck="false"></textarea>
</div>
"""

_CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
.live-root {
  width: 100%;
}
.live-input {
  width: 100%;
  height: 420px;
  min-height: 400px;
  padding: 16px 18px;
  font-family: Consolas, 'Courier New', monospace;
  font-size: 15px;
  line-height: 1.6;
  color: var(--st-text-color, #f1f5f9);
  background-color: var(--st-secondary-background-color, #1e293b);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  outline: none;
  resize: vertical;
}
.live-input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25);
}
"""

_JS = r"""
export default function({ parentElement, data, setStateValue }) {
  const input = parentElement.querySelector("#input");
  input.placeholder = data.placeholder ?? "";

  // Set initial value only once on mount to prevent infinite re-render loops
  if (!parentElement._initialized) {
    input.value = data.value ?? "";
    parentElement._initialized = true;
  }

  parentElement._debounce = data.debounce ?? 450;

  if (!parentElement._attached) {
    let timer = null;
    let lastSent = input.value;

    const triggerUpdate = () => {
      clearTimeout(timer);
      const delay = parentElement._debounce;
      timer = setTimeout(() => {
        if (input.value !== lastSent) {
          lastSent = input.value;
          setStateValue("value", input.value);
        }
      }, delay);
    };

    input.addEventListener("input", triggerUpdate);
    input.addEventListener("paste", () => {
      setTimeout(triggerUpdate, 30);
    });
    parentElement._attached = true;
  }
}
"""

@st.cache_resource
def get_live_textarea_component():
    return st.components.v2.component(
        "live_textarea_component",
        html=_HTML,
        css=_CSS,
        js=_JS,
        isolate_styles=True,
    )


_live_textarea_component = get_live_textarea_component()


def live_textarea(value="", placeholder="", debounce=450, key="live_textarea_widget"):
    internal_key = f"_comp_{key}"
    state = st.session_state.get(internal_key, {})
    current_value = state.get("value", value) if isinstance(state, dict) else value

    def _sync():
        curr = st.session_state.get(internal_key, {})
        if isinstance(curr, dict) and "value" in curr:
            st.session_state[key] = curr["value"]

    result = _live_textarea_component(
        data={
            "value": value,
            "placeholder": placeholder,
            "debounce": debounce,
        },
        default={"value": value},
        key=internal_key,
        on_value_change=_sync,
    )
    val = getattr(result, "value", None) if hasattr(result, "value") else (result.get("value") if isinstance(result, dict) else None)
    live = val if val is not None else current_value
    st.session_state[key] = live
    return live


@lru_cache(maxsize=4096)
def get_tokens_cached(text):
    ids = model.encode(text)
    pieces = model.get_tokens(ids)
    return ids, pieces


# =========================================================
# 3. TIKTOKENIZER TOKEN VISUALIZER (· for space, \n)
# =========================================================
TOKEN_COLORS = [
    "#BAE6FD",  # Sky Blue
    "#FDE68A",  # Pastel Yellow
    "#A7F3D0",  # Mint Green
    "#FECDD3",  # Soft Rose
    "#DDD6FE",  # Lavender Purple
    "#FED7AA",  # Peach Orange
    "#E9D5FF",  # Soft Violet
    "#CCFBF1",  # Light Teal
]


def render_tiktokenizer_view(tokens_with_ids):
    if not tokens_with_ids:
        return "<div style='color: #94a3b8; font-style: italic; padding: 16px;'>Start typing on the left to see tokens!</div>"

    spans = []
    # Cap DOM rendering at first 1,200 tokens to keep browser buttery smooth
    render_tokens = tokens_with_ids[:1200]
    for i, (tid, piece) in enumerate(render_tokens):
        safe_piece = html.escape(piece)
        safe_piece = safe_piece.replace(" ", "·")
        
        if "\n" in safe_piece:
            parts = safe_piece.split("\n")
            inner_text = r"\n<br>".join(parts)
        else:
            inner_text = safe_piece

        # Properly escape tooltip with quotes to prevent HTML tag breaking
        safe_tooltip = html.escape(f"Token ID: {tid} | Value: {repr(piece)}", quote=True)
        spans.append(f'<span class="tok-chip tok-c{i % 8}" title="{safe_tooltip}">{inner_text}</span>')

    trunc_msg = ""
    if len(tokens_with_ids) > 1200:
        trunc_msg = f"<div style='margin-top: 10px; font-size: 13px; color: #64748b; font-style: italic;'>... showing first 1,200 of {len(tokens_with_ids):,} tokens for optimal rendering speed</div>"

    return f"<div class='visualizer-box'>{''.join(spans)}{trunc_msg}</div>"


# =========================================================
# 4. STREAMLIT CONFIG & PROFESSIONAL MODERN THEME
# =========================================================
st.set_page_config(
    page_title="MiniBPETokenizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        /* Proper top padding so navbar never cuts off the title */
        .block-container {
            padding-top: 3.5rem !important;
            padding-bottom: 2.5rem !important;
            max-width: 1400px !important;
        }
        .main-title {
            font-size: 34px;
            font-weight: 800;
            color: var(--st-text-color, #ffffff);
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 12px;
            letter-spacing: -0.5px;
        }
        .spec-banner {
            background: rgba(30, 41, 59, 0.7);
            border: 1px solid rgba(59, 130, 246, 0.35);
            border-left: 5px solid #3b82f6;
            border-radius: 8px;
            padding: 16px 22px;
            margin-bottom: 24px;
            backdrop-filter: blur(8px);
        }
        .spec-title {
            font-size: 16px;
            font-weight: 700;
            color: #60a5fa;
            margin-bottom: 8px;
        }
        .spec-content {
            font-size: 14px;
            color: #cbd5e1;
            line-height: 1.65;
        }
        .stat-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 14px 20px;
            margin-bottom: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .stat-label {
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .stat-value {
            font-size: 30px;
            font-weight: 800;
            color: #0f172a;
        }
        .visualizer-box {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 18px 20px;
            min-height: 200px;
            max-height: 420px;
            overflow-y: auto;
            line-height: 1.9;
            font-family: Consolas, 'Courier New', monospace;
            word-break: break-all;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .ids-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 14px 18px;
            font-family: Consolas, 'Courier New', monospace;
            font-size: 13.5px;
            line-height: 1.6;
            color: #334155;
            max-height: 150px;
            overflow-y: auto;
            word-break: break-all;
            margin-top: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .tok-chip {
            color: #0f172a;
            padding: 2px 3px;
            border-radius: 3px;
            margin: 0;
            display: inline;
            font-family: Consolas, 'Courier New', monospace;
            font-size: 15px;
            cursor: pointer;
        }
        .tok-c0 { background-color: #BAE6FD; }
        .tok-c1 { background-color: #FDE68A; }
        .tok-c2 { background-color: #A7F3D0; }
        .tok-c3 { background-color: #FECDD3; }
        .tok-c4 { background-color: #DDD6FE; }
        .tok-c5 { background-color: #FED7AA; }
        .tok-c6 { background-color: #E9D5FF; }
        .tok-c7 { background-color: #CCFBF1; }
    </style>
    """,
    unsafe_allow_html=True,
)

# 1. BADA HEADING with Author Attribution
st.markdown("<h1 class='main-title'>⚡ MiniBPETokenizer <span style='font-size: 16px; font-weight: 500; color: #94a3b8; margin-left: 10px;'>| Created by Raj</span></h1>", unsafe_allow_html=True)

# 2. BADA PROPER SPECIFICATIONS CARD
st.markdown(
    """
    <div class="spec-banner">
        <div class="spec-title">Model Specifications & Corpus Coverage</div>
        <div class="spec-content">
            • <strong>Developer:</strong> Created & Trained by <strong>Raj</strong><br>
            • <strong>Architecture:</strong> Byte-Level BPE | <strong>Vocabulary:</strong> 10,000 tokens (256 base bytes + 9,744 learned merges)<br>
            • <strong>Training Corpus:</strong> Curated ~18,900 lines of English technical text, mathematical expressions (Calculus, Greek notation: <em>α, β, ω, ∇, ∑</em>), and code syntax.<br>
            • <strong>Language Coverage:</strong> Highly optimized for English, math formulas, and code. Out-of-vocabulary scripts (e.g., Hindi / Devanagari) fall back to individual UTF-8 byte tokens.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Simple, Clean Default Showcase Text with Raj's Attribution
DEFAULT_TEXT = """# MiniBPETokenizer | Created by Raj

-- 1. Natural Language
Hello! This custom Byte-Level BPE tokenizer was built from scratch by Raj.

-- 2. Math & Formulas
f'(x) = n·x^(n-1)  and  y'' + ω²y = 0
7 + 5 = 12,  9 - 4 = 5,  and  2^10 = 1024

-- 3. Python Loop
total = 0
for i in range(5):
    total += i

-- 4. SQL Query
SELECT name, score FROM students WHERE score >= 80;"""

# 2-Column Spacious Layout
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    user_text = live_textarea(
        value=DEFAULT_TEXT,
        placeholder="Type or paste text here...",
        debounce=450,
        key="main_input",
    )

with col2:
    if user_text:
        # Ultra-fast cached inference
        ids, pieces = get_tokens_cached(user_text)
        tokens_with_ids = list(zip(ids, pieces))

        # 1. Token Count Card (Bada & Clear)
        st.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-label">Token count</div>
                <div class="stat-value">{len(ids)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 2. Tiktokenizer-style Visualizer (Bada & Spacious)
        st.markdown(render_tiktokenizer_view(tokens_with_ids), unsafe_allow_html=True)

        # 3. Token IDs Card
        ids_str = ", ".join(map(str, ids))
        st.markdown(f"<div class='ids-card'>{html.escape(ids_str)}</div>", unsafe_allow_html=True)
    else:
        st.info("Start typing on the left to see tokens!")