# Wedding Save-the-Date

Static landing page for **Andreas & Nikoleta** — guests scan a QR code and add the wedding to their calendar.

**Live URL:** https://wedding.neophitou.com

## Local preview

Serve the `site/` folder with any static file server, for example:

```powershell
cd site
python -m http.server 8080
```

Open http://localhost:8080

## Regenerate QR code

```powershell
npm install
npm run generate-qr
```

Outputs `qr-code.svg` and `qr-code.png` in the project root.

## Re-optimize background images

If you replace `Save The Date Assets/background.svg`:

```powershell
python scripts/optimize_background.py
```

## GitHub Pages setup

1. Create a GitHub repo and push this project.
2. In the repo go to **Settings → Pages → Build and deployment**:
   - Source: **GitHub Actions**
3. Push to `main` — the workflow deploys the `site/` folder automatically.
4. Add custom domain `wedding.neophitou.com` under **Settings → Pages → Custom domain**.
5. Ensure `site/CNAME` contains `wedding.neophitou.com` (already set).

## DNS (at your domain registrar)

Add one CNAME record:

| Type  | Name    | Value                      |
|-------|---------|----------------------------|
| CNAME | wedding | `YOUR_GITHUB_USERNAME.github.io` |

Replace `YOUR_GITHUB_USERNAME` with your GitHub username (e.g. `andreasngnosisnet`).

DNS can take up to 24 hours to propagate. GitHub will provision HTTPS once DNS is correct.

## Calendar event

- **Date:** 11 July 2027
- **Time:** 18:00 – 02:00 (Europe/Nicosia)
- **ICS file:** `site/AndreasAndNikoletaWedding.ics`
