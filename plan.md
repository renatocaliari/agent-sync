# Plano: Migrar Agents CLI para YAML e Remover Symlink Fallback

## Discovery

Este plano foi aprovado pelo usuário via Plannotator UI em 2026-03-05.

**Decisões confirmadas:**
1. Remover symlink fallback - Nova order: native → config → copy
2. Migrar agents para YAML registry
3. skills_method com override na config do usuário
4. Sempre usar `skills_dir` unificado

---

## Fase 1: Criar Registry YAML

### Task 1.1: Criar `agent_registry.yaml`
Arquivo: `src/agent_sync/agent_registry.yaml`

Criar registry com todos os agents. O schema deve suportar:
- `method`: native | config | copy
- `config_dir`: Path base da config
- `config_filename`: Nome do arquivo de config
- `skills_dir_name`: Nome da pasta de skills no agent
- `check`: Como verificar se o agent está instalado (ex: `binary: name` ou `path: exists`)
- `config_update` (opcional):
  - `path`: JSON path (ex: `skills.paths`)
  - `action`: append | set

Exemplo `opencode`:
```yaml
opencode:
  method: config
  config_dir: "~/.config/opencode"
  config_filename: "opencode.json"
  skills_dir_name: "skills"
  check:
    binary: "opencode"
  config_update:
    path: "skills.paths"
    action: append
```

Agents iniciais:
- opencode (config method)
- qwen-code (copy method)
- claude-code (copy method)
- gemini-cli (copy method)
- pi.dev (native method)
- global-skills (native method)

### Task 1.2: Criar `registry_loader.py`
... (rest of Task 1.2) ...

### Task 1.5: Validar Schema YAML
- Implementar validação básica para garantir que campos obrigatórios por `method` estejam presentes.

---

## Fase 2: Remover Symlink

... (Tasks 2.1 - 2.3) ...

### Task 2.4: Implementar `_apply_config_method()`
Arquivo: `src/agent_sync/skills.py`

Suportar atualização dinâmica via JSON:
- Carregar config do agent
- Navegar via dot-notation (ex: `skills.paths`)
- Aplicar `action` (append se for lista, set se for valor único)
- Salvar de volta

---

## Fase 3: Override de skills_method

### Task 3.1: Adicionar métodos em `config.py`
Arquivo: `src/agent_sync/config.py`

- `get_skills_method(agent_name)`
- `set_skills_method(agent_name, method)`

### Task 3.2: Usar override em `_configure_agent()`
- Ler config primeiro
- Se não tiver, usar default YAML
- Salvar método que funcionou

---

## Fase 4: CLI e Docs

### Task 4.1: Atualizar `agent-sync agents`
Arquivo: `src/agent_sync/cli.py`

Adicionar coluna "Skills Method"

### Task 4.2: Atualizar README
- Remover menções symlink
- Documentar arquitetura YAML
- Como adicionar agents

### Task 4.3: Criar `docs/adding-agents.md`
Guia de contribuição

---

## Arquivos

| Arquivo | Ação |
|---------|------|
| `agent_registry.yaml` | CRIAR |
| `registry_loader.py` | CRIAR |
| `agents/base.py` | REFAZER |
| `agents/__init__.py` | MODIFICAR |
| `skills.py` | MODIFICAR |
| `config.py` | MODIFICAR |
| `cli.py` | MODIFICAR |
| `README.md` | MODIFICAR |
| `docs/adding-agents.md` | CRIAR |

---

## Riscos

- Breaking change: manter imports antigos
- YAML inválido: validar schema
- Windows paths: usar pathlib