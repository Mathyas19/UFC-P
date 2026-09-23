import asyncio
import random
from typing import Dict, List

import discord
from discord.ext import commands

from card_generator import generate_card
from config import TOKEN
from database import DatabaseManager
from game_data import PLAYER_LIBRARY, STYLES, get_player_by_id


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

db = DatabaseManager()
ranked_queue: List[int] = []
player_styles: Dict[int, str] = {}


async def _build_profile_embed(user_id: int, username: str) -> discord.Embed:
    profile = db.get_or_create_user(str(user_id), username)
    inventory = db.get_user_players(str(user_id))
    dragons = sum(1 for item in inventory if item["is_dragon"])

    embed = discord.Embed(title=f"👤 {username}", color=0xFF5A36)
    embed.add_field(name="Nível", value=f"{profile['level']}/100", inline=True)
    embed.add_field(name="UFC Points", value=str(profile['ufc_points']), inline=True)
    embed.add_field(name="Energia", value=f"{profile['energy']}/50", inline=True)
    embed.add_field(name="Vitórias", value=str(profile['wins']), inline=True)
    embed.add_field(name="Empates", value=str(profile['draws']), inline=True)
    embed.add_field(name="Derrotas", value=str(profile['losses']), inline=True)
    embed.add_field(name="Partidas Jogadas", value=str(profile['matches_played']), inline=True)
    embed.add_field(name="Caixas UFC Dragon", value=str(profile['dragon_boxes']), inline=True)
    embed.add_field(name="Dragons recebidos", value=str(dragons), inline=True)
    embed.add_field(name="Quantidade de jogadores", value=str(profile['player_count']), inline=True)
    return embed


