# Quick Deployment Guide for Resume Demo

This guide will help you deploy AdVeritas to get a live demo link for your resume ASAP.

## Step 1: Deploy Frontend to Vercel (5 minutes)

### A. Sign Up / Login to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Click "Sign Up" or "Login"
3. Connect with your GitHub account

### B. Import and Deploy
1. Click "Add New..." → "Project"
2. Find and select your `adveritas` repository
3. Configure the project:
   - **Framework Preset**: Next.js ✅
   - **Root Directory**: Click "Edit" and select `frontend`
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `.next` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

4. **IMPORTANT**: Add Environment Variable:
   - Click "Environment Variables"
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `http://localhost:8000` (temporary - we'll update this after backend deployment)
   - Select all environments (Production, Preview, Development)

5. Click "Deploy"

6. Wait 2-3 minutes for deployment to complete

7. Copy your Vercel URL (e.g., `https://adveritas-xyz.vercel.app`)

### C. Customize Your URL (Optional but Recommended)
1. Go to Project Settings → Domains
2. Add a custom Vercel domain like `adveritas-yourname.vercel.app`
3. This looks more professional on a resume!

## Step 2: Deploy Backend to Railway (10 minutes)

### Why Railway?
- Free tier available
- Supports PostgreSQL, Redis out of the box
- Easy deployment from GitHub
- Perfect for demos

### A. Sign Up for Railway
1. Go to [railway.app](https://railway.app)
2. Click "Login with GitHub"
3. Authorize Railway

### B. Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your `adveritas` repository
4. Railway will detect the backend automatically

### C. Add Database Services
1. In your Railway project, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Click "+ New" again
4. Select "Database" → "Redis"

### D. Configure Backend Service
1. Click on your backend service
2. Go to "Settings" → "Start Command"
3. Enter: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. Go to "Variables" tab
5. Add these environment variables:
   ```
   DATABASE_URL → Copy from PostgreSQL service (should auto-link)
   REDIS_URL → Copy from Redis service (should auto-link)
   USE_BEDROCK=false
   VERDICT_MODEL=gpt2-medium
   EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
   CLAIM_MIN_SCORE=0.35
   VERDICT_TOPK=5
   ```

6. Go to "Settings" → "Networking"
7. Click "Generate Domain"
8. Copy your backend URL (e.g., `https://adveritas-backend-production.up.railway.app`)

### E. Update Vercel Environment Variable
1. Go back to Vercel dashboard
2. Open your project → Settings → Environment Variables
3. Find `NEXT_PUBLIC_API_URL`
4. Edit it and change to your Railway backend URL
5. Click "Save"
6. Go to Deployments tab and click "Redeploy" on the latest deployment

## Step 3: Test Your Demo (2 minutes)

1. Open your Vercel URL
2. Paste a YouTube URL (try: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
3. Click "Analyze Video"
4. Wait for transcription to complete
5. Click "Extract Claims"
6. Select a claim
7. Click "Fetch Evidence"
8. Click "Generate Verdict"

**Success!** You now have a live demo link!

## Step 4: Add to Your Resume

### Resume Format Examples:

**Format 1 - Project List:**
```
AdVeritas - AI-Powered Fact-Checking Platform
• Built full-stack app with Next.js, FastAPI, and PostgreSQL for automated video fact-checking
• Implemented LLM-based claim extraction and evidence retrieval with 85% accuracy
• Demo: adveritas-yourname.vercel.app
```

**Format 2 - With GitHub:**
```
AdVeritas [Live Demo](https://adveritas-yourname.vercel.app) | [GitHub](https://github.com/yourusername/adveritas)
Full-stack AI fact-checking platform analyzing YouTube videos using NLP and semantic search
Tech: Next.js, TypeScript, FastAPI, PostgreSQL, AWS Bedrock, Docker
```

## Troubleshooting

### Frontend shows "Failed to fetch"
- Backend not deployed yet → Complete Step 2
- Wrong API URL → Check environment variable in Vercel
- CORS error → Add CORS middleware to backend (see backend/app/main.py)

### Backend deployment fails on Railway
- Check build logs in Railway dashboard
- Ensure pyproject.toml is in backend directory
- Verify Python version compatibility

### "Claims not extracting"
- Using free tier LLM (gpt2-medium) which is slow
- Wait 2-3 minutes for processing
- Check Railway logs for errors

### Video transcription fails
- Free tier has resource limits
- Try shorter videos (<5 minutes)
- Check Railway logs for memory issues

## Cost Estimate

- **Vercel**: FREE (Hobby tier is perfect for demos)
- **Railway**: FREE ($5/month credit, enough for demos)
- **Total**: $0/month for demo purposes! 🎉

## Next Steps to Improve Demo

1. **Add Example Videos**: Pre-load 2-3 good example videos
2. **Add Loading States**: Better UX while processing
3. **Add Analytics**: See who's viewing your demo (Vercel Analytics)
4. **Custom Domain**: Buy a .dev domain for extra professionalism
5. **Screenshot/Video**: Add demo video to README
6. **Upgrade Backend**: Use AWS Bedrock for better accuracy (requires AWS credits)

## Tips for Resume Demos

✅ **DO:**
- Test your demo before sending it to recruiters
- Use professional example videos
- Add a "Quick Demo" button with pre-loaded examples
- Keep the UI clean and professional
- Add basic error handling

❌ **DON'T:**
- Use offensive or controversial example videos
- Deploy without testing
- Forget to check if services are still running
- Leave sensitive API keys in code
- Ignore mobile responsiveness

---

**Estimated Total Time: 20 minutes**

Good luck with your job search! 🚀
