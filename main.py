import os
import io
import glob
import textwrap
from datetime import datetime, timezone

import discord
from discord import AuditLogAction, app_commands
from discord.ui import View, Button
from PIL import Image, ImageDraw, ImageFont
from .shared import user_cache
from.keep_alive import keep_alive

# ——— 環境変数からトークン取得 ———
TOKEN = os.getenv("TOKEN")

# ——— ログ通知先チャンネル ———
LOG_CHANNEL_ID = 1372856531229610104

# ——— 画像保存設定 ———
MAX_CHARS_PER_LINE = 12
MAX_IMAGES = 10

# ——— Discord Client のセットアップ ———
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents, reconnect=True)
tree = app_commands.CommandTree(client)

user_cache = {}  # ユーザーID -> ユーザー名のキャッシュ

# ——— AuditLog 検索ヘルパー ———
async def fetch_audit_entry(
    guild: discord.Guild,
    action: AuditLogAction,
    target_id: int,
    *,
    lookback: float = 15.0
) -> discord.AuditLogEntry | None:
    now = datetime.now(timezone.utc)
    async for entry in guild.audit_logs(limit=10, action=action):
        if entry.target.id == target_id:
            if (now - entry.created_at).total_seconds() <= lookback:
                return entry
    return None

# ——— 画像保存／管理ユーティリティ ———
def get_user_folder(user_id: int) -> str:
    path = f"./user_images/{user_id}/"
    os.makedirs(path, exist_ok=True)
    return path

def get_user_images(user_id: int) -> list[str]:
    folder = get_user_folder(user_id)
    return sorted(glob.glob(f"{folder}/*.png"))

def delete_all_images(user_id: int) -> None:
    for p in get_user_images(user_id):
        try: os.remove(p)
        except: pass

def delete_image(path: str) -> bool:
    try:
        os.remove(path)
        return True
    except:
        return False

async def save_image(user_id: int, image_binary: io.BytesIO, name: str) -> str:
    folder = get_user_folder(user_id)
    file_path = os.path.join(folder, f"{name}.png")
    
    image_binary.seek(0)
    with open(file_path, "wb") as f:
        f.write(image_binary.read())
    return file_path

# ——— キック／退出監視 ———
@client.event
async def on_member_remove(member: discord.Member):
    guild = member.guild
    log_ch = guild.get_channel(LOG_CHANNEL_ID)
    if not log_ch:
        return

    # キック判定
    kick_entry = await fetch_audit_entry(guild, AuditLogAction.kick, member.id)
    if kick_entry:
        reason = kick_entry.reason or "なし"
        ts = kick_entry.created_at.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        await log_ch.send(
            f"🚪 **{member}** がキックされました\n"
            f"→ 実行者: **{kick_entry.user}**\n"
            f"→ 時間: `{ts}`\n"
            f"→ 理由: {reason}"
        )
        return

    # 自発退出
    await log_ch.send(f"👋 **{member}** が退出しました")

@client.event
async def on_member_ban(guild: discord.Guild, user: discord.User):
    log_ch = guild.get_channel(LOG_CHANNEL_ID)
    if not log_ch:
        return

    ban_entry = await fetch_audit_entry(guild, AuditLogAction.ban, user.id)
    if ban_entry:
        reason = ban_entry.reason or "なし"
        ts = ban_entry.created_at.astimezone().strftime("%Y-%m-%d %H:%M:%S")
        await log_ch.send(
            f"🔨 **{user}** が BAN されました\n"
            f"→ 実行者: **{ban_entry.user}**\n"
            f"→ 時間: `{ts}`\n"
            f"→ 理由: {reason}"
        )
    else:
        now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
        await log_ch.send(f"🔨 **{user}** が BAN されました\n→ 時間: `{now}`")

