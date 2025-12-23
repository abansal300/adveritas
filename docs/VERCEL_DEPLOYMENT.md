# Vercel Deployment Guide

This guide will help you deploy the AdVeritas frontend to Vercel.

## Prerequisites

1. A Vercel account (sign up at [vercel.com](https://vercel.com))
2. A deployed backend API (see Backend Deployment below)

## Frontend Deployment to Vercel

### Option 1: Deploy via Vercel CLI (Recommended)

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy from the project root:
```bash
vercel
```

4. Follow the prompts:
   - Set up and deploy? **Y**
   - Which scope? Select your account
   - Link to existing project? **N**
   - What's your project's name? **adveritas**
   - In which directory is your code located? **frontend**

5. Set environment variables:
```bash
vercel env add NEXT_PUBLIC_API_URL production
```
Enter your backend API URL when prompted (e.g., `https://your-backend.railway.app`)

6. Deploy to production:
```bash
vercel --prod
```

### Option 2: Deploy via Vercel Dashboard

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository
3. Configure the project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
4. Add environment variable:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: Your backend API URL
5. Click "Deploy"

## Backend Deployment

The backend requires PostgreSQL, Redis, and Celery workers. Recommended platforms:

### Option 1: Railway (Easiest)

1. Go to [railway.app](https://railway.app)
2. Create new project from GitHub repo
3. Add services:
   - PostgreSQL database
   - Redis
4. Configure environment variables in Railway dashboard
5. Deploy backend service

### Option 2: Render

1. Go to [render.com](https://render.com)
2. Create new Web Service from GitHub repo
3. Set:
   - **Build Command**: `cd backend && pip install -e .`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0`
4. Add PostgreSQL and Redis services
5. Configure environment variables

### Option 3: AWS (Most Control)

Deploy using:
- **Backend**: AWS Elastic Beanstalk or ECS
- **Database**: AWS RDS (PostgreSQL)
- **Cache**: AWS ElastiCache (Redis)
- **Queue**: AWS SQS (alternative to Celery)

## Environment Variables

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://your-backend-api-url.com
```

### Backend
See backend/.env.example for full list of required variables.

## Post-Deployment

1. Test the frontend at your Vercel URL
2. Submit a YouTube URL to verify the connection to your backend
3. Add your Vercel URL to your resume!

## Troubleshooting

**Frontend shows connection errors:**
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check backend is running and accessible
- Verify CORS is configured in backend to allow your Vercel domain

**Build fails:**
- Check build logs in Vercel dashboard
- Verify all dependencies are in package.json
- Ensure Node.js version compatibility

## Demo Tips

For a resume demo link:
1. Use a short, memorable URL (customize in Vercel dashboard)
2. Prepare example YouTube URLs that work well
3. Consider adding a "Demo Video" button with a pre-loaded example
4. Add analytics to track visitors (Vercel Analytics)
