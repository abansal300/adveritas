# 🎯 AdVeritas - Quick Commands

## Local Development

### Start Backend (Docker)
```bash
cd /Users/arnav/adveritas
docker compose up -d
```

### Start Frontend
```bash
cd /Users/arnav/adveritas/frontend
npm run dev
```

### Stop Everything
```bash
# Stop backend
docker compose down

# Stop frontend (in the terminal where it's running)
Ctrl+C
```

### View Logs
```bash
# Backend logs
docker compose logs -f api

# Worker logs
docker compose logs -f worker
```

## Deployment

### Push to GitHub
```bash
cd /Users/arnav/adveritas
git add .
git commit -m "Your commit message"
git push
```

### Check Deployment Status
- **Frontend:** https://vercel.com/dashboard
- **Backend:** https://dashboard.render.com

## URLs

### Local Development
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

### Production (after deployment)
- Frontend: https://adveritas.vercel.app
- Backend: https://adveritas-api.onrender.com

## Testing

### Test Pipeline (Local)
```bash
cd /Users/arnav/adveritas
bash scripts/test_pipeline.sh
```

### Test API (Local)
```bash
# Health check
curl http://localhost:8000/health

# List videos
curl http://localhost:8000/videos/

# Get video details
curl http://localhost:8000/videos/4
```

## Troubleshooting

### Reset Database
```bash
docker compose down -v
docker compose up -d
```

### Clear Docker Cache
```bash
docker system prune -a --volumes
```

### Frontend Not Updating
```bash
cd frontend
rm -rf .next
npm run dev
```

### Backend Not Starting
```bash
docker compose logs api
docker compose restart api
```
