# Deploying Wingato Open

Ships with a `Dockerfile` and a Render Blueprint (`render.yaml`).

## 1. Push to GitHub

Fastest way: run **deploy.bat** (Windows) or **deploy.sh** (Mac/Linux) and
paste your repo URL when asked. Or do it by hand:

```bash
cd wingato-open
git init
git add .
git commit -m "Wingato Open"
git branch -M main
git remote add origin https://github.com/<your-username>/wingato-open.git
git push -u origin main
```

(Create the empty repo on github.com first. Use a Personal Access Token as
the password if asked.)

## 2. Deploy on Render

1. Sign up at render.com (GitHub login is easiest).
2. **New +** → **Blueprint** → pick the `wingato-open` repo.
3. Render reads `render.yaml`, builds the Docker image, and deploys.
4. You get a URL like `https://wingato-open.onrender.com`.

Every push to `main` redeploys automatically.

## 3. Free-tier caveats

- **Spins down after ~15 min idle**; next visit takes 30–60s to wake.
- **Limited bandwidth.** Streaming big files through the free tier is fine
  for light use; heavy traffic will hit limits. (A future improvement is to
  redirect to the source URL instead of proxying, which uses no server
  bandwidth.)
- No disk needed — nothing is stored.

## 4. Adding ads

1. Get approved by an ad network (AdSense, Ezoic, PropellerAds, etc.).
   Legal, family-safe content makes approval straightforward.
2. Paste the ad code into the `.ad-slot` blocks in
   `templates/index.html`, `results.html` and `item.html`.
3. Redeploy (just push).

## 5. Other free hosts

Koyeb, Fly.io and Railway all run the included Dockerfile. Any host that
runs containers will work — no ffmpeg or special runtime needed.
