# 🔄 agent-sync

**Sincronize configurações e skills entre múltiplos AI agents CLI**

Suporta: **opencode**, **claude-code**, **gemini-cli**, **pi.dev**, **qwen-code**

---

## 🎯 O que faz

`agent-sync` é um CLI unificado que sincroniza suas configurações, skills e prompts entre diferentes AI agents e múltiplas máquinas, via repositório GitHub privado.

### Funcionalidades

| Feature | Descrição |
|---------|-----------|
| **Multi-Agent** | Suporte a 5+ agents (opencode, claude, gemini, pi, qwen) |
| **Config Sync** | Sincroniza configs, modes, tools, prompts |
| **Skills Sync** | Compartilha skills entre agents e máquinas |
| **Secrets Safe** | Scrubbing automático, env vars, overrides locais |
| **GitHub-Based** | Usa repositório privado para sync |
| **Agent-Native** | Skills que rodam dentro de cada agent |

---

## 🚀 Quick Start

### Pré-requisitos

```bash
# Instalar Git
brew install git

# Instalar GitHub CLI
brew install gh
gh auth login

# Instalar agent-sync
pip install agent-sync
```

### Primeira Máquina - Setup Interativo (Recomendado)

```bash
# Executar wizard de setup
agent-sync setup

# O wizard vai automaticamente:
# 1. Detectar agents instalados
# 2. Centralizar skills existentes → ~/.agents/skills/
# 3. Configurar agents para usar global skills
# 4. Criar repositório GitHub
# 5. Mostrar resumo detalhado

# Enviar configs para GitHub
agent-sync push
```

### Máquinas Adicionais

```bash
# Link ao repositório existente
agent-sync link https://github.com/username/my-agent-configs.git

# Baixar configs e skills
agent-sync pull
```

### Comandos Úteis

```bash
# Centralizar skills existentes
agent-sync skills centralize

# Ver configuração
agent-sync config show

# Reconfigurar
agent-sync setup
```

```bash
# Linkar ao repositório existente
agent-sync link https://github.com/username/my-agent-configs.git

# Baixar configs
agent-sync pull

# Verificar status
agent-sync status
```

---

## 📖 Comandos

### Comandos Principais

```bash
# Setup e Configuração
agent-sync setup           # Setup interativo (pode reconfigurar a qualquer momento)
agent-sync config show     # Ver configuração atual
agent-sync config edit     # Editar arquivo de configuração
agent-sync config reset    # Resetar para defaults (mantém repo)

# Inicializar e Linkar
agent-sync init            # Criar novo repositório (com wizard se não configurado)
agent-sync link <url>      # Linkar a repositório existente

# Sync
agent-sync pull            # Baixar e aplicar configs remotas
agent-sync push            # Commitar e enviar mudanças locais
agent-sync status          # Mostrar status do sync

# Agents
agent-sync agents          # Listar agents e status
agent-sync enable <name>   # Habilitar sync de um agent
agent-sync disable <name>  # Desabilitar sync de um agent

# Secrets
agent-sync secrets enable  # Habilitar sync de secrets
agent-sync secrets disable # Desabilitar sync de secrets
```

### Reconfigurar

Já está usando e quer mudar algo? Veja [docs/RECONFIGURATION.md](docs/RECONFIGURATION.md)

```bash
# Reconfigurar com wizard
agent-sync setup

# Ou comandos rápidos
agent-sync enable gemini-cli
agent-sync disable claude-code

# Ver configuração
agent-sync config show
```

### Opções do `init`

```bash
agent-sync init \
  --name my-configs \
  --private \
  --agents opencode claude-code qwen-code
```

| Opção | Descrição |
|-------|-----------|
| `--name` | Nome do repositório |
| `--private/--public` | Visibilidade do repo (default: private) |
| `--agents` | Agents para sync (pode repetir) |

### Gerenciamento de Agents

