import discord
from discord import app_commands
from discord.ui import View, Button
from discord.ext import tasks
from PIL import Image, ImageDraw, ImageFont
import io
import os
import textwrap
import glob

# Discord Botのセットアップ
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents, reconnect=True)
tree = app_commands.CommandTree(client)

TOKEN = os.getenv("TOKEN")

MAX_CHARS_PER_LINE = 12  # 12文字ごとに改行
MAX_IMAGES = 10  # 保存する画像の最大数
cpu_information = {}

@client.event
async def on_ready():
    await tree.sync()
    os.makedirs("./files", exist_ok=True)
    print(f"We have logged in as {client.user}")

# ユーザーのすべての画像を削除
def delete_all_images(user_id):
    user_images = get_user_images(user_id)
    for img in user_images:
        delete_image(img)

# 画像を削除
def delete_image(image_path):
    try:
        os.remove(image_path)
        return True
    except Exception as e:
        print(f"Error deleting image: {e}")
        return False

# ユーザーのフォルダを取得 or 作成
def get_user_folder(user_id):
    folder_path = f"./user_images/{user_id}/"
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

# ユーザーの画像一覧を取得
def get_user_images(user_id):
    folder_path = get_user_folder(user_id)
    return sorted(glob.glob(f"{folder_path}/*.png"))  # 古い順にソート

# ユーザーの画像をファイル名で検索
def get_image_by_name(user_id, name):
    user_images = get_user_images(user_id)
    for img in user_images:
        if name in img:  # ファイル名に名前が含まれているかチェック
            return img
    return None

# ユーザーの画像をn番目の画像で取得
def get_image_by_index(user_id, index):
    user_images = get_user_images(user_id)
    if 0 <= index < len(user_images):
        return user_images[index]
    return None

# 画像の保存処理
async def save_image(user_id, image,name):
    folder_path = get_user_folder(user_id)
    file_path = f"{folder_path}/{name}.png"

    with open(file_path, "wb") as f:
        image.seek(0)
        f.write(image.read())

    return file_path

