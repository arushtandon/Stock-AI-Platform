# Safron setup: deploy, logo, and credentials

Follow these steps in order.

---

## 1. Deploy (push changes so Render redeploys)

### 1.1 Push your code to GitHub

In a terminal, from the **stock-ai-platform** folder:

```powershell
cd "C:\Users\tando\Order Placement\stock-ai-platform"
git add .
git status
git commit -m "Safron branding, Integrations page, logo placeholder"
git push origin main
```

(Use your actual path to the project if it’s different.)

### 1.2 Let Render redeploy

- **If auto-deploy is on:** Render will redeploy **stock-ai-api** and **stock-ai-frontend** after the push. Wait a few minutes and check the **Logs** for each service to confirm a successful deploy.
- **If nothing deploys:** In the Render dashboard, open **stock-ai-api** → **Manual Deploy** → **Deploy latest commit**. Do the same for **stock-ai-frontend**.

When both show “Deployed” (green), the new Safron UI and the `/integrations` page are live.

---

## 2. Replace the logo with the Safron company logo

### Option A – Replace the file (easiest)

1. Get your Safron logo as a file (e.g. `safron-logo.png` or `safron-logo.svg`).
2. In your project, go to:  
   `stock-ai-platform\frontend\public\`
3. **Either:**
   - Replace the existing **safron-logo.svg** with your logo file, **and** keep the name `safron-logo.svg`,  
   **or**
   - Add your file (e.g. `safron-logo.png`) and keep the same name so the app keeps working without code changes.
4. If you use a **different filename** (e.g. `my-safron-logo.png`), you must update the app to use it:
   - In the repo, search for `safron-logo.svg` (in `frontend/src`).
   - Replace every `src="/safron-logo.svg"` with `src="/my-safron-logo.png"` (or your filename).
5. Commit and push so the frontend redeploys with the new logo:

   ```powershell
   git add frontend/public/
   git commit -m "Use Safron company logo"
   git push origin main
   ```

### Option B – Only change the image path in code

1. Put your logo file in `frontend/public/` (e.g. `safron-logo.png`).
2. In every file that shows the logo, change the image source to your file, e.g.  
   from: `src="/safron-logo.svg"`  
   to: `src="/safron-logo.png"`.
3. Commit and push (as in step 5 above).

**Suggested logo size:** About 120×40 pixels (or similar ratio) so it fits the nav bar.

---

## 3. Set credentials (API keys for the four premium sources)

You add the keys in Render’s **Environment** for the API service. The app never sees the keys in the browser; only the server uses them.

### 3.1 Open the API service in Render

1. Go to [dashboard.render.com](https://dashboard.render.com) and sign in.
2. In the list of services, click **stock-ai-api**.

### 3.2 Open Environment

1. In the left sidebar, click **Environment** (under “Manage”).
2. You’ll see the existing environment variables.

### 3.3 Add the four variables

Click **Add Environment Variable** and add these **one by one**. Use the **key** exactly as written; the **value** is your API key or token from each provider.

| Key (name)            | Where to get the value |
|------------------------|------------------------|
| `DANELFIN_API_KEY`     | Your Danelfin account / API or subscription. |
| `SEEKING_ALPHA_API_KEY`| Seeking Alpha Premium: account or API credentials. |
| `INVESTING_PRO_API_KEY`| Investing.com Pro / InvestingPro API key. |
| `TRADINGVIEW_API_KEY` | TradingView API or webhook/token if they provide one. |

- **Key:** type exactly, e.g. `DANELFIN_API_KEY`.  
- **Value:** paste the key/token (often a long string). Don’t add quotes unless the provider says so.

Add all four, then click **Save Changes**.

### 3.4 Redeploy the API

After saving env vars, Render will usually ask to **redeploy** the service. If it doesn’t:

1. Go to the **stock-ai-api** service.
2. Click **Manual Deploy** (top right).
3. Choose **Deploy latest commit** (or the branch you use).

Wait until the deploy finishes (green “Deployed” and logs show the app started).

### 3.5 Check “Connected” on the Integrations page

1. Open your frontend URL, e.g. `https://stock-ai-frontend.onrender.com`.
2. In the nav, click **Integrations**.
3. For each of the four sources you configured, you should see **“Connected”** (green).  
   If you see **“Not configured”**, that variable is missing or wrong in Render → stock-ai-api → Environment; fix it and redeploy again.

---

## Quick checklist

| Step | What to do |
|------|------------|
| 1. Deploy | `git add .` → `git commit -m "..."` → `git push`; wait for Render to redeploy API and frontend (or trigger Manual Deploy). |
| 2. Logo | Put your Safron logo in `frontend/public/` as `safron-logo.svg` (or same name you use in code), then commit and push. |
| 3. Credentials | Render → stock-ai-api → Environment → add `DANELFIN_API_KEY`, `SEEKING_ALPHA_API_KEY`, `INVESTING_PRO_API_KEY`, `TRADINGVIEW_API_KEY` → Save → redeploy API. |
| 3b. Verify | Open frontend → Integrations; each source with a key set should show “Connected”. |

If a step fails (e.g. deploy error or still “Not configured”), check the **Logs** for that service on Render and fix the reported issue (typo in env name, wrong value, etc.).