# ——— 画像生成モーダル／ビュー ———
class ImageSaveConfirmation(View):
    def __init__(self, oldest_path: str, user_id: int, image_binary: io.BytesIO, name: str):
        super().__init__()
        self.target = oldest_path
        self.user_id = user_id
        self.binary = image_binary
        self.name = name

    @discord.ui.button(label="削除して保存", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: Button):
        os.remove(self.target)
        await save_image(self.user_id, self.binary, self.name)
        await interaction.response.send_message("古い画像を削除して保存しました。", ephemeral=True)

    @discord.ui.button(label="キャンセル", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("保存をキャンセルしました。", ephemeral=True)

class ImageDeleteConfirmation(View):
    def __init__(self, path: str):
        super().__init__()
        self.path = path

    @discord.ui.button(label="削除", style=discord.ButtonStyle.danger)
    async def delete(self, interaction: discord.Interaction, button: Button):
        delete_image(self.path)
        await interaction.response.send_message("画像を削除しました。", ephemeral=True)

    @discord.ui.button(label="キャンセル", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("削除をキャンセルしました。", ephemeral=True)

class ProfileModal(discord.ui.Modal, title="性能表記"):
    text_input = discord.ui.TextInput(
        label="性能情報 (例: 周波数, ビット数など)",
        style=discord.TextStyle.paragraph,
        required=True,
    )

    def __init__(self, attachment, font_size, ephemeral, user_id, save, name):
        super().__init__()
        self.attachment = attachment
        self.font_size = font_size
        self.ephemeral = ephemeral
        self.user_id = user_id
        self.save = save
        self.name = name

    async def on_submit(self, interaction: discord.Interaction):
        # 画像処理
        data = await self.attachment.read()
        img = Image.open(io.BytesIO(data)).resize((300,300), Image.LANCZOS)
        font = ImageFont.truetype("./msgothic.ttc", self.font_size)
        lines = textwrap.wrap(self.text_input.value, MAX_CHARS_PER_LINE)
        extra = len(lines) * (self.font_size + 5)
        canvas = Image.new("RGB", (300, 300 + extra), "white")
        canvas.paste(img, (0,0))
        draw = ImageDraw.Draw(canvas)
        y = 300
        for line in lines:
            draw.text((10, y), line, fill="black", font=font)
            y += self.font_size + 5

        buf = io.BytesIO()
        canvas.save(buf, format="PNG")
        buf.seek(0)

        await interaction.response.send_message(
            "画像を生成しました！",
            file=discord.File(buf, "modified.png"),
            ephemeral=self.ephemeral
        )

        if self.save:
            imgs = get_user_images(self.user_id)
            if len(imgs) >= MAX_IMAGES:
                view = ImageSaveConfirmation(imgs[0], self.user_id, buf, self.name)
                await interaction.followup.send(
                    "上限を超えました。古い画像を削除してもよいですか？",
                    file=discord.File(imgs[0]),
                    view=view,
                    ephemeral=True
                )
            else:
                await save_image(self.user_id, buf, self.name)

# ——— スラッシュコマンド定義 ———
@tree.command(name="profile", description="画像に情報を追加します")
async def profile(
    interaction: discord.Interaction,
    attachment: discord.Attachment,
    font_size: int = 20,
    ephemeral: bool = False,
    save: bool = False,
    name: str = "CPU"
):
    await interaction.response.send_modal(ProfileModal(
        attachment=attachment,
        font_size=font_size,
        ephemeral=ephemeral,
        user_id=interaction.user.id,
        save=save,
        name=name
    ))

@tree.command(name="library", description="保存画像を一覧表示します")
async def library(
    interaction: discord.Interaction,
    name: str | None = None,
    n: int | None = None
):
    user_id = interaction.user.id
    imgs = get_user_images(user_id)

    if name:
        path = next((p for p in imgs if name in os.path.basename(p)), None)
        if path:
            await interaction.response.send_message(file=discord.File(path))
        else:
            await interaction.response.send_message("該当画像が見つかりません。")
    elif n is not None:
        if 0 <= n-1 < len(imgs):
            await interaction.response.send_message(file=discord.File(imgs[n-1]))
        else:
            await interaction.response.send_message("その番号の画像は存在しません。")
    else:
        if imgs:
            msg = "\n".join(f"{i+1}: {os.path.basename(p)}" for i,p in enumerate(imgs))
            await interaction.response.send_message(
                msg, files=[discord.File(p) for p in imgs], ephemeral=True
            )
        else:
            await interaction.response.send_message("保存画像はありません。")

@tree.command(name="delete", description="画像を削除します (0 で全削除)")
async def delete(
    interaction: discord.Interaction,
    n: int
):
    user_id = interaction.user.id
    imgs = get_user_images(user_id)

    if n == 0:
        delete_all_images(user_id)
        await interaction.response.send_message("すべての画像を削除しました。", ephemeral=True)
    else:
        idx = n - 1
        if 0 <= idx < len(imgs):
            view = ImageDeleteConfirmation(imgs[idx])
            await interaction.response.send_message(
                f"「{os.path.basename(imgs[idx])}」を削除しますか？",
                file=discord.File(imgs[idx]),
                view=view,
                ephemeral=True
            )
        else:
            await interaction.response.send_message("その番号の画像は存在しません。", ephemeral=True)

@tree.command(name="reset_user_cache")
async def reset_user_cache(interaction: discord.Interaction):
    """ユーザーキャッシュをリセットします。"""
    await cache_user_name()
    await interaction.response.send_message(f"ユーザーキャッシュをリセットしました\n{user_cache}", ephemeral=True)

# ——— RPG コマンド群 ———
RPG_USERS = {}

@tree.command(name="join-rpg", description="RPGに参加します")
async def join_rpg(interaction: discord.Interaction):
    uid = interaction.user.id
    if uid not in RPG_USERS:
        RPG_USERS[uid] = {"login_days": 0, "level": 1}
    await interaction.response.send_message("RPGに参加しました！", ephemeral=True)

@tree.command(name="login", description="RPGにログインします")
async def login(interaction: discord.Interaction):
    uid = interaction.user.id
    if uid in RPG_USERS:
        RPG_USERS[uid]["login_days"] += 1
        await interaction.response.send_message("ログインしました！", ephemeral=True)
    else:
        await interaction.response.send_message("未登録です。/join-rpg で登録してください。", ephemeral=True)

@tree.command(name="rpg_information", description="RPGステータスを表示します")
async def rpg_information(interaction: discord.Interaction):
    uid = interaction.user.id
    if uid in RPG_USERS:
        info = "\n".join(f"{k}: {v}" for k,v in RPG_USERS[uid].items())
        await interaction.response.send_message(info, ephemeral=True)
    else:
        await interaction.response.send_message("未登録です。/join-rpg で登録してください。", ephemeral=True)

# ——— 起動処理 ———

async def cache_user_name():
    for guild in client.guilds:
        async for member in guild.fetch_members(limit=None):
            user_cache[str(member.id)] = f'{member.name}#{member.discriminator}'

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    await cache_user_name()

if __name__ == "__main__":
    os.makedirs(keep_alive.USER_IMAGE_DIR, exist_ok=True)
    keep_alive()
    client.run(TOKEN)
