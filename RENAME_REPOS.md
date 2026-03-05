# How to Rename Your Repositories

## Your Current Repositories

| Old Name | New Name |
|----------|----------|
| `agent-sync-configs` | `agent-sync-private-configs` |
| `my-agent-skills` | `agent-sync-public-skills` |

---

## Method 1: GitHub Web UI (Recommended)

### Step 1: Rename on GitHub

1. Go to `https://github.com/YOUR_USERNAME/agent-sync-configs`
2. Click **Settings** tab
3. Scroll to **Danger Zone**
4. Click **Change repository name**
5. Enter new name: `agent-sync-private-configs`
6. Click **Rename**

Repeat for `my-agent-skills` → `agent-sync-public-skills`

### Step 2: Update Local Remote URLs

```bash
# Navigate to your local repos
cd ~/path/to/agent-sync-configs

# Update remote URL
git remote set-url origin https://github.com/YOUR_USERNAME/agent-sync-private-configs.git

# Verify
git remote -v

# Repeat for skills repo
cd ~/path/to/my-agent-skills
git remote set-url origin https://github.com/YOUR_USERNAME/agent-sync-public-skills.git
git remote -v
```

### Step 3: Update agent-sync Config

```bash
# Edit your agent-sync config
agent-sync config edit

# Update repo_url to:
# https://github.com/YOUR_USERNAME/agent-sync-private-configs.git
```

---

## Method 2: GitHub CLI (Fast)

```bash
# Rename private configs repo
gh repo rename YOUR_USERNAME/agent-sync-private-configs --yes

# Rename public skills repo  
gh repo rename YOUR_USERNAME/agent-sync-public-skills --yes

# Update local remotes
cd ~/path/to/agent-sync-configs
git remote set-url origin https://github.com/YOUR_USERNAME/agent-sync-private-configs.git

cd ~/path/to/my-agent-skills
git remote set-url origin https://github.com/YOUR_USERNAME/agent-sync-public-skills.git
```

---

## Method 3: Complete Script

```bash
#!/bin/bash

USERNAME="YOUR_USERNAME"

echo "Renaming repositories..."

# Rename on GitHub (requires gh CLI)
gh repo rename $USERNAME/agent-sync-private-configs --yes
gh repo rename $USERNAME/agent-sync-public-skills --yes

# Update local remotes
REPO1_PATH="$HOME/Developmet/agent-sync-configs"
REPO2_PATH="$HOME/Developmet/my-agent-skills"

if [ -d "$REPO1_PATH" ]; then
    cd "$REPO1_PATH"
    git remote set-url origin https://github.com/$USERNAME/agent-sync-private-configs.git
    echo "✓ Updated: agent-sync-configs"
fi

if [ -d "$REPO2_PATH" ]; then
    cd "$REPO2_PATH"
    git remote set-url origin https://github.com/$USERNAME/agent-sync-public-skills.git
    echo "✓ Updated: my-agent-skills"
fi

# Update agent-sync config
echo "Updating agent-sync config..."
agent-sync config edit

echo "Done! ✅"
```

---

## After Renaming

### 1. Test Private Configs

```bash
cd ~/path/to/agent-sync-private-configs
git pull
git push
agent-sync status
```

### 2. Test Public Skills

```bash
cd ~/path/to/agent-sync-public-skills
git pull
git push
```

### 3. Update Documentation

If you have the repo URLs documented anywhere, update them:
- README files
- Scripts
- CI/CD configurations
- Other machines

---

## GitHub Redirects

**Good news:** GitHub automatically creates redirects from old repo names!

- Old URL: `github.com/YOUR_USERNAME/agent-sync-configs`
- New URL: `github.com/YOUR_USERNAME/agent-sync-private-configs`

The old URL will redirect to the new one automatically.

**However:** Update your local remotes anyway for best practices!

---

## Troubleshooting

### "Repository not found" after rename

```bash
# Clear git cache
git remote prune origin

# Re-verify remote
git remote -v

# Re-clone if needed
git clone https://github.com/YOUR_USERNAME/agent-sync-private-configs.git
```

### agent-sync still shows old repo name

```bash
# Edit config manually
agent-sync config edit

# Or reset and re-link
agent-sync config reset
agent-sync link https://github.com/YOUR_USERNAME/agent-sync-private-configs.git
```

### GitHub CLI not installed

```bash
# macOS
brew install gh

# Authenticate
gh auth login
```
