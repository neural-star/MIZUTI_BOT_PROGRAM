importインポート discorddiscord
fromdiscord import app_commands よりdiscord import app_commands
fromdiscord。ui import View, Button よりdiscord.ui import View, Button
fromdiscord。ext インポートタスクからdiscord.ext import tasks
fromPIL インポート Image、ImageDraw、ImageFont からPIL import Image, ImageDraw, ImageFont
importimport ioio
importos をインポートos
importテキストラップをインポートtextwrap
importglob をインポートglob
fromgoogleapiclient。discovery インポートビルド からgoogleapiclient.discovery import build
fromkeep_alive インポートから keep_aliveimport keep_alive

## Discord Bot の の consult TOTOACHONB 咎めDiscord Botのセットアップ
intentsintents = discord。Intents。default()discord.Intents.default()
intentsintents。members = Truemembers = True
clientクライアント = discord。Client（intents=intents, reconnect=True）discord.Client(intents=intents, reconnect=True)
treeツリー = app_commands。CommandTree（クライアント）CommandTree(client)

TOKENTOKEN = os。getenv("TOKEN")os.getenv("TOKEN")
YOUTUBE_API_KEY = os。getenv("youtube_api_key")os.getenv("youtube_api_key")
CHANNEL_ID = os。getenv("chanel_id")os.getenv("chanel_id")
YOUTUBE_CHANNEL_ID = os。getenv("youtube_id")os.getenv("youtube_id")

MAX_CHARS_PER_LINE = 16 # 16 文字の行16  # 16文字ごとに改行
MAX_IMAGES = 10 # RECORRENT son suurneu 影の / 大数10  # 保存する画像の最大数

## YouTube API の 尖 際 錫YouTube APIの初期化
youtubeyoutube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY）build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
## 汝新の 'は' 'は' RECONITION sons し det, 'は' 通るは 'は'IDを保存して、重複通知を防ぐ
latest_video_id = なしNone

@client。eventclient.event
asyncasync def on_ready():def on_ready():
 await tree。sync()await tree.sync()
 check_new_videos。start()start()
 print（f"{client。user} としてログインしました")print(f"We have logged in as {client.user}")

##60 瀹 とにニェェ？ちょ60分ごとにチェック
@tasks。loop（分=60)tasks.loop(minutes=60)
asyncasync def check_new_videos():def check_new_videos():
 グローバル latest_video_idglobal latest_video_id
 試してみてください:try:
 応答 = youtube。search()。list()response = youtube.search().list(
 part= "スニペット" 、part="snippet",
 channelid=youtube_CHANNEL_ID 、channelId=YOUTUBE_CHANNEL_ID,
 order= "日付" 、order="date",
 maxresults=1 、maxResults=1,
 type= "video"type="video"
 )。execute()).execute()

 video_id = response['items'][0]['id']['videoId']response['items'][0]['id']['videoId']
 video_title = response['items'][0]['snippet']['title']response['items'][0]['snippet']['title']
 video_thumbnail = response['items'][0]['snippet']['thumbnails']['high']['url']response['items'][0]['snippet']['thumbnails']['high']['url']
 video_url = f"https://www。youtube。com/watch？v={video_id}"f"https://www.youtube.com/watch?v={video_id}"

 もしvideo_id！= latest_video_id:if video_id != latest_video_id:
 channel = client。get_channel（int（CHANNEL_ID）)channel = client.get_channel(int(CHANNEL_ID))

 = discord。Embed を埋め込む (embed = discord.Embed(
 title=video_title 、title=video_title,
 url=video_url 、url=video_url,
 description= "新思イグガpublicelougaレマ思タ！:忠:",description="新しい動画が公開されました！:tada: ",
 color=discord。color。red()color=discord.Color.red()
            )
 embed。set_thumbnail（url=video_thumbnail）embed.set_thumbnail(url=video_thumbnail)

 await channel。send（embed=embed）await channel.send(embed=embed)
 latest_video_id = video_id

 e: としての例外を除くexcept Exception as e:
 print（f"etLAー gazu 生しまし た: {e}")print(f"エラーが発生しました: {e}")

## ウーリーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシューダーヌーのシュー
defdef delete_all_images（user_id）:(user_id):
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
async def save_image(user_id, image):
    folder_path = get_user_folder(user_id)
    file_path = f"{folder_path}/{discord.utils.utcnow().timestamp()}.png"

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

    def __init__(self, attachment, font_size, ephemeral, user_id, save):
        super().__init__()
        self.attachment = attachment
        self.font_size = font_size
        self.ephemeral = ephemeral
        self.user_id = user_id
        self.save = save

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
                await save_image(self.user_id, image_binary)

        

