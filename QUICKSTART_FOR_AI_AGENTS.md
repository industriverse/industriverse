# Quickstart Guide for AI Agents
## Pick Up Development from GitHub

**Target Audience:** Claude Code, Manus AI, or any AI development assistant  
**Time to Complete:** 5-10 minutes  
**Last Updated:** November 18, 2025

---

## 🎯 Mission

You are an AI agent tasked with continuing development of the **Industriverse Capsule Pins** project. This guide will help you:

1. Clone the repository from GitHub
2. Understand the current state (Week 16 complete)
3. Identify the next enhancement priorities
4. Start contributing immediately

---

## ⚡ 60-Second Onboarding

```bash
# 1. Clone repository
git clone https://github.com/industriverse/industriverse.git
cd industriverse/capsule-pins-pwa

# 2. Read completion status
cat docs/WEEK16_COMPLETION_REPORT.md | head -50

# 3. Check pending work
cat todo.md | grep "\[ \]"

# 4. Install and run
pnpm install && pnpm dev
```

**That's it!** The app is now running at http://localhost:3000

---

## 📚 Essential Reading (In Order)

Read these documents to understand the complete context:

### 1. **AI_ENHANCEMENT_DIRECTIVES.md** (This Directory)
**Purpose:** Complete guide for AI agents  
**Read time:** 15 minutes  
**Key sections:**
- Repository structure
- Complete architecture overview
- Enhancement priorities
- Development standards

### 2. **WEEK16_COMPLETION_REPORT.md** (docs/)
**Purpose:** What was delivered in Week 16  
**Read time:** 10 minutes  
**Key sections:**
- Backend infrastructure
- AR/VR components
- Production deployment
- Known issues

### 3. **WEEK16_DAC_FACTORY_ARCHITECTURE.md** (docs/)
**Purpose:** Technical architecture deep dive  
**Read time:** 15 minutes  
**Key sections:**
- Data flow architecture
- Shadow Twin Consensus Network
- Integration points

### 4. **todo.md** (Root Directory)
**Purpose:** Current task tracking  
**Read time:** 2 minutes  
**Look for:** `[ ]` (pending tasks) vs `[x]` (completed tasks)

---

## 🏗️ Project Context

### What Is This Project?

**Capsule Pins** is an industrial intelligence platform that transforms factory sensor data into actionable "capsules" (alerts/insights) delivered across multiple platforms:

- **Web (PWA)** - Progressive Web App for browsers
- **Mobile (Android)** - Native app for factory floor workers
- **Desktop (Electron)** - Cross-platform desktop app for operators
- **AR/VR** - Immersive 3D visualization with gesture controls

### The Vertical Stack

The project is built on a complete vertical stack:

```
Remix Lab → A2A → MCP → Thermodynamic Computing → DAC Factory
```

Each layer provides specific capabilities:
- **Remix Lab:** Cognitive architecture (AI reasoning)
- **A2A:** Agent-to-agent communication
- **MCP:** Model Context Protocol (cross-platform state)
- **Thermodynamic Computing:** Energy-efficient computation
- **DAC Factory:** Data-as-a-Capsule transformation

### Week 16 Completion State

✅ **Delivered:**
- Sensor ingestion pipeline (MQTT, OPC-UA)
- Capsule creation engine with rules
- Shadow Twin Consensus validation
- AR/VR gesture controls (MediaPipe)
- TouchDesigner generative visualizations
- Production deployment (Docker + Kubernetes)
- Comprehensive documentation

⚠️ **Pending:**
- Database setup (MySQL/PostgreSQL)
- Real sensor integration testing
- OPC-UA TypeScript type fixes
- Production cloud deployment

---

## 🎯 Your First Task

### Option 1: Fix Database Integration (Recommended)

**Why:** Enables full data persistence and removes console errors.

**Steps:**
1. Read `docs/DEPLOYMENT.md` section "Database Setup"
2. Choose PostgreSQL or SQLite
3. Update `.env` with `DATABASE_URL`
4. Run `pnpm db:push` to initialize schema
5. Restart server: `pnpm dev`
6. Verify: No database errors in console

**Success criteria:**
- ✅ No "ECONNREFUSED" errors
- ✅ Capsules persist across restarts
- ✅ WebSocket shows "connected" status

### Option 2: Connect Real Sensors

**Why:** Test end-to-end data flow with actual factory hardware.

