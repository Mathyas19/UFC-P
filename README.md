# UFC-P Discord Bot

Bot de Discord em Python com jogadores, ranked, energia, UFC Dragon e geração de cartas.

## Jeito mais fácil de iniciar

### Windows

1. Instale o Python 3.10 ou superior.
2. Baixe o projeto pelo botão **Code > Download ZIP** e extraia a pasta.
3. Abra a pasta `UFC-P`.
4. Dê dois cliques em `iniciar_windows.bat`.
5. Cole o token do bot quando o programa pedir e pressione Enter.

### Linux/macOS

Abra o terminal dentro da pasta do projeto e execute:

```bash
chmod +x iniciar_linux_mac.sh
./iniciar_linux_mac.sh
```

O script cria o ambiente Python, instala as dependências, cria o arquivo `.env` e inicia o bot. A pasta `data` já está incluída; o banco SQLite e as cartas serão criados automaticamente.

## Configuração do Discord

No Discord Developer Portal, ative **Message Content Intent** e **Server Members Intent**. Convide o bot usando os escopos `bot` e `applications.commands`.

> Segurança: nunca publique o token no GitHub. Se um token real apareceu no repositório, revogue-o e gere outro no Discord Developer Portal.

## Início manual

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
.venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
python bot.py
```

Depois edite `.env` e substitua `cole_seu_token_aqui` pelo token novo do bot. No Windows, copie `.env.example`, renomeie a cópia para `.env` e edite-a pelo Bloco de Notas.
