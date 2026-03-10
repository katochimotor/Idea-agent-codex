$ErrorActionPreference = "Stop"

git add .
git commit -m "dev update: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git push
