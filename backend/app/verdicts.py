# backend/app/verdicts.py
"""
Verdict Generation Module

This module provides fact-checking verdict generation capabilities using either
AWS Bedrock or local Hugging Face models. It analyzes claims against evidence
and returns structured verdicts with confidence scores.
"""
import os
import json
import json5
import re
import logging
import boto3
from typing import Dict, List, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Configuration
USE_BEDROCK = os.getenv("USE_BEDROCK", "false").lower() == "true"
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "meta.llama3-2-3b-instruct-v1:0")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Cached clients
_bedrock_client = None
_local_pipeline = None


def get_bedrock_client():
    """
    Get or create a singleton AWS Bedrock client.
    
    Returns:
        boto3.client: Configured Bedrock runtime client
    """
    global _bedrock_client
    if _bedrock_client is None:
        try:
            _bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=AWS_REGION
            )
            logger.info(f"Initialized Bedrock client in region {AWS_REGION}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
    return _bedrock_client


def get_local_pipeline():
    """
    Get or create a singleton local model pipeline.
    
    Returns:
        transformers.Pipeline: Cached text generation pipeline
    """
    global _local_pipeline
    if _local_pipeline is None:
        from transformers import pipeline
        
        model_name = os.getenv("VERDICT_MODEL", "gpt2-medium")
        hf_token = os.getenv("HF_TOKEN")
        
        logger.info(f"Loading local model: {model_name}")
        _local_pipeline = pipeline(
            "text-generation",
            model=model_name,
            device_map="auto" if os.getenv("CUDA_VISIBLE_DEVICES") else None,
            torch_dtype="auto",
            trust_remote_code=True,
            token=hf_token,
        )
        logger.info("Local model pipeline initialized")
    return _local_pipeline


TEMPLATE = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a fact-checking assistant. Analyze the claim against the provided evidence and return ONLY a valid JSON object.

<|eot_id|><|start_header_id|>user<|end_header_id|>

CLAIM: {claim}

EVIDENCE:
{evidence}

Return ONLY a valid JSON object with these exact keys:
- label: one of ["TRUE", "PARTLY_TRUE", "FALSE", "UNVERIFIABLE"]
- confidence: float between 0.0 and 1.0
- rationale: string explaining your reasoning
- sources: array of relevant source URLs

Label guidelines:
- TRUE: Evidence strongly supports the claim
- PARTLY_TRUE: Evidence partially supports the claim
- FALSE: Evidence directly contradicts the claim (proves it wrong)
- UNVERIFIABLE: No relevant evidence found OR evidence is insufficient to determine truth

IMPORTANT: If the evidence is unrelated or irrelevant to the claim, you MUST use UNVERIFIABLE, not FALSE.

Example format:
{{"label": "UNVERIFIABLE", "confidence": 0.3, "rationale": "No relevant evidence found", "sources": []}}

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""


def build_evidence_block(rows: List[Dict]) -> str:
    """
    Format evidence rows into a readable text block.
    
    Args:
        rows: List of evidence dictionaries with title, url, and snippet
        
    Returns:
        Formatted evidence string
    """
    lines = []
    for r in rows:
        title = (r.get("title") or "")
        url = (r.get("url") or "")
        snippet = (r.get("snippet") or "").replace("\n", " ")[:300]
        lines.append(f"[{title}] {url} — {snippet}")
    return "\n".join(lines)


def parse_json(s: str) -> Dict:
    """
    Parse JSON from LLM output with fallback handling.
    
    Attempts to extract and parse JSON even from messy model outputs.
    Falls back to json5 for malformed JSON, and returns a safe default
    if all parsing fails.
    
    Args:
        s: Raw string output from LLM
        
    Returns:
        Parsed verdict dictionary with required fields
    """
    s = s.strip()
    
    # Try to find JSON object in the response
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', s, re.S)
    if json_match:
        blob = json_match.group(0)
    else:
        # Fallback: look for any JSON-like structure
        json_match = re.search(r"\{.*\}", s, re.S)
        blob = json_match.group(0) if json_match else s
    
    # Try standard JSON first
    try: 
        result = json.loads(blob)
        if all(key in result for key in ["label", "confidence", "rationale", "sources"]):
            logger.debug("Successfully parsed JSON response")
            return result
    except json.JSONDecodeError as e:
        logger.debug(f"Standard JSON parsing failed: {e}")
    
    # Try json5 (more lenient)
    try: 
        result = json5.loads(blob)
        if all(key in result for key in ["label", "confidence", "rationale", "sources"]):
            logger.debug("Successfully parsed JSON5 response")
            return result
    except Exception as e:
        logger.debug(f"JSON5 parsing failed: {e}")
    
    # Last resort: return minimal valid response
    logger.warning(f"Failed to parse model response. Raw output: {s[:200]}...")
    return {
        "label": "UNVERIFIABLE", 
        "confidence": 0.2, 
        "rationale": f"Parser failed. Raw response: {s[:200]}...", 
        "sources": []
    }


def normalize_verdict(out: Dict) -> Dict:
    """
    Normalize and validate verdict fields.
    
    Args:
        out: Raw verdict dictionary from parser
        
    Returns:
        Normalized verdict with valid label, confidence, rationale, and sources
    """
    # Normalize label
    lbl = str(out.get("label", "UNVERIFIABLE")).upper().replace(" ", "_")
    valid_labels = {"TRUE", "PARTLY_TRUE", "FALSE", "UNVERIFIABLE"}
    if lbl not in valid_labels:
        logger.warning(f"Invalid label '{lbl}', defaulting to UNVERIFIABLE")
        lbl = "UNVERIFIABLE"
    
    # Normalize confidence
    conf = float(out.get("confidence", 0.5))
    conf = max(0.0, min(1.0, conf))  # Clamp to [0, 1]
    
    # Normalize sources
    srcs = out.get("sources", [])
    if isinstance(srcs, str): 
        srcs = [srcs]
    
    return {
        "label": lbl, 
        "confidence": conf,
        "rationale": out.get("rationale", ""), 
        "sources": srcs
    }


def generate_verdict_bedrock(claim_text: str, evidence_rows: List[Dict]) -> Dict:
    """
    Generate verdict using AWS Bedrock inference.
    
    Args:
        claim_text: The claim to fact-check
        evidence_rows: List of evidence items with snippets and sources
        
    Returns:
        Verdict dictionary with label, confidence, rationale, and sources
        
    Raises:
        Exception: If Bedrock API call fails
    """
    topk = int(os.getenv("VERDICT_TOPK", "5"))
    ev_block = build_evidence_block(evidence_rows[:topk])
    prompt = TEMPLATE.format(claim=claim_text, evidence=ev_block)
    
    logger.info(f"Generating verdict for claim (Bedrock): {claim_text[:100]}...")
    
    # Bedrock API call
    client = get_bedrock_client()
    
    body = json.dumps({
        "prompt": prompt,
        "max_gen_len": 512,
        "temperature": 0.1,
        "top_p": 0.9,
        "stop": ["<|eot_id|>", "<|end_of_text|>"]
    })
    
    try:
        response = client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        response_body = json.loads(response['body'].read())
        generated_text = response_body.get('generation', '')
        
        logger.info(f"Bedrock response received ({len(generated_text)} chars)")
        logger.debug(f"Raw model output: {generated_text[:500]}...")
        
        out = parse_json(generated_text)
        logger.debug(f"Parsed verdict: {out}")
        
        return normalize_verdict(out)
        
    except Exception as e:
        logger.error(f"Bedrock API call failed: {e}")
        raise


def generate_verdict_local(claim_text: str, evidence_rows: List[Dict]) -> Dict:
    """
    Generate verdict using local Hugging Face model.
    
    Args:
        claim_text: The claim to fact-check
        evidence_rows: List of evidence items with snippets and sources
        
    Returns:
        Verdict dictionary with label, confidence, rationale, and sources
    """
    topk = int(os.getenv("VERDICT_TOPK", "5"))
    ev_block = build_evidence_block(evidence_rows[:topk])
    prompt = TEMPLATE.format(claim=claim_text, evidence=ev_block)
    
    logger.info(f"Generating verdict for claim (local): {claim_text[:100]}...")
    
    pipe = get_local_pipeline()
    
    gen = pipe(
        prompt,
        max_new_tokens=100,
        do_sample=False,
        return_full_text=False,
    )[0]["generated_text"]
    
    logger.info(f"Local model response received ({len(gen)} chars)")
    logger.debug(f"Raw model output: {gen[:500]}...")
    
    out = parse_json(gen)
    logger.debug(f"Parsed verdict: {out}")
    
    return normalize_verdict(out)


def generate_verdict(claim_text: str, evidence_rows: List[Dict]) -> Dict:
    """
    Main function to generate verdict using configured backend.
    
    Routes to either AWS Bedrock or local model based on USE_BEDROCK env var.
    
    Args:
        claim_text: The claim to fact-check
        evidence_rows: List of evidence items with snippets and sources
        
    Returns:
        Verdict dictionary with label, confidence, rationale, and sources
    """
    if USE_BEDROCK:
        return generate_verdict_bedrock(claim_text, evidence_rows)
    else:
        return generate_verdict_local(claim_text, evidence_rows)