**Steps:**
1. Read `docs/ADMIN_MANUAL.md` section "Sensor Configuration"
2. Set up MQTT broker (Mosquitto or cloud service)
3. Configure sensor topics in `server/adapters/MQTTAdapter.ts`
4. Connect temperature/pressure/vibration sensors
5. Verify capsules created from real data

**Success criteria:**
- ✅ Real sensor data in logs
- ✅ Capsules created automatically
- ✅ Shadow Twin consensus validates capsules

### Option 3: Fix OPC-UA Types

**Why:** Remove TypeScript errors (currently 22 errors).

**Steps:**
1. Open `server/adapters/OPCUAAdapter.ts`
2. Install correct types: `pnpm add -D @types/node-opcua`
3. Fix type annotations (see errors in console)
4. Test with real OPC-UA PLC

**Success criteria:**
- ✅ Zero TypeScript errors
- ✅ OPC-UA connection successful
- ✅ PLC data ingested

---

## 🔍 Understanding the Codebase

### Key Directories

```
capsule-pins-pwa/
├── client/src/              # Frontend (React + TypeScript)
│   ├── components/ar-vr/    # AR/VR components (Week 15-16)
│   ├── pages/               # Route pages
│   └── services/            # API clients
│
├── server/                  # Backend (Node.js + Express)
│   ├── adapters/            # Sensor adapters (MQTT, OPC-UA)
│   ├── services/            # Business logic
│   └── websocket/           # Real-time gateway
│
├── docs/                    # Documentation
│   ├── AI_ENHANCEMENT_DIRECTIVES.md  # Complete AI guide
│   ├── WEEK16_COMPLETION_REPORT.md   # Week 16 summary
│   └── DEPLOYMENT.md                 # Deployment instructions
│
├── k8s/                     # Kubernetes manifests
├── docker-compose.yml       # Docker stack
└── todo.md                  # Task tracking
```

### Key Files to Understand

| File | Purpose | Lines | Priority |
|------|---------|-------|----------|
| `server/services/CapsuleCreationEngine.ts` | Core capsule logic | ~400 | 🔴 High |
| `server/adapters/MQTTAdapter.ts` | MQTT sensor integration | ~300 | 🔴 High |
| `client/src/components/ar-vr/MediaPipeHandsController.tsx` | Gesture controls | ~600 | 🟡 Medium |
| `client/src/components/ar-vr/TouchDesignerVisualizer.tsx` | Generative art | ~700 | 🟡 Medium |
| `client/src/services/ShadowTwinConsensusClient.ts` | Consensus validation | ~400 | 🔴 High |
| `server/websocket/CapsuleGatewayServer.ts` | WebSocket server | ~300 | 🔴 High |

### Data Flow

```
Sensor (MQTT/OPC-UA)
  ↓
MQTTAdapter / OPCUAAdapter
  ↓
SensorIngestionService
  ↓
CapsuleCreationEngine (applies rules)
  ↓
Shadow Twin Consensus (validates)
  ↓
CapsuleGatewayServer (broadcasts via WebSocket)
  ↓
Frontend (PWA / Android / Desktop / AR/VR)
```

---

## 🚀 Development Workflow

### 1. Pick a Task

Check `todo.md` for pending tasks:
```bash
cat todo.md | grep "\[ \]"
```

Or choose from Enhancement Priorities in `AI_ENHANCEMENT_DIRECTIVES.md`.

### 2. Create a Branch

```bash
git checkout -b feat/your-feature-name
```

### 3. Make Changes

Follow development standards in `AI_ENHANCEMENT_DIRECTIVES.md`:
- TypeScript strict mode
- ESLint + Prettier
- Functional components (React)
- Async/await over promises

### 4. Test Your Changes

```bash
# Run development server
pnpm dev

# Run tests (if available)
pnpm test

# Check TypeScript
pnpm type-check

# Lint code
pnpm lint
```

### 5. Commit Changes

Follow Conventional Commits:
```bash
git add .
git commit -m "feat(scope): add feature description"
```

Examples:
```
feat(ar-vr): add voice command support for hands-free operation
fix(websocket): resolve connection timeout on slow networks
docs(readme): update deployment instructions for Kubernetes
```

### 6. Push and Create PR

```bash
git push origin feat/your-feature-name
```

Then create a Pull Request on GitHub.

---

## 🔧 Common Commands

