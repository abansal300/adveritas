# Railway Backend Deployment Guide

Complete step-by-step guide to deploy AdVeritas backend to Railway.

## Prerequisites

- Railway account (free tier available)
- GitHub repository with your code
- 15 minutes of time

## Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project" or "Login"
3. Connect with your GitHub account
4. Authorize Railway to access your repositories

## Step 2: Create New Project

1. Click "New Project" button
2. Select "Deploy from GitHub repo"
3. Choose your `adveritas` repository
4. Railway will detect it's a monorepo

## Step 3: Add PostgreSQL Database

1. In your Railway project dashboard, click "+ New"
2. Select "Database" → "Add PostgreSQL"
3. Railway will automatically provision the database
4. The `DATABASE_URL` environment variable will be auto-generated

## Step 4: Add Redis Cache

1. Click "+ New" again
2. Select "Database" → "Add Redis"
3. Railway will provision Redis
4. The `REDIS_URL` environment variable will be auto-generated

## Step 5: Configure Backend Service

### 5.1 Service Settings

1. Click on your backend service (should be auto-created from GitHub)
2. Go to "Settings" tab

### 5.2 Set Root Directory

1. Scroll to "Source"
2. Under "Root Directory", enter: `backend`
3. Click "Save"

### 5.3 Environment Variables

Click on the "Variables" tab and add these:

```bash
# Auto-linked (should already be there)
DATABASE_URL → (linked from PostgreSQL service)
REDIS_URL → (linked from Redis service)

# LLM Configuration - Option 1: Local Model (FREE)
USE_BEDROCK=false
VERDICT_MODEL=gpt2-medium

# LLM Configuration - Option 2: AWS Bedrock (BETTER QUALITY)
# USE_BEDROCK=true
# BEDROCK_MODEL_ID=arn:aws:bedrock:us-east-2:240147162366:inference-profile/us.meta.llama3-2-3b-instruct-v1:0
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=<your-key>
# AWS_SECRET_ACCESS_KEY=<your-secret>

# Embeddings
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Model Parameters
CLAIM_MIN_SCORE=0.35
VERDICT_TOPK=5

# Python
PYTHONUNBUFFERED=1
```

**If using AWS Bedrock** (recommended for better quality):
- Add your AWS credentials from `.env` file
- Make sure your AWS account has Bedrock access
- The ARN is already configured

### 5.4 Generate Public Domain

1. Go to "Settings" → "Networking"
2. Click "Generate Domain"
3. Copy your backend URL (e.g., `https://adveritas-backend-production.up.railway.app`)
4. **Save this URL** - you'll need it for Vercel!

## Step 6: Deploy

1. Railway will automatically start deploying
2. Watch the "Deployments" tab for progress
3. Click on the deployment to see build logs
4. Wait 5-10 minutes for first deployment (downloading ML models)

### Troubleshooting Deployment

**Build fails with memory error:**
- Click on your service → Settings → Resources
- Railway free tier has 8GB RAM, which should be enough
- If still failing, consider removing torch/transformers from dependencies temporarily

**Database connection fails:**
- Make sure DATABASE_URL is properly linked
- Check that pgvector extension is supported (Railway's PostgreSQL supports it by default)

**Redis connection fails:**
- Make sure REDIS_URL is properly linked
- Format should be: `redis://default:password@host:port`

## Step 7: Verify Deployment

1. Open your Railway backend URL in browser
2. You should see: `{"message": "Adveritas API is running."}`
3. Add `/docs` to URL to see API documentation
4. Test health endpoint: `/health` should return `{"ok": true, "service": "api"}`

## Step 8: Update Vercel Frontend

Now that backend is deployed, update your Vercel frontend:

1. Go to Vercel dashboard
2. Open your `adveritas` project
3. Go to Settings → Environment Variables
4. Find `NEXT_PUBLIC_API_URL`
5. Update value to your Railway backend URL
6. Click "Save"
7. Go to Deployments → Click "Redeploy" on latest deployment

## Step 9: Test End-to-End

1. Open your Vercel frontend URL
2. Paste a YouTube URL (try: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
3. Click "Analyze Video"
4. Wait for transcription
5. Extract claims
6. Fetch evidence
7. Generate verdict

**Success!** 🎉

## Cost Breakdown

**Railway Free Tier:**
- $5 in free credits per month
- 8GB RAM, 8 vCPU
- Shared PostgreSQL and Redis
- Perfect for demos and small projects

**Estimated Usage:**
- Backend Service: ~$3-4/month
- PostgreSQL: ~$0.50/month
- Redis: ~$0.25/month
- **Total: ~$4-5/month** (within free tier!)

## Important Notes

### For Demo/Resume Use:

1. **Railway goes to sleep after inactivity**
   - Free tier apps sleep after 30 minutes of no requests
   - First request after sleep takes ~30 seconds to wake up
   - Solution: Use a service like [cron-job.org](https://cron-job.org) to ping your API every 20 minutes

2. **Large ML Models**
   - Whisper, Transformers take time to download on first deploy
   - Models are cached, subsequent deployments are faster
   - Using AWS Bedrock instead of local models saves memory

3. **Video Processing**
   - Longer videos require more resources
   - For demos, use videos <5 minutes
   - Celery worker processes tasks in background

### Upgrade Options (Future)

If you need more:
- Railway Pro: $20/month for more resources
- Deploy to AWS ECS for production scale
- Use separate services for Celery workers

## Common Issues & Solutions

### Issue: "ModuleNotFoundError"
**Solution:** Railway didn't install dependencies
- Check that `pyproject.toml` is in backend directory
- Verify Root Directory is set to `backend`
- Check build logs for pip install errors

### Issue: "Connection to database failed"
**Solution:**
- Make sure DATABASE_URL is linked from PostgreSQL service
- Check that pgvector extension is enabled in startup (it should be automatic)

### Issue: "Out of memory"
**Solution:**
- Switch to AWS Bedrock instead of local torch models
- Remove torch/transformers if not using local LLM
- Upgrade to Railway Pro for more RAM

### Issue: Backend is slow
**Solution:**
- First deployment is always slow (downloading models)
- Use AWS Bedrock for faster inference
- Consider caching frequently used embeddings

### Issue: CORS errors in frontend
**Solution:**
- Backend already has CORS enabled for all origins
- Make sure you're using the correct Railway backend URL in Vercel
- Check that URL doesn't have trailing slash

## Alternative: Deploy Without Celery (Simpler)

If you want to simplify and deploy without background workers:

1. Modify API endpoints to process synchronously instead of with Celery
2. Remove Redis requirement
3. Only need PostgreSQL
4. Responses will be slower but simpler architecture

## Next Steps

1. ✅ Backend deployed to Railway
2. ✅ Frontend deployed to Vercel
3. ✅ Both connected and working

**Now you have a live demo link for your resume!**

### Resume-Ready URLs:
- **Frontend:** `https://your-project.vercel.app`
- **Backend API:** `https://your-backend.up.railway.app`
- **API Docs:** `https://your-backend.up.railway.app/docs`

Add these to your resume, portfolio, and LinkedIn! 🚀
