# ✅ Paths Verificados e Atualizados

## Resumo das Verificações

Os paths de configuração e skills para cada agent CLI foram verificados contra a documentação oficial e atualizados.

---

## Paths Atualizados

### Opencode ✅
- **Config:** `~/.config/opencode/opencode.json`
- **Skills:** `~/.config/opencode/skills/` (plural é o padrão)
- **Tools:** `~/.config/opencode/tools/`
- **Commands:** `~/.config/opencode/commands/`

**Fonte:** https://opencode.ai/docs/config/

---

### Claude Code ✅
- **Config:** `~/.claude/settings.json`
- **Commands:** `~/.claude/commands/`

**Fonte:** https://code.claude.com/docs/

---

### Gemini CLI ✅
- **Config:** `~/.gemini/settings.json`
- **Project Config:** `.gemini/settings.json`
- **Tools:** `.gemini/` (custom tool scripts)

**Fonte:** https://gemini-cli-docs.pages.dev/cli/configuration

---

### Pi.dev ✅
- **Config:** `~/.pi/settings.json`
- **Skills (global):** `~/.pi/agent/skills/`
- **Skills (shared):** `~/.agents/skills/` ← Suporte nativo
- **Skills (project):** `.pi/skills/`, `.agents/skills/`

**Fonte:** https://github.com/badlogic/pi-mono

---

### Qwen Code ✅
- **Config:** `~/.qwen/settings.json`
- **Skills (global):** `~/.qwen/skills/`
- **Skills (shared):** `~/.agents/skills/` ← Suporte nativo
- **Skills (project):** `.qwen/skills/`

**Fonte:** https://qwenlm.github.io/qwen-code-docs/

---

### Global Skills ✅
- **Path:** `~/.agents/skills/`
- **Suportado nativamente por:** Pi.dev, Qwen Code
- **Configurável para:** Opencode (via config)

---

## Mudanças no Código

### 1. `src/agent_sync/agents/__init__.py`

```python
# Paths atualizados por agent:

class OpencodeAgent:
    config_path = ~/.config/opencode/opencode.json
    skills_path = ~/.config/opencode/skills/

class ClaudeCodeAgent:
    config_dir = ~/.claude/
    config_path = ~/.claude/settings.json
    skills_path = ~/.claude/commands/

class GeminiCliAgent:
    config_dir = ~/.gemini/
    config_path = ~/.gemini/settings.json
    skills_path = ~/.gemini/tools/

class PiDevAgent:
    config_dir = ~/.pi/
    config_path = ~/.pi/settings.json
    skills_path = ~/.pi/agent/skills/
    _additional_skills_paths = [~/.agents/skills/]  # ← Novo!

class QwenCodeAgent:
    config_dir = ~/.qwen/
    config_path = ~/.qwen/settings.json
    skills_path = ~/.qwen/skills/
    _additional_skills_paths = [~/.agents/skills/]  # ← Novo!
```

### 2. Novo Método: `get_all_skills_paths()`

```python
def get_all_skills_paths(self) -> list[Path]:
    """Get all skills paths for this agent (some agents have multiple)."""
    paths = [self.skills_path]
    
    # Add agent-specific additional paths
    if hasattr(self, '_additional_skills_paths'):
        paths.extend(self._additional_skills_paths())
    
    return [p for p in paths if p.exists()]
```

### 3. `src/agent_sync/sync.py` Atualizado

Agora usa `get_all_skills_paths()` para:
- Copiar skills de múltiplos diretórios (quando aplicável)
- Evitar colisões de arquivos com prefixos únicos
- Restaurar skills no path primário do agent

---

## Tabela Resumo

| Agent | Config | Skills | Shared (~/.agents/skills/) |
|-------|--------|--------|---------------------------|
| opencode | `~/.config/opencode/opencode.json` | `~/.config/opencode/skills/` | ❌ |
| claude-code | `~/.claude/settings.json` | `~/.claude/commands/` | ❌ |
| gemini-cli | `~/.gemini/settings.json` | `~/.gemini/tools/` | ❌ |
| pi.dev | `~/.pi/settings.json` | `~/.pi/agent/skills/` | ✅ |
| qwen-code | `~/.qwen/settings.json` | `~/.qwen/skills/` | ✅ |
| global-skills | - | `~/.agents/skills/` | N/A |

---

## Documentação Adicional

- `docs/AGENT_PATHS.md` - Detalhes completos de cada agent
- `README.md` - Atualizado com paths corretos

---

## Testes

```bash
# Verificar paths
agent-sync agents

# Output esperado:
# opencode      ~/.config/opencode/opencode.json  ~/.config/opencode/skills/
# claude-code   ~/.claude/settings.json           ~/.claude/commands/
# gemini-cli    ~/.gemini/settings.json           ~/.gemini/tools/
# pi.dev        ~/.pi/settings.json               ~/.pi/agent/skills/
# qwen-code     ~/.qwen/settings.json             ~/.qwen/skills/
# global-skills -                                 ~/.agents/skills/
```

---

## Notas Importantes

1. **Pi.dev e Qwen Code** suportam nativamente `~/.agents/skills/`
2. **Opencode** usa plural (`skills/`, `tools/`, `commands/`) como padrão
3. **Claude Code** usa `commands/` para skills customizados
4. **Gemini CLI** usa `.gemini/` para tools e configs de projeto
5. **Todos os paths** foram verificados na documentação oficial