class ProfileInventoryView(discord.ui.View):
    def __init__(self, user_id: int, username: str):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.username = username

    @discord.ui.button(label="👥 JOGADORES DISPONÍVEIS", style=discord.ButtonStyle.primary)
    async def list_players(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("Este perfil não é seu.", ephemeral=True)
            return

        inventory = db.get_user_players(str(self.user_id))
        if not inventory:
            await interaction.response.send_message("Você ainda não possui jogadores.", ephemeral=True)
            return

        items_per_page = 5
        pages = [inventory[i : i + items_per_page] for i in range(0, len(inventory), items_per_page)]
        page = 0

        def build_view(current_page: int):
            v = discord.ui.View(timeout=180)
            for item in pages[current_page]:
                label = f"{item['name']} — {item['ovr']} OVR" + (" — UFC DRAGON" if item['is_dragon'] else "")
                async def callback(player_item=item, interaction_local=interaction):
                    card_path = generate_card(player_item["player_id"])
                    file = discord.File(card_path, filename=f"{player_item['player_id'].lower()}.png")
                    embed = discord.Embed(title=f"{player_item['name']}", color=0xFFD700 if player_item['is_dragon'] else 0xFF5A36)
                    embed.add_field(name="OVR", value=str(player_item['ovr']), inline=True)
                    embed.add_field(name="Posição", value=player_item['position'], inline=True)
                    embed.add_field(name="Ataque", value=str(player_item['attack']), inline=True)
                    embed.add_field(name="Defesa", value=str(player_item['defense']), inline=True)
                    embed.add_field(name="Físico", value=str(player_item['physical']), inline=True)
                    embed.add_field(name="Energia", value=str(player_item['energy']), inline=True)
                    embed.set_image(url=f"attachment://{card_path.name}")
                    await interaction_local.response.send_message(embed=embed, file=file, ephemeral=True)

                v.add_item(discord.ui.Button(label=label[:80], style=discord.ButtonStyle.secondary, custom_id=f"card_{player_item['player_id']}"))
                v.children[-1].callback = callback

            if len(pages) > 1:
                prev = discord.ui.Button(label="◀️", style=discord.ButtonStyle.secondary)
                next_ = discord.ui.Button(label="▶️", style=discord.ButtonStyle.secondary)

                async def prev_callback(interaction_prev: discord.Interaction):
                    nonlocal page
                    page = (page - 1) % len(pages)
                    await interaction_prev.response.edit_message(content=f"Jogadores possuídos ({page + 1}/{len(pages)})", embed=build_embed(page), view=build_view(page))

                async def next_callback(interaction_next: discord.Interaction):
                    nonlocal page
                    page = (page + 1) % len(pages)
                    await interaction_next.response.edit_message(content=f"Jogadores possuídos ({page + 1}/{len(pages)})", embed=build_embed(page), view=build_view(page))

                prev.callback = prev_callback
                next_.callback = next_callback
                v.add_item(prev)
                v.add_item(next_)

            return v

        def build_embed(current_page: int):
            lista = pages[current_page]
            text = "\n".join(
                f"• {item['name']} — {item['ovr']} OVR" + (" — UFC DRAGON" if item['is_dragon'] else "")
                for item in lista
            )
            emb = discord.Embed(title="👥 Jogadores possuídos", description=text, color=0x00B0F4)
            emb.set_footer(text=f"Página {current_page + 1}/{len(pages)}")
            return emb

        await interaction.response.send_message(embed=build_embed(page), view=build_view(page), ephemeral=True)


class StylePickerView(discord.ui.View):
    def __init__(self, bot_ref, user_one: int, user_two: int):
        super().__init__(timeout=180)
        self.bot_ref = bot_ref
        self.user_one = user_one
        self.user_two = user_two
        self.selected = {}

    def _add_style_button(self, label: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id not in (self.user_one, self.user_two):
                await interaction.response.send_message("Você não pode escolher esse estilo nesta luta.", ephemeral=True)
                return

            self.selected[str(interaction.user.id)] = label
            await interaction.response.edit_message(content=f"✅ Estilo selecionado: **{label}**", view=None)

            if len(self.selected) >= 2:
                await self.bot_ref.finalize_ranked_match(self.user_one, self.user_two, self.selected)

        self.add_item(discord.ui.Button(label=label, style=discord.ButtonStyle.primary, custom_id=f"style_{label.lower().replace('-', '')}"))
        self.children[-1].callback = callback

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True


# add style buttons
for style_name in ["Ataque", "Defesa", "Contra-ataque", "Equilibrado", "Pressão", "Paciência"]:
    setattr(StylePickerView, f"style_{style_name.lower().replace('-', '').replace(' ', '_')}", None)


@bot.event
async def on_ready():
    print(f"Bot conectado: {bot.user} (ID: {bot.user.id})")
    await bot.tree.sync()


@bot.tree.command(name="perfil", description="Mostra o perfil do jogador e seu inventário.")
async def perfil(interaction: discord.Interaction):
    username = interaction.user.display_name
    await interaction.response.send_message(embed=await _build_profile_embed(interaction.user.id, username), view=ProfileInventoryView(interaction.user.id, username), ephemeral=True)


@bot.tree.command(name="rank-participar", description="Entrar na fila ranked e procurar uma luta.")
async def rank_participar(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id in ranked_queue:
        await interaction.response.send_message("Você já está na fila ranked.", ephemeral=True)
        return

    ranked_queue.append(user_id)
    if len(ranked_queue) < 2:
        await interaction.response.send_message("Você entrou na fila ranked. Aguarde o próximo oponente.", ephemeral=True)
        return

    challenger_one = ranked_queue.pop(0)
    challenger_two = ranked_queue.pop(0)
    await interaction.response.send_message("Luta encontrada! Escolha seu estilo abaixo.", ephemeral=True)
    view = StylePickerView(bot, challenger_one, challenger_two)
    for style_name in ["Ataque", "Defesa", "Contra-ataque", "Equilibrado", "Pressão", "Paciência"]:
        view._add_style_button(style_name)

    for user_id_target in (challenger_one, challenger_two):
        member = bot.get_user(user_id_target)
        if member is not None:
            try:
                await member.send(content="🎮 Você foi encontrado em uma luta ranked. Escolha seu estilo:", view=view)
            except Exception:
                pass


async def resolve_match(user_one_id: int, user_two_id: int, style_one: str, style_two: str):
    fighter_one_id = db.get_fighter_for_user(str(user_one_id))
    fighter_two_id = db.get_fighter_for_user(str(user_two_id))

    player_one = get_player_by_id(fighter_one_id)
    player_two = get_player_by_id(fighter_two_id)

    profile_one = db.get_user_profile(str(user_one_id))
    profile_two = db.get_user_profile(str(user_two_id))

    energy_one = max(0.45, profile_one["energy"] / 50)
    energy_two = max(0.45, profile_two["energy"] / 50)

    style_one_mod = STYLES[style_one]
    style_two_mod = STYLES[style_two]

    round_wins_one = 0
    round_wins_two = 0
    round_events = []

    for round_number in range(1, 6):
        attack_one = (player_one["attack"] * style_one_mod["offense_bonus"] + player_one["physical"] * 0.6) * energy_one
        attack_two = (player_two["attack"] * style_two_mod["offense_bonus"] + player_two["physical"] * 0.6) * energy_two

        defense_one = (player_one["defense"] * style_one_mod["defense_bonus"]) * (0.8 + (profile_one["energy"] / 100))
        defense_two = (player_two["defense"] * style_two_mod["defense_bonus"]) * (0.8 + (profile_two["energy"] / 100))

        damage_one = max(0, attack_one - defense_two)
        damage_two = max(0, attack_two - defense_one)

        if damage_one > damage_two:
            round_wins_one += 1
            outcome = "Vitória do round para {0}"
            round_events.append(f"Round {round_number}: {player_one['name']} leva vantagem e vence o round.")
        elif damage_two > damage_one:
            round_wins_two += 1
            outcome = "Vitória do round para {0}"
            round_events.append(f"Round {round_number}: {player_two['name']} leva vantagem e vence o round.")
        else:
            round_events.append(f"Round {round_number}: reviravolta, os dois se equilibram.")

    if round_wins_one > round_wins_two:
        result = {str(user_one_id): "win", str(user_two_id): "loss"}
        winner_id = user_one_id
        winner_name = player_one["name"]
    elif round_wins_two > round_wins_one:
        result = {str(user_one_id): "loss", str(user_two_id): "win"}
        winner_id = user_two_id
        winner_name = player_two["name"]
    else:
        result = {str(user_one_id): "draw", str(user_two_id): "draw"}
        winner_id = None
        winner_name = "Empate"

    db.record_match_result(str(user_one_id), str(user_two_id), result[str(user_one_id)], fighter_one_id, fighter_two_id, "\n".join(round_events))
    db.record_match_result(str(user_two_id), str(user_one_id), result[str(user_two_id)], fighter_two_id, fighter_one_id, "\n".join(round_events))

    # energy loss after the whole fight
    db.use_energy(str(user_one_id), 1)
    db.use_energy(str(user_two_id), 1)

    return {
        "winner_id": winner_id,
        "winner_name": winner_name,
        "rounds": round_events,
        "result": result,
        "fighter_one": player_one,
        "fighter_two": player_two,
    }


async def finalize_ranked_match(user_one_id: int, user_two_id: int, selected_styles: Dict):
    style_one = selected_styles.get(str(user_one_id), "Equilibrado")
    style_two = selected_styles.get(str(user_two_id), "Equilibrado")

    match_result = await resolve_match(user_one_id, user_two_id, style_one, style_two)
    winner_msg = "Empate" if match_result["winner_id"] is None else f"<@{match_result['winner_id']}>"

    embed = discord.Embed(title="🥊 Luta Ranked concluída", color=0xFF5A36)
    embed.add_field(name="Resultado", value=f"Vencedor: {winner_msg}", inline=False)
    embed.add_field(name="Estilo 1", value=style_one, inline=True)
    embed.add_field(name="Estilo 2", value=style_two, inline=True)
    embed.add_field(name="Fighter 1", value=match_result["fighter_one"]["name"], inline=True)
    embed.add_field(name="Fighter 2", value=match_result["fighter_two"]["name"], inline=True)
    embed.description = "\n".join(match_result["rounds"][:3])

    for user_id_target in (user_one_id, user_two_id):
        member = bot.get_user(user_id_target)
        if member is not None:
            await member.send(embed=embed)


@bot.tree.command(name="abrir-caixa", description="Abre uma Caixa UFC Dragon para tentar obter um jogador exclusivo.")
async def abrir_caixa(interaction: discord.Interaction):
    profile = db.get_or_create_user(str(interaction.user.id), interaction.user.display_name)
    if profile["dragon_boxes"] <= 0:
        await interaction.response.send_message("Você não tem Caixas UFC Dragon para abrir.", ephemeral=True)
        return

    result = db.open_dragon_chest(str(interaction.user.id))
    if not result["opened"]:
        await interaction.response.send_message(result["reason"], ephemeral=True)
        return

    if result["is_dragon"]:
        card_path = generate_card(result["reward"])
        file = discord.File(card_path, filename=f"{result['reward'].lower()}.png")
        embed = discord.Embed(title="🐉 UFC DRAGON ABERTA!", description="Você conseguiu um jogador exclusivo de 100 OVR!", color=0xFFD700)
        embed.add_field(name="Jogador", value=result["reward"], inline=False)
        embed.set_image(url=f"attachment://{card_path.name}")
        await interaction.response.send_message(embed=embed, file=file, ephemeral=True)
    else:
        await interaction.response.send_message(f"{result['reason']} Jogador recebido: **{result['reward']}**", ephemeral=True)


@bot.tree.command(name="jogadores", description="Lista todos os jogadores do usuário.")
async def jogadores(interaction: discord.Interaction):
    inventory = db.get_user_players(str(interaction.user.id))
    if not inventory:
        await interaction.response.send_message("Você ainda não possui jogadores.", ephemeral=True)
        return

    text = "\n".join(f"• {item['name']} — {item['ovr']} OVR" + (" — UFC DRAGON" if item['is_dragon'] else "") for item in inventory)
    embed = discord.Embed(title="👥 Jogadores possuídos", description=text, color=0x00B0F4)
    await interaction.response.send_message(embed=embed, ephemeral=True)


if __name__ == "__main__":
    bot.run(TOKEN)
