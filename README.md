# UFC-P Discord Bot

## Rodar localmente

1. Instale Python 3.10 ou superior.
2. Crie o ambiente e instale as dependências:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

3. Copie `.env.example` para `.env` e coloque o token do bot em `DISCORD_TOKEN`.
4. No Discord Developer Portal, ative **Message Content Intent** e **Server Members Intent**, convide o bot com os escopos `bot` e `applications.commands`.
5. Execute:

```bash
python bot.py
```

O banco SQLite e as cartas serão criados automaticamente dentro de `data/`.