### Development

```bash
# Install dependencies
pnpm install

# Run development server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start

# Run tests
pnpm test

# Type check
pnpm type-check

# Lint code
pnpm lint

# Format code
pnpm format
```

### Database

```bash
# Initialize database schema
pnpm db:push

# Generate database migration
pnpm db:generate

# Run database migrations
pnpm db:migrate

# Open database studio (GUI)
pnpm db:studio
```

### Docker

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Rebuild containers
docker-compose up -d --build
```

### Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/deployment.yaml

# Check pods
kubectl get pods

# View logs
kubectl logs -f deployment/capsule-pins-app

# Port forward
kubectl port-forward svc/capsule-pins-app 3000:3000
```

---

## 🐛 Troubleshooting

### Issue: "ECONNREFUSED" Database Errors

**Solution:**
```bash
# Option 1: Use SQLite (simplest)
echo "DATABASE_URL=file:./dev.db" >> .env
pnpm db:push
pnpm dev

# Option 2: Start PostgreSQL with Docker
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=capsule_pins \
  -p 5432:5432 postgres:15
echo "DATABASE_URL=postgresql://postgres:password@localhost:5432/capsule_pins" >> .env
pnpm db:push
pnpm dev
```

### Issue: "Unable to reach server" WebSocket Error

**Solution:**
1. Ensure server is running: `pnpm dev`
2. Check WebSocket URL in `.env`
3. Verify no firewall blocking port 3000

### Issue: AR/VR Gestures Not Working

**Solution:**
1. Grant camera permission in browser
2. Use HTTPS (MediaPipe requires secure context)
3. Use Chrome/Edge (best compatibility)

### Issue: TypeScript Errors

**Solution:**
```bash
# Install missing types
pnpm add -D @types/node-opcua

# Check for errors
pnpm type-check

# Fix automatically (if possible)
pnpm lint --fix
```

---

## 📞 Getting Help

### 1. Check Documentation

- `docs/AI_ENHANCEMENT_DIRECTIVES.md` - Complete AI guide
- `docs/DEPLOYMENT.md` - Deployment instructions
- `docs/OPERATOR_GUIDE.md` - User guide
- `docs/ADMIN_MANUAL.md` - Admin guide

### 2. Search Issues

https://github.com/industriverse/industriverse/issues

### 3. Create New Issue

Use issue templates and include:
- Error logs
- Expected vs actual behavior
- Reproduction steps

---

## ✅ Success Checklist

Before considering your work complete:

- [ ] Code follows project standards (see `AI_ENHANCEMENT_DIRECTIVES.md`)
- [ ] TypeScript compiles without errors (`pnpm type-check`)
- [ ] Linting passes (`pnpm lint`)
- [ ] Tests pass (if applicable) (`pnpm test`)
- [ ] Documentation updated (if adding features)
- [ ] Commit messages follow Conventional Commits
- [ ] Changes tested locally (`pnpm dev`)
- [ ] No console errors in browser
- [ ] Performance maintained (60 FPS rendering, <50ms latency)

---

## 🎯 Next Steps

1. **Read this document** (5 minutes) ✅
2. **Read `AI_ENHANCEMENT_DIRECTIVES.md`** (15 minutes)
3. **Read `WEEK16_COMPLETION_REPORT.md`** (10 minutes)
4. **Choose your first task** (from Enhancement Priorities)
5. **Start coding!** 🚀

---

## 📝 Quick Reference

| Resource | Purpose | Location |
|----------|---------|----------|
| **Complete AI Guide** | Full documentation for AI agents | `docs/AI_ENHANCEMENT_DIRECTIVES.md` |
| **Week 16 Report** | What was delivered | `docs/WEEK16_COMPLETION_REPORT.md` |
| **Architecture** | Technical deep dive | `docs/WEEK16_DAC_FACTORY_ARCHITECTURE.md` |
| **Deployment** | How to deploy | `docs/DEPLOYMENT.md` |
| **Operator Guide** | User documentation | `docs/OPERATOR_GUIDE.md` |
| **Admin Manual** | IT/DevOps guide | `docs/ADMIN_MANUAL.md` |
| **Task Tracking** | Pending work | `todo.md` |

---

**Welcome aboard! Let's build something amazing together.** 🚀

---

**Document Version:** 1.0.0  
**Author:** Manus AI  
**Last Updated:** November 18, 2025
