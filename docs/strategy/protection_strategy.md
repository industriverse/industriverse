# Industriverse Confidential Protection Strategy
**Confidential - Internal Strategy**

## 1. The "Black Box" Philosophy
While we patent the *architecture* and *interfaces*, the *implementation details* (the "Secret Sauce") remain Confidential Information. This includes specific hyperparameters, training datasets, and complex heuristic logic.

## 2. Repository Architecture (The Split)
We will migrate from a single monolithic repo to a tiered structure:

### Tier 1: Public Repo (`industriverse-core`)
*   **Visibility**: Public (Open Source / Source Available)
*   **Content**:
    *   Interfaces & Abstract Base Classes (`src/core/interfaces`)
    *   Capsule Protocol Definitions (`src/core/capsule_uri.py`)
    *   CLI Tools (`dac-builder`)
    *   Demo Visualizations (Frontend)
    *   **Mock Implementations** of sensitive services.

### Tier 2: Private Repo (`industriverse-engine`)
*   **Visibility**: Private (Internal Team Only)
*   **Content**:
    *   Real TNN & EBDM Implementations (`src/tnn`, `src/generative_layer`)
    *   Energy Prior Library (`src/ebm_lib/priors`)
    *   Discovery Loop Logic (`src/unified_loop`)
    *   AI Shield Logic (`src/ai_safety`)

## 3. Obfuscation & Deployment
For client deployments (On-Premise or Private Cloud):
*   **Compiled Binaries**: Distribute the "Engine" as compiled Python wheels (`.whl`) or binary executables (using PyInstaller/Nuitka) to prevent easy reverse-engineering.
*   **API-First**: Whenever possible, host the Engine as a SaaS API, so the code never leaves our infrastructure.
*   **Code Obfuscation**: Use tools like `pyarmor` for critical modules if source distribution is absolutely necessary.

## 4. Access Control
*   **Role-Based Access**:
    *   **Contractors**: Access only to specific modules or the Public Repo.
    *   **Core Team**: Full access to Private Repo.
*   **Environment Isolation**: Development, Staging, and Production environments are strictly separated. Keys and secrets are managed via a secure vault (e.g., HashiCorp Vault).

## 5. "Poison Pill" / License Check
*   Embed a license check mechanism in the Engine that requires a valid, periodically refreshed cryptographic token to run. This prevents unauthorized usage if the code leaks.
