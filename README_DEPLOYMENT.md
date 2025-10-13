# AdVeritas - Free Deployment Guide (Vercel + Render)

This guide will help you deploy AdVeritas **100% free** using Vercel (frontend) and Render (backend).

## 📋 Prerequisites

- GitHub account
- Vercel account (free) - sign up at https://vercel.com
- Render account (free) - sign up at https://render.com

## 🚀 Step-by-Step Deployment

### Part 1: Push to GitHub

1. **Create a new GitHub repository**
   - Go to https://github.com/new
   - Name it `adveritas`
   - Make it public or private
   - Don't initialize with README

2. **Push your code**
   ```bash
   cd /Users/arnav/adveritas
   git add .
   git commit -m "Prepare for deployment"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/adveritas.git
   git push -u origin main
   ```

### Part 2: Deploy Backend to Render

#### Option A: Manual Setup (Recommended for learning)

1. **Go to Render Dashboard**
   - Visit https://dashboard.render.com

2. **Create PostgreSQL Database**
   - Click "New +" → "PostgreSQL"
   - Name: `adveritas-db`
   - Database: `adveritas`
   - User: `adveritas`
   - Plan: **Free**
   - Click "Create Database"
   - **Copy the Internal Database URL** (starts with `postgresql://`)

3. **Create Redis**
   - Click "New +" → "Redis"
   - Name: `adveritas-redis`
   - Plan: **Free**
   - Click "Create Redis"
   - **Copy the Internal Redis URL** (starts with `redis://`)

4. **Create Web Service (API)**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Name: `adveritas-api`
   - Root Directory: `backend`
   - Environment: **Docker**
   - Plan: **Free**
   - Add Environment Variables:
     ```
     DATABASE_URL=<paste PostgreSQL URL from step 2>
     REDIS_URL=<paste Redis URL from step 3>
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
   - **Copy the service URL** (e.g., `https://adveritas-api.onrender.com`)

5. **Create Background Worker (Celery)**
   - Click "New +" → "Background Worker"
   - Connect your GitHub repository
   - Name: `adveritas-worker`
   - Root Directory: `backend`
   - Environment: **Docker**
   - Build Command: Leave empty
   - Start Command: `celery -A app.celery_app.celery_app worker -l INFO --concurrency=1`
   - Plan: **Free**
   - Add the **same environment variables as step 4**
   - Click "Create Background Worker"

#### Option B: Blueprint Setup (Faster)

1. **Go to Render Dashboard**
2. **Click "New +" → "Blueprint"**
3. **Connect your GitHub repository**
4. **Render will detect `render.yaml`** and create all services automatically
5. **Review and Deploy**

### Part 3: Deploy Frontend to Vercel

1. **Go to Vercel Dashboard**
   - Visit https://vercel.com/dashboard

2. **Import Project**
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Select the `frontend` folder as the root directory

3. **Configure Project**
   - Framework Preset: **Next.js**
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`
   
4. **Add Environment Variable**
   - Click "Environment Variables"
   - Add:
     ```
     Name: NEXT_PUBLIC_API_URL
     Value: https://adveritas-api.onrender.com
     ```
     (Use the URL from Part 2, Step 4)

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes
   - **Copy your Vercel URL** (e.g., `https://adveritas.vercel.app`)

### Part 4: Update CORS (Backend)

1. **Update `backend/app/main.py`**
   - Change CORS settings to allow your Vercel domain:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://adveritas.vercel.app"],  # Your Vercel URL
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Commit and push**
   ```bash
   git add backend/app/main.py
   git commit -m "Update CORS for production"
   git push
   ```

3. **Render will auto-deploy** the changes

## ✅ Verify Deployment

1. **Visit your Vercel URL** (e.g., `https://adveritas.vercel.app`)
2. **Test with a YouTube URL**
3. **Wait for processing** (first request takes ~30s due to cold start on free tier)

## ⚠️ Important Notes

### Free Tier Limitations

- **Render Free Tier:**
  - Spins down after 15 minutes of inactivity
  - First request after spin-down takes 30-60 seconds
  - 750 hours/month (enough for 1 service)

- **Vercel Free Tier:**
  - 100GB bandwidth/month
  - Unlimited deployments
  - No cold starts

### Storage Limitation

The free deployment **does not include MinIO** (S3 storage). Audio files are stored temporarily in `/tmp` and may be lost. 

**Solutions:**
1. **Use Cloudflare R2** (free tier: 10GB storage)
2. **Use AWS S3** (free tier: 5GB for 12 months)
3. **Upgrade Render** to paid plan with persistent storage

## 🆙 Upgrading

To eliminate cold starts and get persistent storage:

- **Render Starter Plan:** $7/month
  - No cold starts
  - 24/7 uptime
  - Persistent storage

## 🔧 Troubleshooting

### Frontend not connecting to backend
- Check `NEXT_PUBLIC_API_URL` in Vercel environment variables
- Verify backend is deployed and running

### Backend errors
- Check Render logs: Dashboard → Service → Logs
- Verify all environment variables are set

### Database connection errors
- Check `DATABASE_URL` is correctly copied from PostgreSQL service
- Ensure PostgreSQL service is running

### Cold start issues
- First request takes 30-60 seconds on free tier
- Use cron-job.org to ping your API every 10 minutes to keep it warm

## 📝 Next Steps

1. **Add custom domain** (optional, $12/year)
2. **Setup monitoring** with Render's built-in tools
3. **Add analytics** with Vercel Analytics (free)
4. **Upgrade to paid tier** when ready for production

---

**Your app is now live! 🎉**

Frontend: https://adveritas.vercel.app  
Backend: https://adveritas-api.onrender.com

