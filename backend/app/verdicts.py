import os, json, json5, re, time
from typing import Dict, List
from transformers import pipeline

_MODEL_NAME = os.getenv("VERDICT_MODEL", "meta-llama/Llama-3.2-3B-Instruct")
_TOPK = int(os.getenv("VERDICT_TOPK", "5"))
_HF_TOKEN = os.getenv("HF_TOKEN")

_pipe = None
def get_pipe():
    global _pipe
    if _pipe is None:
        # text-generation works across most instruct models
        _pipe = pipeline(
            "text-generation",
            model=_MODEL_NAME,
            device_map="auto" if os.getenv("CUDA_VISIBLE_DEVICES") else None,
            torch_dtype="auto",
            trust_remote_code=True,
            token=_HF_TOKEN,  # Pass HF token for gated models
        )
    return _pipe

TEMPLATE = """You are a fact-checking assistant.
Decide if the CLAIM is true, partly true, false, or unverifiable using the EVIDENCE passages.
Respond ONLY as a compact JSON object with keys: label, confidence, rationale, sources.
Allowed labels: TRUE, PARTLY_TRUE, FALSE, UNVERIFIABLE.
Confidence must be a float 0..1.
If no decisive evidence, choose UNVERIFIABLE.

CLAIM:
{claim}

EVIDENCE (each item: [title] url — snippet):
{evidence}

JSON:"""

def build_evidence_block(rows: List[Dict]) -> str:
    lines = []
    for r in rows:
        title = (r.get("title") or "")
        url = (r.get("url") or "")
        raw_snippet = (r.get("snippet") or "")
        # clean outside the f-string (no backslashes inside {...})
        snippet_clean = raw_snippet.replace("\n", " ")[:300]
        lines.append(f"[{title}] {url} — {snippet_clean}")
    return "\n".join(lines)

def parse_json(s: str) -> Dict:
    # Try strict JSON first, then json5, then regex salvage
    m = re.search(r"\{.*\}", s, re.S)
    blob = m.group(0) if m else s
    try: return json.loads(blob)
    except Exception:
        try: return json5.loads(blob)
        except Exception:
            # last resort minimal
            return {"label": "UNVERIFIABLE", "confidence": 0.2, "rationale": "Parser failed", "sources": []}

def generate_verdict(claim_text: str, evidence_rows: List[Dict]) -> Dict:
    ev_block = build_evidence_block(evidence_rows[:_TOPK])
    prompt = TEMPLATE.format(claim=claim_text, evidence=ev_block)
    gen = get_pipe()(
        prompt,
        max_new_tokens=100,  # Reduced for fast CPU generation (was 300)
        do_sample=False,
        return_full_text=False,
    )[0]["generated_text"]
    out = parse_json(gen)
    # normalize
    lbl = str(out.get("label","UNVERIFIABLE")).upper().replace(" ", "_")
    if lbl not in {"TRUE","PARTLY_TRUE","FALSE","UNVERIFIABLE"}:
        lbl = "UNVERIFIABLE"
    conf = float(out.get("confidence", 0.5))
    srcs = out.get("sources", [])
    if isinstance(srcs, str): srcs = [srcs]
    return {"label": lbl, "confidence": max(0.0, min(1.0, conf)),
            "rationale": out.get("rationale",""), "sources": srcs}
