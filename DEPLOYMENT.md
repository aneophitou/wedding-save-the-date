# DNS setup for wedding.neophitou.com

Add this record at your domain registrar (where you manage neophitou.com DNS):

| Field | Value |
|-------|-------|
| **Type** | CNAME |
| **Name / Host** | `wedding` |
| **Value / Points to** | `andreasngnosisnet.github.io` |
| **TTL** | 3600 (or default) |

After pushing to GitHub and enabling Pages:

1. Create repo `wedding-save-the-date` on GitHub (or any name).
2. Push this project: `git remote add origin https://github.com/andreasngnosisnet/wedding-save-the-date.git` then `git push -u origin master`
3. **Settings → Pages → Build and deployment:** Source = **GitHub Actions**
4. **Settings → Pages → Custom domain:** enter `wedding.neophitou.com`
5. Wait for DNS + HTTPS (up to 24 hours)

Verify with: `nslookup wedding.neophitou.com`