```bash
# Listar todos os agents
agent-sync agents

# Habilitar sync de um agent específico
agent-sync enable opencode

# Desabilitar sync de um agent
agent-sync disable claude-code

# Habilitar global skills (~/.agents/skills)
agent-sync enable global-skills
```

### Gerenciamento de Secrets

```bash
# Habilitar sync de secrets
agent-sync secrets enable

# Habilitar incluindo MCP secrets
agent-sync secrets enable --include-mcp

# Desabilitar sync de secrets
agent-sync secrets disable
```

### Outros Comandos

```bash
# Listar agents suportados
agent-sync agents

# Gerar config inicial
agent-sync generate-config

# Ver versão
agent-sync --version
```

---

## 🔐 Segurança e Secrets

### Como funciona

1. **Scrubbing Automático**: Secrets são detectados e substituídos por placeholders `{{env:VAR_NAME}}`
2. **Env Local**: Valores reais ficam em `~/.config/agent-sync/.env` (NUNCA syncado)
3. **Overrides Locais**: Configs específicas por máquina em `~/.config/agent-sync/overrides.yaml`

### O que é protegido

- API keys (`api_key`, `token`, `secret`)
- Credenciais MCP
- Auth tokens
- Senhas

### Exemplo

**Config syncada:**
```json
{
  "mcpServers": {
    "github": {
      "env": {
        "GITHUB_TOKEN": "{{env:AGENT_SYNC_GITHUB_TOKEN}}"
      }
    }
  }
}
```

**Env local** (`~/.config/agent-sync/.env`):
```bash
AGENT_SYNC_GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

---

## 📁 Estrutura de Arquivos

### No seu computador

```
~/.config/agent-sync/
├── config.yaml              # Configuração principal
├── overrides.yaml           # Overrides locais (não syncado)
└── .env                     # Secrets (não syncado)

~/.local/share/agent-sync/
└── repo/                    # Clone do repositório
```

### No repositório GitHub

```
my-agent-configs/
├── configs/
│   ├── opencode/
│   ├── claude-code/
│   ├── gemini-cli/
│   ├── pi.dev/
│   └── qwen-code/
├── skills/
│   ├── opencode/
│   ├── claude-code/
│   └── ...
├── prompts/                 # Opcional
├── .gitignore
└── README.md
```

---

## 🤖 Agents Suportados

| Agent | Config Path | Skills/Commands Path | Docs |
|-------|-------------|---------------------|------|
| **opencode** | `~/.config/opencode/opencode.json` | `~/.config/opencode/skills/` | [Docs](https://opencode.ai/docs/) |
| **claude-code** | `~/.claude/settings.json` | `~/.claude/commands/` | [Docs](https://code.claude.com/docs/) |
| **gemini-cli** | `~/.gemini/settings.json` | `~/.gemini/tools/` | [Docs](https://gemini-cli-docs.pages.dev/) |
| **pi.dev** | `~/.pi/settings.json` | `~/.pi/agent/skills/` | [Docs](https://github.com/badlogic/pi-mono) |
| **qwen-code** | `~/.qwen/settings.json` | `~/.qwen/skills/` | [Docs](https://qwenlm.github.io/qwen-code-docs/) |
| **global-skills** | - | `~/.agents/skills/` | - |

### Detalhes por Agent

#### Opencode
```
~/.config/opencode/
├── opencode.json      # Config principal
├── skills/            # Skills globais
├── tools/             # Tools customizadas
└── commands/          # Comandos customizados
```

#### Claude Code
```
~/.claude/
├── settings.json      # Config principal
└── commands/          # Comandos/skills customizados
```

#### Gemini CLI
```
~/.gemini/
└── settings.json      # Config principal
```

#### Pi.dev
```
~/.pi/
├── settings.json      # Config principal
└── agent/skills/      # Skills globais
```

#### Qwen Code
```
~/.qwen/
├── settings.json      # Config principal
└── skills/            # Skills globais
```

### Global Skills

O diretório `~/.agents/skills/` contém skills compartilhadas entre todos os agents:

```bash
# Habilitar sync de global skills
agent-sync enable global-skills

