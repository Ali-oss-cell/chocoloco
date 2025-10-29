# 🚀 Push to GitHub - Commands

## ✅ **Pre-Push Checklist**

Before pushing, make sure:
- [x] `.env` file is in `.gitignore` (✅ Already configured)
- [x] `venv/` is in `.gitignore` (✅ Already configured)
- [x] `db.sqlite3` is in `.gitignore` (✅ Already configured)
- [x] Sensitive files are ignored

---

## 📋 **Commands to Run**

Run these commands **one by one** in your terminal:

### **1. Initialize Git (if not done)**

```bash
cd /home/ali/Desktop/projects/ecomarce_choco
git init
```

### **2. Add Remote Repository**

```bash
git remote add origin git@github.com:Ali-oss-cell/chocoloco.git
```

**Note:** If you get "remote origin already exists", run:
```bash
git remote set-url origin git@github.com:Ali-oss-cell/chocoloco.git
```

### **3. Stage All Files**

```bash
git add .
```

### **4. Check What Will Be Committed**

```bash
git status
```

**Verify:** Make sure `.env` and `venv/` are **NOT** listed!

### **5. Create Initial Commit**

```bash
git commit -m "Initial commit: Django e-commerce API with GraphQL, PostgreSQL, deployment configs"
```

### **6. Rename Branch to Main**

```bash
git branch -M main
```

### **7. Push to GitHub**

```bash
git push -u origin main
```

---

## 🔑 **SSH Key Setup (If Needed)**

If you get **authentication errors**, you need to set up SSH keys:

### **Check if SSH key exists:**

```bash
ls -la ~/.ssh/id_rsa.pub
```

### **If it doesn't exist, create one:**

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

### **Add SSH key to GitHub:**

1. Copy your public key:
```bash
cat ~/.ssh/id_rsa.pub
```

2. Go to GitHub → Settings → SSH and GPG keys → New SSH key
3. Paste the key and save

### **Test SSH connection:**

```bash
ssh -T git@github.com
```

---

## 🔒 **Security Check**

Before pushing, verify sensitive files are ignored:

```bash
# Check if .env is ignored
git check-ignore .env

# View what will be committed
git status

# List ignored files
git status --ignored
```

**IMPORTANT:** Never commit:
- ❌ `.env` file
- ❌ Database files
- ❌ Secret keys
- ❌ Virtual environment (`venv/`)

---

## ✅ **After Pushing**

Once pushed successfully:

1. **Verify on GitHub:**
   - Go to: https://github.com/Ali-oss-cell/chocoloco
   - Check all files are there
   - Verify `.env` is **NOT** visible

2. **Clone on Droplet:**
   ```bash
   cd /home/django
   git clone git@github.com:Ali-oss-cell/chocoloco.git ecomarce_choco
   ```

---

## 🐛 **Troubleshooting**

### **Error: "Permission denied (publickey)"**
→ Set up SSH keys (see above)

### **Error: "remote origin already exists"**
```bash
git remote remove origin
git remote add origin git@github.com:Ali-oss-cell/chocoloco.git
```

### **Error: "fatal: not a git repository"**
```bash
git init
```

### **Want to remove .env from git history (if accidentally committed)?**
```bash
git rm --cached .env
git commit -m "Remove .env from git"
git push
```

---

## 📝 **Your Commands Summary**

Here's the complete sequence:

```bash
cd /home/ali/Desktop/projects/ecomarce_choco
git init
git remote add origin git@github.com:Ali-oss-cell/chocoloco.git
git add .
git status  # Verify .env is NOT listed
git commit -m "Initial commit: Django e-commerce API with GraphQL, PostgreSQL, deployment configs"
git branch -M main
git push -u origin main
```

**That's it! 🚀**

