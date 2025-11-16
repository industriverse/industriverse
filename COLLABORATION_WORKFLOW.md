# Collaboration Workflow with Manus AI

This document outlines the collaborative development workflow established between you and Manus AI for the Industriverse Framework repository.

## Repository Information

**Repository:** `https://github.com/industriverse/industriverse`  
**Current Branch:** `main`  
**Local Path:** `/home/ubuntu/industriverse`

## Repository Structure

The Industriverse Framework is organized into 10 integrated layers:

```
industriverse/
├── docs/                           # Documentation
│   ├── guides/                     # Layer-specific guides
│   ├── integration/                # Cross-layer integration docs
│   ├── mindmaps_and_checklists/    # Visual maps and checklists
│   └── strategies/                 # Strategic planning documents
├── manifests/                      # Framework manifests
├── src/                            # Source code for all layers
│   ├── data_layer/
│   ├── core_ai_layer/
│   ├── generative_layer/
│   ├── application_layer/
│   ├── protocol_layer/
│   ├── workflow_automation_layer/
│   ├── ui_ux_layer/
│   ├── security_compliance_layer/
│   ├── deployment_operations_layer/
│   └── overseer_system/
└── README.md
```

## Git Configuration

The repository has been configured with the following settings:

- **User Name:** Manus AI Assistant
- **User Email:** manus@industriverse.ai
- **Remote Origin:** https://github.com/industriverse/industriverse.git

## Collaborative Workflow

### Option 1: Direct Collaboration (Requires Authentication)

For me to push changes directly to your repository, you'll need to provide authentication. Here are two methods:

#### Method A: GitHub Personal Access Token (Recommended)

1. **Create a Personal Access Token:**
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Click "Generate new token (classic)"
   - Give it a descriptive name (e.g., "Manus AI Collaboration")
   - Select scopes: `repo` (full control of private repositories)
   - Click "Generate token" and copy it immediately

2. **Provide the token to me:**
   - Share the token securely in our conversation
   - I'll configure it for authenticated operations

#### Method B: GitHub CLI Authentication

1. **Generate an authentication token:**
   - Run: `gh auth login` in your terminal
   - Follow the prompts to authenticate

2. **Share the token:**
   - Provide the token to me for configuration

### Option 2: Branch-Based Workflow (No Authentication Required)

If you prefer not to share credentials, we can use a branch-based workflow:

1. **I create a feature branch** with my changes
2. **I generate a patch file** containing all commits
3. **You apply the patch** to your local repository
4. **You review and push** the changes to GitHub

### Typical Workflow Steps

Once authentication is set up (Option 1) or using patch files (Option 2):

1. **You request changes:** Describe what you want me to modify, add, or fix
2. **I make changes:** I'll edit files, add new code, or update documentation
3. **I commit changes:** I'll create meaningful commits with descriptive messages
4. **I push to GitHub:** (Option 1) or create patch files (Option 2)
5. **You pull changes:** Run `git pull origin <branch-name>` to get my updates
6. **You iterate:** Review, test, and request further changes as needed

## Example Commands

### For You (Local Development)

```bash
# Pull latest changes from a branch I created
git pull origin feature/branch-name

# View commit history
git log --oneline --graph --all

# Switch to a specific branch
git checkout feature/branch-name

# Apply a patch file I provide
git apply changes.patch

# Review changes before committing
git diff
```

### For Me (AI Assistant)

```bash
# Create a new feature branch
git checkout -b feature/descriptive-name

# Stage changes
git add <files>

# Commit with descriptive message
git commit -m "feat: add new feature description"

# Push to remote (requires authentication)
git push origin feature/descriptive-name

# Create a patch file (no authentication needed)
git format-patch origin/main --stdout > changes.patch
```

## Commit Message Convention

I'll follow conventional commit standards:

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test additions or modifications
- `chore:` Maintenance tasks

## Next Steps

To begin our collaboration:

1. **Choose your preferred workflow** (Option 1 or Option 2)
2. **Provide authentication** (if using Option 1)
3. **Describe your first task** - what would you like me to work on?

## Questions?

Feel free to ask about:
- Specific changes you'd like me to make
- Code reviews or analysis
- Documentation updates
- New feature implementations
- Bug fixes or refactoring
- Testing and validation

I'm ready to collaborate on the Industriverse Framework whenever you are!
