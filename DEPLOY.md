# 🚀 Deploy AdVeritas for FREE (Vercel + Render)

## Quick Start (30 minutes)

### Step 1: Push to GitHub (5 min)

```bash
cd /Users/arnav/adveritas

# Initialize git if not done
git init
git add .
git commit -m "Initial commit - ready for deployment"

# Create repo on GitHub (https://github.com/new) then:
git remote add origin https://github.com/YOUR_USERNAME/adveritas.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy Backend to Render (15 min)

1. **Go to:** https://dashboard.render.com
2. **Sign up/Login** (use GitHub)
3. **Create PostgreSQL Database:**
   - Click "New +" → "PostgreSQL"
   - Name: `adveritas-db`
   - Plan: **Free**
   - Click "Create"
   - **Copy Internal Database URL**

4. **Create Redis:**
   - Click "New +" → "Redis"
   - Name: `adveritas-redis`
   - Plan: **Free**
   - Click "Create"
   - **Copy Internal Redis URL**

5. **Create Web Service (API):**
   - Click "New +" → "Web Service"
   - Connect GitHub → Select `adveritas` repo
   - Settings:
     - Name: `adveritas-api`
     - Root Directory: `backend`
     - Environment: **Docker**
     - Plan: **Free**
   - Environment Variables (click "Add Environment Variable"):
     ```
     DATABASE_URL=<paste from step 3>
     REDIS_URL=<paste from step 4>
     MINIO_ENDPOINT=http://localhost:9000
     MINIO_BUCKET=adveritas
     MINIO_ACCESS_KEY=minioadmin
     MINIO_SECRET_KEY=minioadmin
     EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
     CLAIM_MIN_SCORE=0.35
     VERDICT_MODEL=gpt2-medium
     VERDICT_TOPK=5
     ```
   - Click "Create Web Service"
   - **Copy your API URL** (e.g., `https://adveritas-api.onrender.com`)

6. **Create Background Worker:**
   - Click "New +" → "Background Worker"
   - Connect same GitHub repo
   - Settings:
     - Name: `adveritas-worker`
     - Root Directory: `backend`
     - Environment: **Docker**
     - Start Command: `celery -A app.celery_app.celery_app worker -l INFO --concurrency=1`
     - Plan: **Free**
   - Add **same Environment Variables as step 5**
   - Click "Create"

### Step 3: Deploy Frontend to Vercel (10 min)

1. **Go to:** https://vercel.com/new
2. **Import your GitHub repo**
3. **Configure:**
   - Root Directory: `frontend`
   - Framework: **Next.js** (auto-detected)
4. **Add Environment Variable:**
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://adveritas-api.onrender.com` (from Step 2.5)
5. **Click "Deploy"**
6. **Copy your Vercel URL** (e.g., `https://adveritas.vercel.app`)

### Step 4: Test It! 🎉

1. Visit your Vercel URL
2. Paste a YouTube URL
3. Click "Analyze Video"
4. **Wait 30-60 seconds** for first request (cold start on free tier)
5. See results!

---

## 📝 What You Get (FREE)

- ✅ **Frontend:** Hosted on Vercel (fast, no cold starts)
- ✅ **Backend API:** Hosted on Render (free tier)
- ✅ **Worker:** Background processing with Celery
- ✅ **Database:** PostgreSQL with pgvector
- ✅ **Cache:** Redis for task queue
- ✅ **HTTPS:** Automatic SSL certificates
- ✅ **Auto-deploy:** Every git push deploys automatically

## ⚠️ Limitations (Free Tier)

- **Cold starts:** Backend sleeps after 15 min → first request takes 30-60s
- **No persistent storage:** Audio files stored in `/tmp` (temporary)
- **CPU only:** GPT-2 model (basic verdicts, not production quality)

## 🆙 Upgrade Later

When ready for production:
- **Render Starter ($7/mo):** No cold starts, persistent storage
- **Better models:** Use OpenAI API or deploy to GPU server
- **Custom domain:** Add your own domain ($12/year)

---

## 🐛 Troubleshooting

**Frontend shows errors:**
- Check Vercel environment variable `NEXT_PUBLIC_API_URL`
- Verify backend is running on Render

**Backend not responding:**
- Check Render logs: Dashboard → adveritas-api → Logs
- First request takes 30-60s (cold start)

**Worker not processing:**
- Check Render logs: Dashboard → adveritas-worker → Logs
- Verify Redis and Database URLs are correct

---

**Need help?** Check `/Users/arnav/adveritas/README_DEPLOYMENT.md` for detailed guide.

**Your app is now LIVE! 🎉**

