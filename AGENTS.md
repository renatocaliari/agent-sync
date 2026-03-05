# LLM Foundation & Project Mandates

This file provides critical instructions for AI models (like Gemini, Claude, etc.) working on the `agent-sync` project.

## 🚀 Automatic Versioning (Hatch-VCS)

This project uses `hatch-vcs` for dynamic versioning based on Git Tags.

**Rules for LLMs:**
1.  **NEVER** hardcode version strings in `pyproject.toml` or `__init__.py`. 
2.  The `__init__.py` should use `importlib.metadata.version("agent-sync")` to read its version.
3.  **To Release a New Version**:
    -   Perform your code changes and commit.
    -   Determine the next semantic version (e.g., `v0.8.1`).
    -   Execute: `git tag vX.X.X`
    -   Execute: `git push origin vX.X.X`
    -   Create a GitHub Release using `gh release create`.

## 🏗️ Architecture Mandates

-   **Agent Registry**: New agent CLI support must be added to `src/agent_sync/agent_registry.yaml`, not hardcoded in Python.
-   **No Symlinks**: Always prefer `Native`, `Config`, or `Copy` methods. Do not re-introduce symlink fallbacks.
-   **UX/DX First**: CLI outputs must be categorized, visual (using Rich panels/tables), and provide clear guidance on errors.

## 📦 Distribution

-   Users update via `agent-sync update`. Ensure this command remains bulletproof and supports both `pipx` and `pip` (with `--break-system-packages` for macOS).
