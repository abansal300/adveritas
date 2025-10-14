# backend/app/verdicts.py
import os
import json
import json5
import re
import boto3
from typing import Dict, List

# Configuration
USE_BEDROCK = os.getenv("USE_BEDROCK", "false").lower() == "true"
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "meta.llama3-2-3b-instruct-v1:0")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

_bedrock_client = None

def get_bedrock_client():
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = boto3.client(
            service_name='bedrock-runtime',
            region_name=AWS_REGION
        )
    return _bedrock_client

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
        snippet = (r.get("snippet") or "").replace("\n", " ")[:300]
        lines.append(f"[{title}] {url} — {snippet}")
    return "\n".join(lines)

def parse_json(s: str) -> Dict:
    m = re.search(r"\{.*\}", s, re.S)
    blob = m.group(0) if m else s
    try: 
        return json.loads(blob)
    except Exception:
        try: 
            return json5.loads(blob)
        except Exception:
            return {
                "label": "UNVERIFIABLE", 
                "confidence": 0.2, 
                "rationale": "Parser failed", 
                "sources": []
            }

def generate_verdict_bedrock(claim_text: str, evidence_rows: List[Dict]) -> Dict:
    """Use AWS Bedrock for verdict generation"""
    topk = int(os.getenv("VERDICT_TOPK", "5"))
    ev_block = build_evidence_block(evidence_rows[:topk])
    prompt = TEMPLATE.format(claim=claim_text, evidence=ev_block)
    
    # Bedrock API call
    client = get_bedrock_client()
    
    body = json.dumps({
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.1,
        "top_p": 0.9,
    })
    
    response = client.invoke_model(
        modelId=BEDROCK_MODEL_ID,
        body=body,
        contentType='application/json',
        accept='application/json'
    )
    
    response_body = json.loads(response['body'].read())
    generated_text = response_body.get('generation', '')
    
    out = parse_json(generated_text)
    
    # Normalize
    lbl = str(out.get("label","UNVERIFIABLE")).upper().replace(" ", "_")
    if lbl not in {"TRUE","PARTLY_TRUE","FALSE","UNVERIFIABLE"}:
        lbl = "UNVERIFIABLE"
    conf = float(out.get("confidence", 0.5))
    srcs = out.get("sources", [])
    if isinstance(srcs, str): 
        srcs = [srcs]
    
    return {
        "label": lbl, 
        "confidence": max(0.0, min(1.0, conf)),
        "rationale": out.get("rationale",""), 
        "sources": srcs
    }

def generate_verdict_local(claim_text: str, evidence_rows: List[Dict]) -> Dict:
    """Use local Hugging Face model (existing code)"""
    from transformers import pipeline
    
    _MODEL_NAME = os.getenv("VERDICT_MODEL", "gpt2-medium")
    _TOPK = int(os.getenv("VERDICT_TOPK", "5"))
    _HF_TOKEN = os.getenv("HF_TOKEN")
    
    _pipe = pipeline(
        "text-generation",
        model=_MODEL_NAME,
        device_map="auto" if os.getenv("CUDA_VISIBLE_DEVICES") else None,
        torch_dtype="auto",
        trust_remote_code=True,
        token=_HF_TOKEN,
    )
    
    ev_block = build_evidence_block(evidence_rows[:_TOPK])
    prompt = TEMPLATE.format(claim=claim_text, evidence=ev_block)
    
    gen = _pipe(
        prompt,
        max_new_tokens=100,
        do_sample=False,
        return_full_text=False,
    )[0]["generated_text"]
    
    out = parse_json(gen)
    lbl = str(out.get("label","UNVERIFIABLE")).upper().replace(" ", "_")
    if lbl not in {"TRUE","PARTLY_TRUE","FALSE","UNVERIFIABLE"}:
        lbl = "UNVERIFIABLE"
    conf = float(out.get("confidence", 0.5))
    srcs = out.get("sources", [])
    if isinstance(srcs, str): srcs = [srcs]
    
    return {
        "label": lbl, 
        "confidence": max(0.0, min(1.0, conf)),
        "rationale": out.get("rationale",""), 
        "sources": srcs
    }

# Main function - routes to Bedrock or local
def generate_verdict(claim_text: str, evidence_rows: List[Dict]) -> Dict:
    if USE_BEDROCK:
        return generate_verdict_bedrock(claim_text, evidence_rows)
    else:
        return generate_verdict_local(claim_text, evidence_rows)