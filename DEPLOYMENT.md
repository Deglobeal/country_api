# Railway Deployment Guide

## Prerequisites
- GitHub account
- Railway account connected to GitHub
- MySQL database on Railway

## Deployment Steps

1. **Fork/Clone this repository** to your GitHub account

2. **Connect to Railway**:
   - Go to [Railway](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add Environment Variables**:
   - Go to your project settings on Railway
   - Add these variables:
     ```
     SECRET_KEY=your-very-secure-random-key
     DEBUG=False
     ALLOWED_HOSTS=.railway.app,your-app-name.railway.app
     ```
   - Railway automatically provides `DATABASE_URL`

4. **Add MySQL Database**:
   - In Railway dashboard, click "New" → "Database" → "MySQL"
   - Railway will automatically set `DATABASE_URL`

5. **Deploy**:
   - Railway will automatically deploy when you push to main
   - Or manually trigger deployment in the dashboard

6. **Verify Deployment**:
   - Check the deployment logs in Railway
   - Visit your app URL (provided by Railway)
   - Test endpoints:
     - `GET /` - API info
     - `POST /countries/refresh/` - Load data
     - `GET /countries/` - List countries

## Custom Domain (Optional)
- Go to Settings → Domains
- Add your custom domain
- Update DNS records as instructed

## Monitoring
- Check logs in Railway dashboard
- Monitor database usage
- Set up alerts for errors