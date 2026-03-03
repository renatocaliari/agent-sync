# Setup Wizard - Guia de Uso

O **agent-sync** agora possui um setup wizard interativo que facilita a configuração inicial.

---

## Quando o Wizard é Executado

### Automaticamente
- Ao rodar `agent-sync init` pela primeira vez (sem argumentos)
- Quando não há configuração existente em `~/.config/agent-sync/config.yaml`

### Manualmente
- Execute `agent-sync setup` para reconfigurar a qualquer momento

### Skip (Pular)
- Use `agent-sync init --name my-repo --no-wizard` para pular o wizard
- Ou passe os parâmetros diretamente: `--agents opencode claude-code`

---

## Passos do Wizard

### Step 1: Detecção de Agents Instalados

```
Step 1: Detecting Installed Agents
────────────────────────────────────

✓ Found installed agents:
  • opencode
  • claude-code
  • qwen-code

Not installed (2):
  • gemini-cli
  • pi.dev
```

O wizard detecta automaticamente quais agents estão instalados no seu sistema.

---

### Step 2: Selecionar Agents para Sync

```
Step 2: Select Agents to Sync
──────────────────────────────

┏━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Agent         ┃ Status ┃ Config Path              ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ opencode      │ ✓      │ ~/.config/opencode/...   │
│ claude-code   │ ✓      │ ~/.claude/settings.json  │
│ gemini-cli    │ ✗      │ ~/.gemini/settings.json  │
│ pi.dev        │ ✗      │ ~/.pi/settings.json      │
│ qwen-code     │ ✓      │ ~/.qwen/settings.json    │
└───────────────┴────────┴──────────────────────────┘

Which agents to sync [all]: all
```

**Opções:**
- `all` - Todos os agents instalados
- `none` - Nenhum agent
- `opencode,claude-code` - Lista específica (separada por vírgula)

---

### Step 3: Configurar Opções por Agent

```
Step 3: Configure Sync Options
───────────────────────────────

Configuring opencode:
  Sync configuration files? [Y/n]: y
  Sync skills/commands/tools? [Y/n]: y

Configuring claude-code:
  Sync configuration files? [Y/n]: y
  Sync skills/commands/tools? [Y/n]: n

Configuring qwen-code:
  Sync configuration files? [Y/n]: y
  Sync skills/commands/tools? [Y/n]: y
```

Para cada agent selecionado, você pode escolher:
- **Sync configs**: Arquivos de configuração (ex: `settings.json`)
- **Sync skills**: Skills, commands, tools personalizados

---

### Step 4: Global Skills

```
Step 4: Global Skills
─────────────────────

Global skills are stored in ~/.agents/skills/
Currently 19 skill(s) found.

Enable sync of global skills (~/.agents/skills/)? [Y/n]: y
```

Skills globais são compartilhadas entre múltiplos agents.

---

### Step 5: Configurações do Repositório

```
Step 5: Repository Settings
────────────────────────────

Repository name [agent-sync-configs]: my-agent-configs
Make repository private? [Y/n]: y
```

- **Nome**: Nome do repositório GitHub
- **Privado**: Recomendado se for sincronizar secrets

---

### Step 6: Secrets (Opcional)

```
Step 6: Secrets Configuration
──────────────────────────────

⚠ Only enable secrets with PRIVATE repositories!

Secrets include:
  • API keys
  • Auth tokens
  • MCP credentials

Enable secrets synchronization? [y/N]: n
```

**Importante:** Só habilite secrets em repositórios **privados**!

---

### Step 7: Revisão e Confirmação

```
Step 7: Review Configuration
─────────────────────────────

┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Setting         ┃ Value                    ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Repository      │ my-agent-configs         │
│ Visibility      │ 🔒 Private               │
│ Agents          │ opencode, claude-code,   │
│                 │ qwen-code, global-skills │
│ Global Skills   │ ✓                        │
│ Secrets         │ ✗ Disabled               │
└─────────────────┴──────────────────────────┘

Per-agent configuration:
  • opencode: configs, skills
  • claude-code: configs
  • qwen-code: configs, skills
  • global-skills: skills

Proceed with this configuration? [Y/n]: y
```

---

## Após o Wizard

### Criar Repositório

Depois de configurar, execute:

```bash
# Inicializa o repositório GitHub
agent-sync init

# Ou se já configurou via wizard:
agent-sync init --no-wizard
```

### Enviar Configs

```bash
# Envia suas configs para o repositório
agent-sync push
```

---

## Exemplo de Sessão Completa

```bash
# 1. Executar wizard
$ agent-sync setup

# 2. Inicializar repositório
$ agent-sync init

# 3. Enviar configs
$ agent-sync push

# 4. Verificar status
$ agent-sync status
```

---

## Configuração Gerada

O wizard cria `~/.config/agent-sync/config.yaml`:

```yaml
repo_url: null  # Definido após `agent-sync init`
agents:
  - opencode
  - claude-code
  - qwen-code
  - global-skills

agents_config:
  opencode:
    enabled: true
    sync:
      configs: true
      skills: true
  
  claude-code:
    enabled: true
    sync:
      configs: true
      skills: false
  
  qwen-code:
    enabled: true
    sync:
      configs: true
      skills: true
  
  global-skills:
    enabled: true
    sync:
      configs: false
      skills: true

include_secrets: false
include_mcp_secrets: false
```

---

## Dicas

1. **Primeira vez**: Use o wizard para configurar tudo corretamente
2. **Reconfigurar**: Execute `agent-sync setup` a qualquer momento
3. **Não-interativo**: Use flags `--name`, `--agents`, `--no-wizard`
4. **Secrets**: Só habilite em repositórios privados
5. **Global skills**: Útil para skills compartilhadas entre agents

---

## Troubleshooting

### Wizard não aparece
- Verifique se há config existente: `cat ~/.config/agent-sync/config.yaml`
- Delete e execute novamente: `rm ~/.config/agent-sync/config.yaml && agent-sync setup`

### Agente não detectado
- Verifique se o agent está instalado: `which opencode`
- O agent pode não estar no PATH

### Cancelar wizard
- Pressione `Ctrl+C` a qualquer momento
- Ou responda `n` na confirmação final
