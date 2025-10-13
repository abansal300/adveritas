# ✅ AdVeritas Deployment Checklist

## Pre-Deployment Setup ✓ DONE

- ✅ Frontend updated to use `API_URL` environment variable
- ✅ `.gitignore` updated to exclude `venv/`
- ✅ Deployment guides created (`DEPLOY.md`, `README_DEPLOYMENT.md`)
- ✅ Command reference created (`COMMANDS.md`)
- ✅ Render configuration created (`backend/render.yaml`)

## Your Next Steps

### 1️⃣ Create GitHub Repository (2 minutes)

```bash
# Go to: https://github.com/new
# Create a new repository named "adveritas"
# Then run:

cd /Users/arnav/adveritas
git init
git add .
git commit -m "Initial commit - AdVeritas fact-checking app"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/adveritas.git
git push -u origin main
```

### 2️⃣ Deploy to Render (15 minutes)

**Follow the guide:** `/Users/arnav/adveritas/DEPLOY.md`

Quick summary:
1. Sign up at https://dashboard.render.com
2. Create PostgreSQL database (free)
3. Create Redis cache (free)
4. Create Web Service for API (free)
5. Create Background Worker for Celery (free)

### 3️⃣ Deploy to Vercel (5 minutes)

1. Go to https://vercel.com/new
2. Import your GitHub repo
3. Set root directory to `frontend`
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = your Render API URL
5. Deploy!

### 4️⃣ Test Your Deployed App

1. Visit your Vercel URL
2. Enter a YouTube URL
3. Wait 30-60 seconds (cold start on free tier)
4. See your fact-checking results!

---

## 📄 Reference Files

- **Quick Start:** `DEPLOY.md`
- **Detailed Guide:** `README_DEPLOYMENT.md`
- **Commands:** `COMMANDS.md`
- **This Checklist:** `DEPLOYMENT_CHECKLIST.md`

---

## 💡 Tips

1. **First deployment takes time** (~5-10 minutes for backend to build)
2. **Free tier has cold starts** (30-60s when app sleeps)
3. **Use cron-job.org** to ping your API every 10 min to keep it warm
4. **Check logs** on Render dashboard if something breaks

---

## 🆘 Need Help?

**Issues?**
- Check Render logs: Dashboard → Service → Logs
- Check Vercel logs: Dashboard → Project → Deployments
- Frontend not connecting? Verify `NEXT_PUBLIC_API_URL` is correct

**Questions?**
- Read `README_DEPLOYMENT.md` for detailed troubleshooting
- Check `COMMANDS.md` for useful commands

---

**Ready to deploy? Start with Step 1️⃣ above!** 🚀
