# Reconfigurando Agent Sync

Você pode reconfigurar o **agent-sync** a qualquer momento, mesmo depois de usar por um tempo.

---

## Quando Reconfigurar

- ✅ Adicionar novo agent (ex: começou a usar Gemini CLI)
- ✅ Remover agent que não usa mais
- ✅ Mudar o que é sincronizado (ex: parar de sync skills)
- ✅ Habilitar/desabilitar global skills
- ✅ Mudar configurações de secrets
- ✅ Corrigir configuração incorreta

---

## Métodos de Reconfiguração

### 1. Setup Wizard (Recomendado)

```bash
# Reconfigurar tudo com wizard interativo
agent-sync setup
```

**O que acontece:**
- Detecta agents instalados
- Mostra configuração atual
- Permite mudar tudo
- Mantém seu repositório vinculado
- **Não deleta dados do repo**

**Fluxo:**
```
1. Aviso de configuração existente
2. Confirmação para continuar
3. Wizard completo (igual ao setup inicial)
4. Configuração atualizada
5. Prompt para rodar `agent-sync push`
```

---

### 2. Comandos de Configuração

#### Ver Configuração Atual

```bash
# Mostrar configuração
agent-sync config show
```

**Output exemplo:**
```
📋 Current Configuration

Repository: https://github.com/user/my-configs.git

Enabled Agents:
  ✓ opencode: configs, skills
  ✓ claude-code: configs
  ✗ gemini-cli (disabled)
  ✓ qwen-code: configs, skills
  ✓ global-skills: skills

Secrets:
  Include secrets: No
  Include MCP: No

Config file: ~/.config/agent-sync/config.yaml
```

---

#### Editar Manualmente

```bash
# Abrir arquivo de configuração no editor
agent-sync config edit

# Ou edite manualmente
nano ~/.config/agent-sync/config.yaml
```

**Exemplo de edição:**

```yaml
# Antes
agents_config:
  opencode:
    enabled: true
    sync:
      configs: true
      skills: true

# Depois - desabilitar skills do opencode
agents_config:
  opencode:
    enabled: true
    sync:
      configs: true
      skills: false  # ← Mudar aqui
```

---

#### Resetar para Defaults

```bash
# Resetar configuração (mantém repo vinculado)
agent-sync config reset
```

**O que faz:**
- Reseta todas as configurações para valores padrão
- Mantém `repo_url` (não desvincula)
- Habilita todos os agents detectados
- Remove configurações customizadas

**Depois do reset:**
```bash
# Reconfigurar com wizard
agent-sync setup

# Ou editar manualmente
agent-sync config edit
```

---

### 3. Comandos Enable/Disable

```bash
# Habilitar agent específico
agent-sync enable gemini-cli

# Desabilitar agent
agent-sync disable claude-code

# Verificar status
agent-sync agents
```

**Rápido e direto** - bom para mudanças simples.

---

## Cenários Comuns

### Cenário 1: Adicionar Novo Agent

Você começou a usar Gemini CLI:

```bash
# Opção A: Wizard (mais fácil)
agent-sync setup
# → Selecionar gemini-cli na lista
# → Configurar opções de sync
# → Confirmar

# Opção B: Comando rápido
agent-sync enable gemini-cli

# Depois: enviar mudanças
agent-sync push -m "feat: add gemini-cli sync"
```

---

### Cenário 2: Parar de Sync Skills

Skills estão ocupando muito espaço:

```bash
# Opção A: Wizard
agent-sync setup
# → Para cada agent: responder "n" em "Sync skills?"

# Opção B: Editar config
agent-sync config edit

# Mudar no YAML:
agents_config:
  opencode:
    sync:
      skills: false  # ← Mudar para false
  claude-code:
    sync:
      skills: false

# Depois: push
agent-sync push -m "chore: disable skills sync"
```

---

### Cenário 3: Habilitar Global Skills

Você quer compartilhar skills entre agents:

