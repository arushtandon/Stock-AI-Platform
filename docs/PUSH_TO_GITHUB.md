# How to Push This Repo to GitHub

Follow these steps to get **stock-ai-platform** on GitHub so you can deploy on Render (or use Blueprints elsewhere).

---

## 1. Create a GitHub account (if you don’t have one)

- Go to [github.com](https://github.com) and sign up.
- Verify your email if asked.

---

## 2. Install Git (if needed)

- **Windows:** Download from [git-scm.com](https://git-scm.com/download/win) or install via `winget install Git.Git`.
- **Mac:** `xcode-select --install` or install from [git-scm.com](https://git-scm.com/download/mac).
- **Linux:** e.g. `sudo apt install git` (Ubuntu/Debian).

Check:

```bash
git --version
```

---

## 3. Open the project folder in a terminal

```bash
cd "C:\Users\tando\Order Placement\stock-ai-platform"
```

(Use your actual path to the project.)

---

## 4. Initialize Git and add files

**If this folder is not a Git repo yet:**

```bash
git init
git add .
git status
```

You should see all project files listed. The `.gitignore` will exclude `.env`, `node_modules`, `.venv`, etc.

**Commit:**

```bash
git commit -m "Initial commit: Stock AI Platform"
```

---

## 5. Create a new repository on GitHub

1. Log in to [github.com](https://github.com).
2. Click the **+** (top right) → **New repository**.
3. **Repository name:** e.g. `stock-ai-platform`.
4. **Description:** optional (e.g. “Cloud stock analysis and recommendation platform”).
5. Choose **Public** (or Private if you have a paid account and want it private).
6. **Do not** check “Add a README”, “Add .gitignore”, or “Choose a license” (you already have files).
7. Click **Create repository**.

---

## 6. Connect your local repo to GitHub and push

GitHub will show commands. Use these (replace `YOUR_USERNAME` with your GitHub username and `stock-ai-platform` with your repo name if different):

```bash
git remote add origin https://github.com/YOUR_USERNAME/stock-ai-platform.git
git branch -M main
git push -u origin main
```

**Example** (if your username is `johndoe`):

```bash
git remote add origin https://github.com/johndoe/stock-ai-platform.git
git branch -M main
git push -u origin main
```

- If Git asks for **username**, use your GitHub username.
- If it asks for **password**, use a **Personal Access Token** (GitHub no longer accepts account passwords for push).  
  To create one: GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token**. Give it `repo` scope, copy the token, and paste it when Git asks for a password.

---

## 7. Confirm on GitHub

- Open `https://github.com/YOUR_USERNAME/stock-ai-platform`.
- You should see your files (e.g. `render.yaml`, `api/`, `frontend/`, `docs/`).

---

## 8. Deploy on Render

- Go to [render.com](https://render.com) → **New** → **Blueprint**.
- Connect GitHub and select **stock-ai-platform**.
- Render will use `render.yaml` to create the services. Click **Apply**.

See [DEPLOY_RENDER.md](DEPLOY_RENDER.md) for full Render steps.

---

## Quick reference

| Step | Command / action |
|------|-------------------|
| First-time setup | `git init` → `git add .` → `git commit -m "Initial commit"` |
| Create repo on GitHub | github.com → New repository (no README/.gitignore) |
| Link and push | `git remote add origin https://github.com/USER/REPO.git` → `git branch -M main` → `git push -u origin main` |
| Later changes | `git add .` → `git commit -m "Your message"` → `git push` |

---

## Troubleshooting

- **“remote origin already exists”**  
  Run: `git remote set-url origin https://github.com/YOUR_USERNAME/stock-ai-platform.git` then push again.

- **“Authentication failed” / “Support for password authentication was removed”**  
  Use a [Personal Access Token](https://github.com/settings/tokens) as the password when Git prompts.

- **“Permission denied (publickey)”**  
  You’re using SSH. Either switch to HTTPS (the `https://github.com/...` URL above) or set up [SSH keys with GitHub](https://docs.github.com/en/authentication/connecting-to-github-with-ssh).
