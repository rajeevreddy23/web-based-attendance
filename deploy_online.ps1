# Quick Deployment Helper for Render (Backend + Database) & Vercel (Frontend)

param(
    [string]$GithubRepoUrl = ""
)

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " CAPSTONE CLOUD DEPLOYMENT: RENDER (BACKEND) + VERCEL (FRONTEND)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# Step 1: Push Code to GitHub
if (-not $GithubRepoUrl) {
    Write-Host "`n[1] Enter your GitHub Repository URL (e.g. https://github.com/yourname/attendance.git):" -ForegroundColor Yellow
    $GithubRepoUrl = Read-Host "GitHub Repo URL"
}

if ($GithubRepoUrl) {
    Write-Host "`n[*] Linking GitHub remote and pushing codebase..." -ForegroundColor Green
    git remote remove origin -ErrorAction SilentlyContinue
    git remote add origin $GithubRepoUrl
    git branch -M main
    git push -u origin main
    Write-Host "[+] Code successfully pushed to GitHub!" -ForegroundColor Green
} else {
    Write-Host "[!] Skipping Git push. Please push your code to GitHub before continuing." -ForegroundColor Red
}

# Step 2: Render Blueprint Instructions
Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host " STEP 2: DEPLOY BACKEND + DATABASE ON RENDER (1-Click Blueprint)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "1. Go to: https://dashboard.render.com/blueprints"
Write-Host "2. Click 'New Blueprint Instance' and select your GitHub repository."
Write-Host "3. Render will read 'render.yaml' and automatically create:"
Write-Host "   - Free PostgreSQL Database (attendance-db)"
Write-Host "   - FastAPI Docker Web Service (attendance-backend)"
Write-Host "4. Once deployed, copy your backend URL: e.g. https://attendance-backend.onrender.com"

# Step 3: Vercel Frontend Instructions
Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host " STEP 3: DEPLOY FRONTEND ON VERCEL" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "1. Go to: https://vercel.com/new"
Write-Host "2. Import your GitHub repository."
Write-Host "3. In 'Root Directory', click Edit and choose: frontend"
Write-Host "4. In 'Environment Variables', add:"
Write-Host "   NEXT_PUBLIC_API_URL = https://your-backend-name.onrender.com/api/v1"
Write-Host "5. Click 'Deploy'."
Write-Host "`n[*] Your Web-Based Attendance Management System will be live online!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