```bash
# Opção A: Wizard
agent-sync setup
# → Step 4: "Enable sync of global skills?" → y

# Opção B: Enable direto
agent-sync enable global-skills

# Ver skills globais
ls ~/.agents/skills/

# Push
agent-sync push
```

---

### Cenário 4: Corrigir Configuração Errada

Configuração ficou bagunçada:

```bash
# Resetar tudo
agent-sync config reset

# Reconfigurar do zero
agent-sync setup

# Verificar
agent-sync config show
agent-sync agents
```

---

### Cenário 5: Mudar Apenas Secrets

Habilitar/desabilitar secrets:

```bash
# Habilitar secrets
agent-sync secrets enable

# Habilitar incluindo MCP
agent-sync secrets enable --include-mcp

# Desabilitar
agent-sync secrets disable

# Verificar
agent-sync config show
```

---

## Fluxo Completo de Reconfiguração

```bash
# 1. Ver configuração atual
agent-sync config show
agent-sync agents

# 2. Reconfigurar (wizard)
agent-sync setup

# 3. Verificar mudanças
agent-sync config show
agent-sync status

# 4. Enviar mudanças para o repo
agent-sync push -m "chore: update configuration"

# 5. Em outras máquinas, puxar mudanças
# (em outra máquina)
agent-sync pull
```

---

## O Que é Mantido vs. Alterado

### Mantido ✅
- URL do repositório
- Configs já sincronizadas no repo
- Histórico do git
- Secrets no `.env` local

### Alterado 🔄
- Configuração em `~/.config/agent-sync/config.yaml`
- Agents habilitados/desabilitados
- Opções de sync por agent
- Configs de secrets

### Não Afetado ❌
- Arquivos em `~/.agents/skills/`
- Configs dos agents (`~/.claude/`, `~/.qwen/`, etc.)
- Repositório GitHub remoto

---

## Boas Práticas

### 1. Faça Push Após Reconfigurar

```bash
agent-sync setup
agent-sync push -m "chore: reconfigure agents"
```

### 2. Avise Outros Usuários

Se compartilha o repo:

```bash
# Após reconfigurar e push
git commit -m "chore: add gemini-cli sync

Other users should run:
  agent-sync pull
"
```

### 3. Teste Antes de Push

```bash
# Verificar status
agent-sync status

# Ver agents
agent-sync agents

# Só depois: push
agent-sync push
```

### 4. Backup da Config

```bash
# Backup antes de reset
cp ~/.config/agent-sync/config.yaml \
   ~/.config/agent-sync/config.yaml.backup

# Depois de reset
agent-sync config reset
```

---

## Troubleshooting

### Reconfiguração não aplica

```bash
# Forçar pull após reconfigurar
agent-sync pull --force

# Ou reset completo
agent-sync config reset
agent-sync setup
agent-sync pull --force
```

### Agents não aparecem

```bash
# Verificar se agent está instalado
which opencode

# Verificar detecção
agent-sync agents

# Se não detectado, instalar agent ou verificar PATH
```

### Configuração corrompida

```bash
# Resetar
agent-sync config reset

# Ou deletar e recriar
rm ~/.config/agent-sync/config.yaml
agent-sync setup
```

---

## Resumo dos Comandos

| Comando | Descrição | Quando Usar |
|---------|-----------|-------------|
| `agent-sync setup` | Wizard interativo | Reconfigurar tudo |
| `agent-sync config show` | Ver configuração | Checar status |
| `agent-sync config edit` | Editar manualmente | Mudanças específicas |
| `agent-sync config reset` | Resetar defaults | Começar do zero |
| `agent-sync enable <agent>` | Habilitar agent | Adicionar agent rápido |
| `agent-sync disable <agent>` | Desabilitar agent | Remover agent rápido |
| `agent-sync push` | Enviar mudanças | Após reconfigurar |

---

## Próximos Passos

Após reconfigurar:

1. ✅ Verificar configuração: `agent-sync config show`
2. ✅ Enviar mudanças: `agent-sync push`
3. ✅ Atualizar outras máquinas: `agent-sync pull`
4. ✅ Testar sync: `agent-sync status`