@tree.command(name="profile", description="画像に、CPUなどの情報を追加します")
async def profile(
    interaction: discord.Interaction,
    attachment: discord.Attachment,
    font_size: int = 20,
    ephemeral: bool = False,
    save: bool = False
):
    await interaction.response.send_modal(MyModal(
        attachment=attachment,
        font_size=font_size,
        ephemeral=ephemeral,
        user_id=interaction.user.id,
        save=save
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
 async def cancel_button（self, interaction: discord。相互作用、ボタン: discord。うい。Button）:
 イハヤトラ シ シネッ。レスポンス。send_message ウーシン ロチマ ス ()
 content= "「 creti agak」" "「 creti agak」"
 ephemeral=true
        )
 となる()は、ラーチーチー()、ラーチーチーチー()、ラーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチーチー

@ツリー。command（name= "library", description="e。ウーーヽーのREQUISION sonsishiantoinamo SHOMA su」
async def library（interaction: discord。インタラクション、名前: str = None、n: int = None）:
 user_id = インタラクション。ユーザー。id を

 名前前ガアールリン合:
 # 指田名前之者之尾之尾
 image_path = get_image_by_name（user_id, name）
 if image_path:
 イハヤトラ シ シネッ。レスポンス。send_message ウーシン ロチマ ス ()
 content=f "指文字リータハニ名前之尾尾: {name}",
 ファイル=discord。file（image_path）
            )
 瀹ノクスン:
 イハヤトラ シ シネッ。レスポンス。send_message ウーシン ロチマ ス ()
 content=f"dificedsa leat Name precous no'su long "DIFF"/diffidsa Leat Name「{ は見ます。limaimaringnt 出社ま し た。
            )
 elif nは、なしは、ハlimaisernancを出発:
 #指Sahzu田竜Go乃竜龍ヲ 表竜
 image_path = get_image_by_index（user_id、n）
 if image_path:
 イ ミ ヒ ノトラ シ シニ？リィー ーニーイー シィー。莠ャ驛ス_メッ ぉーあぃー ゥーー シーー シーー ノ シー（()
 コンテンツ=f の{n + 1}ず mime no'su n。ゥーゥゥゥ アウウーズリーヅ シマサ。、
 涔ァハ =discord。file（image_path）
            )
 瀹ノ ぢ？、まあ:
 イ ミ ヒ ノトラ シ シニ？リー ーニーイーシー。send_message ゥーシー シーシー シーノ シーー（sechais）Milinichi ノイ イック ()
 content=f{n + 1}ず mime no'su n。y 。涔 Riri dun no noishedkita Rich, シ ニイイ リ リ ウ ニニェーマッ ニシニョン。」
            )
 瀹ノ ぢ？、まあ:
 # ゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥ
 user_images = get_user_images（user_id）
 user_images の 莠の合体:
 瀹？[]
 idx neuranate（user_images） neurano-ahauser img:
 瀹？ー アーリーイ ティィ。瀹？ー アーイティ。append（f"{idx + 1}: {os。涔 santhbasename（img）}」
            
 瀹？ー アーイティ。蛟龍(「\no li la noronerun no dou no dou su kannoinoron no dou no du sukukima su」です)
 イ ミ ヒ ノトラ シ シニ？リー ーニーイーシー。send_message ゥーシー シーシー シノ シー（セチャイス） ミニニ ノイ イ。 ()
 コンテンツ="\n。"join（ 怪っとん？assortーa） 、
 涔ァハ =[不和。ユーザー_画像] の の ゙ァァイ （）imgfor img 、
 ephemeral=true
            )
 瀹ノ ぢ？、まあ:
 イ ミ ヒ ノトラ シ シニ？リィー ーニーイー シィー。莠信_メッ トアルァイ ゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥゥリー ーニーイーシー。send_message ゥーシー シーシー シノ シー（セチャイス） ミニニ ノイ イ。 ()
 content= 「RECOMENT sonssa reataizu MRIVELas a Ribiamoushent」。
            )


@ツ リィー。"description" dificationshitenaloigu ime之 涔之 owosushima su。n owo0ni suurkoto prepression suzu det no's my su。「」
非同期 デフ delete（interaction: discord。イ ハ ミノトラ シ シニ シ,n: int）:
 user_id =  Ihe MITolaza シ シニ。ゥーーーーー。

 n == 0 の 勺里 合体:
 #suzu du no 'no' no 'no' no 'o ousonousu suurenu allions
 cretai_ sukuai det_images（user_id）
 イ ミ ノトラ シ シニ？リー ーニーイーシー。send_message ゥーサー ゥーシー シノーシー ミニニ ノイ サ ()
 content=' RECITION sonssa re diteiur suzu do no'su might oushumashiat。、
 ephemeral=true
        )
 瀹ノ ぢ？、まあ:
 # ゥーるーるーリーリーのRECION ゥーウーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンノーンんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこんのこん
 image_path = get_image_by_index（user_id、

 もし image_path:
 # 莠の瀹 Chur utu urae ゥ ヲ ヲ ヅ シ 出現 んんえい
 = ou obulo DeleteConfirmationView（image_path、 user_id）
 イ ミ ノトラ シ シニ？リー ーニーイーシー。send_message ゥーサー ゥーサー シノ シー ミニニ ノイ イ。 ()
 コンテンツ=f "ju Shriv「"{オス。涔さんbasename（image_path）}」 oushuma su ka？、
 涔ァハ =discord。file（image_path） 、
 view=view 、
 ephemeral=true
            )
 瀹ノ チッ、まあ:
 イ ミ ヒノトラ シ シニ？リー スーニャス。send_message ゥーシー シノシー（she）ハニチ ノイ サ ()
 content=f{n + 1}zu mime no'su might hl sons wens Shimaimownanc.,
 ephemeral=true
            )

キー: 涔_ALAAI-ゾー()
ラ ミーアアアアー オービーチー ヒトー。嬴 れ(トーーーーー 、 瀹ー)
