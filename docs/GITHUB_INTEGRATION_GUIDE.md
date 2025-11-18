# GitHub Integration Guide
## Complete Repository Access and Branch Management

**Document Version:** 1.0.0  
**Last Updated:** November 18, 2025  
**Author:** Manus AI

---

## 🎯 Purpose

This document provides complete instructions for accessing the Industriverse GitHub repository, understanding the branch structure, and pulling all necessary commits to continue development from the current state.

---

## 📚 Table of Contents

1. [Repository Information](#repository-information)
2. [Branch Structure](#branch-structure)
3. [Cloning the Repository](#cloning-the-repository)
4. [Accessing Week 16 Code](#accessing-week-16-code)
5. [Understanding Commit History](#understanding-commit-history)
6. [Pulling Latest Changes](#pulling-latest-changes)
7. [Branch Management](#branch-management)
8. [Merge Strategy](#merge-strategy)
9. [Troubleshooting](#troubleshooting)

---

## 📦 Repository Information

### Primary Repository

**URL:** https://github.com/industriverse/industriverse  
**Owner:** industriverse  
**Project:** Capsule Pins - Industrial Intelligence Platform  
**License:** MIT (assumed - verify in repository)

### Repository Structure

The repository contains multiple project phases:

```
industriverse/
├── ar_vr/                    # Week 15: AR/VR Integration
├── capsule-pins-pwa/         # Week 16: Complete DAC Factory
├── docs/                     # Project-wide documentation
└── [other project directories]
```

### Key Branches

The project uses feature branches for development:

| Branch Name | Purpose | Status | Last Commit |
|-------------|---------|--------|-------------|
| `main` | Production-ready code | Stable | Week 16 complete |
| `claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11` | Week 15-16 development | Active | Latest work |
| `develop` | Integration branch | Active | Ongoing |

**Primary development branch for Week 16:**  
`claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11`

---

## 🌿 Branch Structure

### Understanding the Branch Naming

The branch `claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11` follows this pattern:

- **Prefix:** `claude/` - Indicates AI-assisted development
- **Feature:** `refine-discovery-loop` - Feature being developed
- **ID:** `018RD2yViTXaCGCEqpyRtt11` - Unique identifier

### Branch Hierarchy

```
main (production)
  ↓
develop (integration)
  ↓
claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11 (feature)
```

### Commit Flow

Development flows from feature branches → develop → main:

1. **Feature branches** - Active development
2. **Develop branch** - Integration testing
3. **Main branch** - Production releases

---

## 📥 Cloning the Repository

### Method 1: HTTPS (Recommended for Read-Only)

```bash
# Clone the repository
git clone https://github.com/industriverse/industriverse.git

# Navigate to the project
cd industriverse

# Verify clone
git status
git branch -a
```

### Method 2: SSH (Recommended for Contributors)

```bash
# Set up SSH key (if not already done)
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub  # Add this to GitHub Settings → SSH Keys

# Clone with SSH
git clone git@github.com:industriverse/industriverse.git

# Navigate to the project
cd industriverse

# Verify clone
git status
git branch -a
```

### Method 3: GitHub CLI

```bash
# Install GitHub CLI (if not already installed)
# macOS: brew install gh
# Linux: See https://cli.github.com/manual/installation

# Authenticate
gh auth login

# Clone repository
gh repo clone industriverse/industriverse

# Navigate to the project
cd industriverse
```

---

## 🔍 Accessing Week 16 Code

### Step 1: List All Branches

```bash
# View local branches
git branch

# View all branches (local + remote)
git branch -a

# Search for Week 16 branch
git branch -a | grep claude
```

**Expected output:**
```
* main
  remotes/origin/HEAD -> origin/main
  remotes/origin/claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11
  remotes/origin/develop
  remotes/origin/main
```

### Step 2: Checkout Week 16 Branch

```bash
# Checkout the Week 16 development branch
git checkout claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11

# Verify you're on the correct branch
git branch
# Should show: * claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11

# View latest commits
git log --oneline -10
```

### Step 3: Navigate to Capsule Pins PWA

```bash
# Navigate to the Week 16 project directory
cd capsule-pins-pwa

# List contents
ls -la

# Verify key directories exist
ls -la client/src/components/ar-vr/
ls -la server/adapters/
ls -la docs/
```

### Step 4: Verify Week 16 Components

```bash
# Check for Week 16 completion report
cat docs/WEEK16_COMPLETION_REPORT.md | head -50

# Check for AR/VR components
ls -la client/src/components/ar-vr/

# Check for sensor adapters
ls -la server/adapters/

# Check for deployment files
ls -la docker-compose.yml k8s/
```

---

## 📜 Understanding Commit History

### View Recent Commits

```bash
# View last 20 commits
git log --oneline -20

# View commits with graph
git log --oneline --graph --all --decorate -20

# View commits by author
git log --author="Manus" --oneline -20

# View commits in date range
git log --since="2025-11-01" --until="2025-11-18" --oneline
```

### Key Commits for Week 16

Based on the technical context, these are the critical commits:

| Commit Hash | Description | Date |
|-------------|-------------|------|
| `cc6ef42` | Week 15 completion report + test suite | Week 15 |
| `29dbdc4` | TouchDesigner integration | Week 15 |
| `5bd970f` | MediaPipe integration | Week 15 |
| `fadc981` | AR/VR interaction system | Week 15 |
| `d20c443` | Reall3DViewer integration | Week 15 |
| `ff38da3` | Shadow Twin to 3DGS pipeline | Week 15 |
| `[latest]` | Week 16 DAC Factory completion | Week 16 |

### View Specific Commit Details

```bash
# View commit details
git show cc6ef42

# View files changed in commit
git show --name-only cc6ef42

# View diff for specific file
git show cc6ef42:ar_vr/WEEK15_COMPLETION_REPORT.md
```

---

## 🔄 Pulling Latest Changes

### Update Your Local Repository

```bash
# Ensure you're on the correct branch
git checkout claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11

# Fetch all remote changes
git fetch origin

# Pull latest changes
git pull origin claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11

# Verify you have the latest code
git log --oneline -5
```

### Handling Merge Conflicts

If you encounter merge conflicts:

```bash
# View conflicted files
git status

# Open conflicted file and resolve
# Look for markers: <<<<<<<, =======, >>>>>>>

# After resolving, mark as resolved
git add <file>

# Complete the merge
git commit -m "Merge: resolved conflicts in <file>"
```

### Pulling All Branches

```bash
# Fetch all branches
git fetch --all

# List all branches
git branch -a

# Checkout and pull each branch
git checkout main
git pull origin main

git checkout develop
git pull origin develop

git checkout claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11
git pull origin claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11
```

---

## 🌿 Branch Management

### Creating a New Feature Branch

```bash
# Ensure you're on the latest Week 16 branch
git checkout claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11
git pull origin claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11

# Create new feature branch
git checkout -b feat/your-feature-name

# Verify branch created
git branch
```

### Naming Conventions

Follow these conventions for branch names:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feat/` | New feature | `feat/database-integration` |
| `fix/` | Bug fix | `fix/websocket-timeout` |
| `docs/` | Documentation | `docs/update-deployment-guide` |
| `refactor/` | Code refactoring | `refactor/sensor-adapters` |
| `test/` | Adding tests | `test/ar-vr-gestures` |
| `chore/` | Maintenance | `chore/update-dependencies` |

### Pushing Your Branch

```bash
# Add and commit changes
git add .
git commit -m "feat(scope): description"

# Push to remote
git push origin feat/your-feature-name

# Create pull request on GitHub
gh pr create --title "Feature: Your Feature Name" --body "Description"
```

---

## 🔀 Merge Strategy

### Pull Request Workflow

1. **Create feature branch** from latest Week 16 branch
2. **Make changes** and commit regularly
3. **Push branch** to remote
4. **Create Pull Request** on GitHub
5. **Code review** by team
6. **Merge** into development branch

### Merging Feature Branch

```bash
# Ensure your branch is up to date
git checkout feat/your-feature-name
git pull origin claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11
git rebase claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11

# Push rebased branch
git push origin feat/your-feature-name --force-with-lease

# Merge via GitHub Pull Request (recommended)
# OR merge locally:
git checkout claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11
git merge --no-ff feat/your-feature-name
git push origin claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11
```

### Merge Commit Message

Follow Conventional Commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Example:**
```
feat(database): integrate PostgreSQL for capsule persistence

- Added database schema with 6 tables
- Implemented CRUD operations for capsules
- Added connection pooling and error handling
- Updated environment configuration

Closes #123
```

---

## 🐛 Troubleshooting

### Issue: "Permission denied (publickey)"

**Cause:** SSH key not set up or not added to GitHub.

**Solution:**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH and GPG keys → New SSH key

# Test connection
ssh -T git@github.com
```

### Issue: "fatal: not a git repository"

**Cause:** Not in a Git repository directory.

**Solution:**
```bash
# Navigate to repository
cd /path/to/industriverse

# Or clone if not yet cloned
git clone https://github.com/industriverse/industriverse.git
cd industriverse
```

### Issue: "error: Your local changes would be overwritten by merge"

**Cause:** Uncommitted local changes conflict with remote changes.

**Solution:**
```bash
# Option 1: Stash changes temporarily
git stash
git pull
git stash pop

# Option 2: Commit changes
git add .
git commit -m "WIP: local changes"
git pull

# Option 3: Discard local changes (WARNING: loses changes)
git reset --hard HEAD
git pull
```

### Issue: "fatal: refusing to merge unrelated histories"

**Cause:** Trying to merge branches with no common ancestor.

**Solution:**
```bash
# Allow unrelated histories (use with caution)
git pull origin <branch> --allow-unrelated-histories
```

### Issue: Branch Not Found

**Cause:** Branch name misspelled or not fetched.

**Solution:**
```bash
# Fetch all branches
git fetch --all

# List all branches
git branch -a

# Checkout correct branch (copy exact name)
git checkout claude/refine-discovery-loop-018RD2yViTXaCGCEqpyRtt11
```

---

## 📋 Quick Reference Commands

### Essential Git Commands

```bash
# Clone repository
git clone https://github.com/industriverse/industriverse.git

# View branches
git branch -a

# Checkout branch
git checkout <branch-name>

# Pull latest changes
git pull origin <branch-name>

# Create new branch
git checkout -b feat/new-feature

# Stage changes
git add .

# Commit changes
git commit -m "feat(scope): description"

# Push changes
git push origin <branch-name>

# View commit history
git log --oneline -20

# View status
git status

# View diff
git diff
```

### GitHub CLI Commands

```bash
# Clone repository
gh repo clone industriverse/industriverse

# Create pull request
gh pr create --title "Title" --body "Description"

# View pull requests
gh pr list

# Checkout pull request
gh pr checkout <number>

# View issues
gh issue list

# Create issue
gh issue create --title "Title" --body "Description"
```

---

## 🎯 Next Steps After Cloning

1. **Install dependencies:**
   ```bash
   cd capsule-pins-pwa
   pnpm install
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env
   nano .env  # Edit with your configuration
   ```

3. **Initialize database:**
   ```bash
   pnpm db:push
   ```

4. **Run development server:**
   ```bash
   pnpm dev
   ```

5. **Read documentation:**
   - `docs/AI_ENHANCEMENT_DIRECTIVES.md`
   - `docs/WEEK16_COMPLETION_REPORT.md`
   - `QUICKSTART_FOR_AI_AGENTS.md`

---

## 📞 Support

### Resources

- **GitHub Repository:** https://github.com/industriverse/industriverse
- **Issues:** https://github.com/industriverse/industriverse/issues
- **Pull Requests:** https://github.com/industriverse/industriverse/pulls
- **Documentation:** https://github.com/industriverse/industriverse/tree/main/docs

### Getting Help

1. **Search existing issues:** https://github.com/industriverse/industriverse/issues
2. **Create new issue:** Use issue templates
3. **Ask in discussions:** https://github.com/industriverse/industriverse/discussions
4. **Contact maintainers:** Via GitHub or project channels

---

## 📝 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2025-11-18 | Manus AI | Initial release |

---

**Document End**

For questions about GitHub integration, create an issue or refer to the official Git documentation: https://git-scm.com/doc