# Adicionar skill global
cp minha-skill.py ~/.agents/skills/

# Sync
agent-sync push
```

**Nota:** Pi.dev e Qwen Code também suportam `~/.agents/skills/` nativamente.

---

## 📁 Estrutura de Arquivos

### No Seu Computador

```
~/.agents/skills/                    ← Fonte da verdade (global)
├── code-review/
│   └── SKILL.md
├── python-expert/
│   └── SKILL.md
└── security-audit/
    └── SKILL.md

~/.config/agent-sync/
├── config.yaml                      ← Config do agent-sync
└── overrides.yaml                   ← Overrides locais

~/.config/<agent>/                   ← Configs específicas por agent
├── opencode/opencode.json
├── claude-code/settings.json
└── ...

~/.claude/commands/_global → ~/.agents/skills/  ← Symlink (Claude Code)
```

### No Repositório GitHub

```
my-agent-configs/
├── configs/
│   ├── opencode/
│   │   └── opencode.json
│   ├── claude-code/
│   │   └── settings.json
│   └── ...
│
├── skills/
│   └── global/                      ← Skills sincronizadas
│       ├── code-review/
│       │   └── SKILL.md
│       └── ...
│
├── .gitignore
└── README.md
```

## 🔧 Configuração

### Configuração Principal

`~/.config/agent-sync/config.yaml`

```yaml
repo_url: https://github.com/username/my-agent-configs.git
agents:
  - opencode
  - claude-code
  - qwen-code
include_secrets: false
include_mcp_secrets: false
sync_paths:
  configs: true
  skills: true
  prompts: false
  sessions: false
```

### Overrides Locais

`~/.config/agent-sync/overrides.yaml`

```yaml
# Configurações específicas desta máquina
machine_name: "macbook-pro"
custom_paths:
  opencode: /custom/path/to/opencode
```

---

## 🛠️ Desenvolvimento

### Instalar para desenvolvimento

```bash
git clone https://github.com/yourusername/agent-sync.git
cd agent-sync
pip install -e ".[dev]"
```

### Rodar testes

```bash
pytest
```

### Lint e format

```bash
ruff check .
black .
```

---

## 📝 Workflow Típico

### Setup inicial (primeira máquina)

```bash
# 1. Instalar
pip install agent-sync

# 2. Autenticar GitHub
gh auth login

# 3. Inicializar
agent-sync init --name my-agent-configs --private

# 4. Enviar configs existentes
agent-sync push

# 5. Verificar
agent-sync status
```

### Setup em nova máquina

```bash
# 1. Instalar
pip install agent-sync

# 2. Autenticar GitHub
gh auth login

# 3. Linkar
agent-sync link https://github.com/username/my-agent-configs.git

# 4. Baixar configs
agent-sync pull

# 5. Verificar
agent-sync status
```

### Dia-a-dia

```bash
# Antes de começar: puxar mudanças
agent-sync pull

# Fazer mudanças nas configs...

# Enviar mudanças
agent-sync push -m "feat: add new skill"
```

---

## ⚠️ Importante

### Nunca faça

- ❌ Commitar `.env` ou arquivos com secrets
- ❌ Usar repositório público com secrets habilitados
- ❌ Editar configs no repo GitHub diretamente

### Sempre faça

- ✅ Manter repositório **privado**
- ✅ Rodar `agent-sync pull` antes de `push`
- ✅ Verificar `agent-sync status` regularmente
- ✅ Usar `--force` com cuidado no `pull`

---

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/amazing-feature`)
3. Commit suas mudanças (`git commit -m 'feat: add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## 🙏 Inspiração

Este projeto foi inspirado por [opencode-synced](https://github.com/iHildy/opencode-synced), mas expandido para suportar múltiplos agents CLI.

---

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/yourusername/agent-sync/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/agent-sync/discussions)