# 画像削除確認ボタンのView
class DeleteConfirmationView(View):
    def __init__(self, oldest_image, user_id,image_binary):
        super().__init__()
        self.oldest_image = oldest_image
        self.user_id = user_id
        self.image_binary = image_binary

    @discord.ui.button(label="YES (削除)", style=discord.ButtonStyle.danger)
    async def confirm_delete(self, interaction: discord.Interaction, button: Button):
        try:
            os.remove(self.oldest_image)
            await interaction.response.send_message("古い画像を削除しました。", ephemeral=True)
            await save_image(self.user_id, self.image_binary)
        except Exception as e:
            await interaction.response.send_message(f"削除に失敗しました: {e}", ephemeral=True)

    @discord.ui.button(label="NO (保存しない)", style=discord.ButtonStyle.secondary)
    async def cancel_delete(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("画像の保存を取り消しました", ephemeral=True)

class MyModal(discord.ui.Modal, title="性能表記"):
    text_input = discord.ui.TextInput(
        label="性能などの情報を記入してください",
        placeholder="例:周波数,ビット数など...",
        style=discord.TextStyle.paragraph,
        required=True,
    )

    def __init__(self, attachment, font_size, ephemeral, user_id, save,name):
        super().__init__()
        self.attachment = attachment
        self.font_size = font_size
        self.ephemeral = ephemeral
        self.user_id = user_id
        self.save = save
        self.name = name

    async def on_submit(self, interaction: discord.Interaction):
        user_text = self.text_input.value

        # 画像を取得
        image_bytes = await self.attachment.read()
        original_image = Image.open(io.BytesIO(image_bytes))

        # 画像を一旦300x300にリサイズ
        original_image = original_image.resize((300, 300), Image.LANCZOS)

        # フォント設定
        font = ImageFont.truetype("./msgothic.ttc", self.font_size)

        # 改行処理（MAX_CHARS_PER_LINE 文字ごと）
        wrapped_text = textwrap.wrap(user_text, MAX_CHARS_PER_LINE)

        # 必要な余白を計算（行数 * フォントサイズ + 行間調整）
        num_lines = len(wrapped_text)
        extra_space = num_lines * (self.font_size + 5)  # 行ごとに余白を追加

        # 新しいキャンバス作成（元画像 + 余白）
        new_height = 300 + extra_space
        new_image = Image.new("RGB", (300, new_height), "white")
        new_image.paste(original_image, (0, 0))

        # テキスト描画
        draw = ImageDraw.Draw(new_image)
        y_position = 300  # 画像の下部から少し余白を空ける
        for line in wrapped_text:
            draw.text((10, y_position), line, fill="black", font=font)
            y_position += self.font_size + 5  # 行間を調整

        # 画像をバイトデータに変換
        image_binary = io.BytesIO()
        new_image.save(image_binary, format="PNG")
        image_binary.seek(0)

        # 画像を送信
        await interaction.response.send_message(
            content="画像を生成しました！",
            file=discord.File(fp=image_binary, filename="modified_image.png"),
            ephemeral=self.ephemeral
        )

        # ユーザーごとのフォルダに保存（オプション）
        if self.save:
            user_images = get_user_images(self.user_id)
            if len(user_images) >= MAX_IMAGES:
                # 画像が10枚を超えたら、一番古い画像を削除するか確認
                oldest_image = user_images[0]
                view = DeleteConfirmationView(oldest_image, self.user_id,image_binary)
                await interaction.followup.send(
                    f"保存上限を超えました。最も古い画像を削除しますか？一番古い画像:",
                    file=discord.File(user_images[0]),
                    view=view,
                    ephemeral=True
                )
            else:
                await save_image(self.user_id, image_binary,self.name)

        

@tree.command(name="profile", description="画像に、CPUなどの情報を追加します")
async def profile(
    interaction: discord.Interaction,
    attachment: discord.Attachment,
    font_size: int = 20,
    ephemeral: bool = False,
    save: bool = False,
    name: str = "CPU",
):
    await interaction.response.send_modal(MyModal(
        attachment=attachment,
        font_size=font_size,
        ephemeral=ephemeral,
        user_id=interaction.user.id,
        save=save,
        name=name,
    ))

# 削除確認用のビュー
class DeleteConfirmationView(discord.ui.View):
    def __init__(self, image_path, user_id):
        super().__init__()
        self.image_path = image_path
        self.user_id = user_id

    @discord.ui.button(label="削除", style=discord.ButtonStyle.danger)
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if delete_image(self.image_path):
            await interaction.response.send_message(
                content=f"画像「{os.path.basename(self.image_path)}」を削除しました。",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                content="画像の削除に失敗しました。",
                ephemeral=True
            )
        self.stop()

    @discord.ui.button(label="キャンセル", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            content="削除がキャンセルされました。",
            ephemeral=True
        )
        self.stop()

@tree.command(name="library", description="ユーザーの保存した画像を表示します")
async def library(interaction: discord.Interaction, name: str = None, n: int = None):
    user_id = interaction.user.id

    if name:
        # 指定した名前の画像を検索
        image_path = get_image_by_name(user_id, name)
        if image_path:
            await interaction.response.send_message(
                content=f"指定された名前の画像: {name}",
                file=discord.File(image_path)
            )
        else:
            await interaction.response.send_message(
                content=f"指定された名前の画像「{name}」は見つかりませんでした。"
            )
    elif n is not None:
        # 指定された番号の画像を表示
        image_path = get_image_by_index(user_id, n)
        if image_path:
            await interaction.response.send_message(
                content=f"{n + 1}番目の画像を表示します。",
                file=discord.File(image_path)
            )
        else:
            await interaction.response.send_message(
                content=f"{n + 1}番目の画像は存在しません。"
            )
    else:
        # すべての画像を表示
        user_images = get_user_images(user_id)
        if user_images:
            messages = []
            for idx, img in enumerate(user_images):
                messages.append(f"{idx + 1}: {os.path.basename(img)}")
            
            messages.append("\nこれらの画像のいずれかを選択できます。")
            await interaction.response.send_message(
                content="\n".join(messages),
                files=[discord.File(img) for img in user_images],
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                content="保存された画像はありません。"
            )


@tree.command(name="delete", description="指定した番号番目の画像を削除します。nを0にすることですべての画像を削除します")
async def delete(interaction: discord.Interaction, n: int):
    user_id = interaction.user.id

    if n == 0:
        # すべての画像を削除する場合
        delete_all_images(user_id)
        await interaction.response.send_message(
            content="保存されているすべての画像を削除しました。",
            ephemeral=True
        )
    else:
        # ユーザーの保存した画像を取得
        image_path = get_image_by_index(user_id, n)

        if image_path:
            # 削除確認のビューを作成して送信
            view = DeleteConfirmationView(image_path, user_id)
            await interaction.response.send_message(
                content=f"画像「{os.path.basename(image_path)}」を削除しますか？",
                file=discord.File(image_path),
                view=view,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                content=f"{n + 1}番目の画像は存在しません。",
                ephemeral=True
            )

@tree.command(name="cpuinfo", description="CPUの情報を保存します")
async def cpuinfo(interaction: discord.Interaction, file: discord.Attachment,instruction: discord.Attachment,name: str = None):
    await interaction.response.defer(thinking=True, ephemeral=True)
    if name is None:
        cpuname = file.filename.split(".")[0]
    else:
        cpuname = name
    
    cpuname = cpuname.replace(" ", "_")
    save_path = os.path.join("./files", cpuname + ".mcstructure")
    await file.save(save_path)
    save_path = os.path.join("./files", cpuname + ".png")
    
    await instruction.save(save_path)
    cpu_information[cpuname] = interaction.user.id
    await interaction.followup.send(
        content="CPUの情報を保存しました！",
        ephemeral=True
    )

@tree.command(name="getcpuinfo", description="CPUの情報を取得します")
async def getcpuinfo(interaction: discord.Interaction, name: str):
    await interaction.response.defer(thinking=True, ephemeral=True)
    cpuname = name.replace(" ", "_")
    save_path = os.path.join("./files", cpuname + ".mcstructure")
    save_path2 = os.path.join("./files", cpuname + ".png")
    path = f"./user_images/{cpu_information[cpuname]}/{cpuname}.png"
    files_to_send = [discord.File(save_path), discord.File(save_path2)]
    
    if os.path.exists(path):
        files_to_send.append(discord.File(path))
    if os.path.exists(save_path):
        await interaction.followup.send(
            content=f"CPUの情報を取得しました！",
            files=files_to_send,
            ephemeral=True
        )
    else:
        await interaction.followup.send(
            content="CPUの情報が見つかりませんでした！",
            ephemeral=True
        )
    

"""
ここからRPG関連のコード
"""

RPG_USERS_INFORMATION = {}

@tree.command(name="login", description="ログインします")
async def login(interaction: discord.Interaction):
    
    user_id = interaction.user.id
    if user_id in RPG_USERS_INFORMATION:
        await interaction.response.send_message("ログインしました！",ephemeral=True)
        RPG_USERS_INFORMATION[user_id]["login days"] += 1
    else:
        await interaction.response.send_message("まだ登録されていません！/join-rpgを実行して登録してください！",ephemeral=True)

@tree.command(name="information", description="RPGの情報を表示します")
async def information(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id in RPG_USERS_INFORMATION:
        messages = []
        for key, value in RPG_USERS_INFORMATION[user_id].items():
            messages.append(f"{key}: {value}\n")
        await interaction.response.send_message(messages,ephemeral=True)
    else:
        await interaction.response.send_message("まだ登録されていません！/join-rpgを実行して登録してください！",ephemeral=True)

@tree.command(name="join-rpg", description="RPGに参加します")
async def join_rpg(interaction: discord.Interaction):
    await interaction.response.send_message(
        content="RPGに参加しました！",
        ephemeral=True
    )
    user_id = interaction.user.id
    RPG_USERS_INFORMATION[user_id] = {"login days": 0, "level": 0, }

client.run(TOKEN)
