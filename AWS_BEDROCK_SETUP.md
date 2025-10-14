# 🚀 AWS Bedrock Setup Guide

## Why Use AWS Bedrock?

Your current setup uses **GPT-2** locally, which:
- ❌ Doesn't follow instructions well (not instruction-tuned)
- ❌ Returns "Parser failed" errors
- ❌ Slow on CPU (~60 seconds per verdict)

AWS Bedrock with **Llama 3.2** will:
- ✅ Generate proper JSON verdicts
- ✅ Much faster (2-5 seconds per verdict)
- ✅ Better quality fact-checking
- ✅ Only ~$0.001 per verdict (very cheap!)

---

## 📋 Setup Steps

### **1. Get AWS Credentials**

1. **Log in to AWS Console:** https://console.aws.amazon.com
2. **Go to IAM:** https://console.aws.amazon.com/iam/home#/security_credentials
3. **Create Access Key:**
   - Click "Create access key"
   - Select "Application running outside AWS"
   - Copy both: `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`

### **2. Request Bedrock Access**

1. **Go to Bedrock Console:** https://console.aws.amazon.com/bedrock
2. **Select Region:** us-east-1 (or your preferred region)
3. **Request Model Access:**
   - Click "Model access" in left sidebar
   - Find "Meta" → "Llama 3.2 3B Instruct"
   - Click "Request model access"
   - Usually approved instantly!

### **3. Add Credentials to .env File**

```bash
cd /Users/arnav/adveritas
nano .env
```

**Replace these lines:**
```bash
AWS_ACCESS_KEY_ID=YOUR_AWS_ACCESS_KEY_HERE
AWS_SECRET_ACCESS_KEY=YOUR_AWS_SECRET_KEY_HERE
```

**With your actual credentials from step 1.**

Save and exit (Ctrl+O, Enter, Ctrl+X).

### **4. Restart Docker Services**

```bash
docker compose restart worker api
```

### **5. Test It!**

```bash
./scripts/test_pipeline.sh
```

You should now see proper verdicts with labels like `TRUE`, `FALSE`, `PARTLY_TRUE`, or `UNVERIFIABLE` instead of "Parser failed"! 🎉

---

## 🔧 Configuration Options

### **Available Llama Models on Bedrock:**

Edit `.env` to change `BEDROCK_MODEL_ID`:

- `meta.llama3-2-1b-instruct-v1:0` - Fastest, cheapest
- `meta.llama3-2-3b-instruct-v1:0` - **Recommended** (balanced)
- `meta.llama3-2-11b-instruct-v1:0` - Higher quality
- `meta.llama3-2-90b-instruct-v1:0` - Best quality (expensive)

### **Switch Back to Local Models:**

If you want to use local models again:

```bash
# Edit .env
USE_BEDROCK=false
```

---

## 💰 Pricing (Very Affordable!)

**Llama 3.2 3B Instruct (us-east-1):**
- Input: ~$0.00015 per 1K tokens
- Output: ~$0.0002 per 1K tokens
- **Per verdict: ~$0.001-0.002** (less than a penny!)
- **1000 verdicts: ~$1-2**

---

## 🎯 For Your Resume

Once working with Bedrock, you can say:

**SWE Resume:**
- "Integrated AWS Bedrock for scalable LLM inference, reducing verdict generation time from 60s to 3s"
- "Deployed production system using AWS Bedrock with Llama-3.2-3B for high-quality fact verification"

**DS/ML Resume:**
- "Optimized ML inference pipeline by migrating from local models to AWS Bedrock, achieving 20x speedup"
- "Implemented cloud-native LLM deployment using AWS Bedrock with Llama 3.2 for real-time fact-checking"

---

## 🐛 Troubleshooting

### "Parser failed" still appears:
- Check `.env` file has correct credentials (no quotes needed)
- Verify `USE_BEDROCK=true` (no quotes)
- Restart worker: `docker compose restart worker`

### "AccessDeniedException" or "ModelNotFound":
- Request model access in Bedrock console
- Verify you're in the correct AWS region (us-east-1)
- Wait 5-10 minutes for access approval

### "Invalid credentials":
- Regenerate AWS access keys
- Make sure IAM user has Bedrock permissions

---

## ✅ Success Criteria

When working correctly, you'll see:

```json
{
  "ok": true,
  "label": "TRUE",           // or FALSE, PARTLY_TRUE, UNVERIFIABLE
  "confidence": 0.85,         // 0.0 to 1.0
  "rationale": "According to the evidence from Wikipedia...",
  "sources": ["wikipedia.org/..."]
}
```

Instead of:
```json
{
  "ok": true,
  "label": "UNVERIFIABLE",
  "confidence": 0.2,
  "rationale": "Parser failed",  // ❌ This is the error!
  "sources": []
}
```

---

**Need help? Check the AWS Bedrock documentation:** https://docs.aws.amazon.com/bedrock/

