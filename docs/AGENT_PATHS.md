# Paths de Configuração por Agent CLI

Este documento lista os paths exatos usados por cada agent CLI, baseados na documentação oficial.

---

## Opencode

**Documentação:** https://opencode.ai/docs/

### Paths

| Tipo | Path | Descrição |
|------|------|-----------|
| Config | `~/.config/opencode/opencode.json` | Configuração principal |
| Skills | `~/.config/opencode/skills/` | Skills globais |
| Tools | `~/.config/opencode/tools/` | Tools customizadas |
| Commands | `~/.config/opencode/commands/` | Comandos customizados |
| Plugins | `~/.config/opencode/plugins/` | Plugins |
| Modes | `~/.config/opencode/modes/` | Modes customizados |
| Themes | `~/.config/opencode/themes/` | Temas |
| Agents | `~/.config/opencode/agents/` | Agent configs |

### Projeto

No diretório do projeto: `.opencode/`

```
.opencode/
├── opencode.json
├── skills/
├── tools/
├── commands/
└── modes/
```

### Notas

- Nomes plurais são o padrão (`skills/`, `tools/`, `commands/`)
- Nomes singulares também funcionam para backwards compatibility
- Skills são arquivos `SKILL.md` dentro de subdiretórios

---

## Claude Code

**Documentação:** https://code.claude.com/docs/

### Paths

| Tipo | Path | Descrição |
|------|------|-----------|
| Config | `~/.claude/settings.json` | Configuração principal |
| Commands | `~/.claude/commands/` | Comandos/skills customizados |
| Worktrees | `<repo>/.claude/worktrees/` | Worktrees por repositório |

### Projeto

No diretório do projeto: `.claude/`

```
.claude/
├── settings.json
└── commands/
```

### Notas

- Settings podem ser carregados via `--settings ./settings.json`
- Comandos customizados são arquivos `.md` ou `.sh` no diretório `commands/`
- Worktrees são específicos por repositório

---

## Gemini CLI

**Documentação:** https://gemini-cli-docs.pages.dev/

### Paths

| Tipo | Path | Descrição |
|------|------|-----------|
| Config | `~/.gemini/settings.json` | Configuração do usuário |
| Project Config | `.gemini/settings.json` | Configuração do projeto |
| Tools | `.gemini/` | Scripts de tools customizadas |
| Sandbox | `.gemini/sandbox-*.sb` | Perfis de sandbox customizados |

### Sistema

| OS | Path |
|----|------|
| Linux | `/etc/gemini-cli/settings.json` |
| Windows | `C:\ProgramData\gemini-cli\settings.json` |
| macOS | `/Library/Application Support/GeminiCli/settings.json` |

### Projeto

```
.gemini/
├── settings.json
├── sandbox.Dockerfile
└── bin/
    ├── get_tools
    └── call_tool
```

### Notas

- Config do usuário sobrescreve config do sistema
- Config do projeto sobrescreve config do usuário
- Tools customizadas podem estar em `bin/` dentro de `.gemini/`

---

## Pi.dev

**Documentação:** https://github.com/badlogic/pi-mono

### Paths

| Tipo | Path | Descrição |
|------|------|-----------|
| Config | `~/.pi/settings.json` | Configuração global |
| Global Skills | `~/.pi/agent/skills/` | Skills globais |
| Global Skills | `~/.agents/skills/` | Skills compartilhadas |
| Project Skills | `.pi/skills/` | Skills do projeto |
| Project Skills | `.agents/skills/` | Skills do projeto (ancestors) |

### Projeto

```
.pi/
├── settings.json
└── skills/
    └── skill-name/
        └── SKILL.md
```

### Notas

- Skills são diretórios contendo um arquivo `SKILL.md`
- Pi.dev procura skills em múltiplos paths (do mais específico ao mais genérico)
- `~/.agents/skills/` é compartilhado com outros agents
- Skills de packages npm também são suportados via `package.json`

---

## Qwen Code

**Documentação:** https://qwenlm.github.io/qwen-code-docs/

### Paths

| Tipo | Path | Descrição |
|------|------|-----------|
| Config | `~/.qwen/settings.json` | Configuração do usuário |
| Skills | `~/.qwen/skills/` | Skills globais |
| Agents | `~/.qwen/agents/` | Agent configs |
| Project Config | `.qwen/settings.json` | Configuração do projeto |
| Project Skills | `.qwen/skills/` | Skills do projeto |

### Projeto

```
.qwen/
├── settings.json
├── skills/
│   └── skill-name/
│       └── SKILL.md
└── agents/
```

### Notas

- Skills são diretórios com arquivo `SKILL.md`
- Config é procurada do diretório atual até o root do git
- `--experimental-skills` flag habilita suporte a skills
- `~/.agents/skills/` também é suportado

---

## Global Skills (~/.agents/skills/)

Este diretório é **compartilhado** entre múltiplos agents:

| Agent | Suporta |
|-------|---------|
| Opencode | ✅ (via config) |
| Claude Code | ❌ |
| Gemini CLI | ❌ |
| Pi.dev | ✅ (nativo) |
| Qwen Code | ✅ (nativo) |

### Estrutura

```
~/.agents/skills/
├── skill-1/
│   └── SKILL.md
├── skill-2/
│   └── SKILL.md
└── skill-3/
    └── SKILL.md
```

### Uso no agent-sync

```bash
# Habilitar sync
agent-sync enable global-skills

# Adicionar skill
mkdir ~/.agents/skills/minha-skill
echo "# Minha Skill" > ~/.agents/skills/minha-skill/SKILL.md

# Sync
agent-sync push
```

---

## Resumo dos Paths no agent-sync

```python
# Opencode
config: ~/.config/opencode/opencode.json
skills: ~/.config/opencode/skills/

# Claude Code
config: ~/.claude/settings.json
skills: ~/.claude/commands/

# Gemini CLI
config: ~/.gemini/settings.json
skills: ~/.gemini/tools/

# Pi.dev
config: ~/.pi/settings.json
skills: ~/.pi/agent/skills/

# Qwen Code
config: ~/.qwen/settings.json
skills: ~/.qwen/skills/

# Global
skills: ~/.agents/skills/
```
