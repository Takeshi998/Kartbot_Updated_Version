import discord, re, psutil, os, subprocess, time, asyncio, shutil, urllib.request, json, pathlib, requests, datetime, aiohttp, math
from discord.ext import commands
from discord import Webhook, AsyncWebhookAdapter


class Player():
    def __init__(self, name, skin, color, spec):
        self.name = name
        self.skin = skin
        self.color = color
        self.spec = spec

players_s = [range(1,16)]
for x in range(1,16):
    players_s.insert(x, Player("", "default", "", True))

players_n = 0

with open(
    str(pathlib.Path(__file__).parent.absolute()) + "/kartbot_config.json", "r"
) as f:
    config = json.loads(f.read())

if not os.path.exists(config["server_folder_path"] + "tmp"):
    os.makedirs(config["server_folder_path"] + "tmp")

map_re = re.compile('Map is now "(.+)"')
node_re = re.compile(r"^\d+:\s+(.+) - \d+ - \d+")
node_ip_re = r"\*.+ has joined the game \(node {}\) \(([\d\.]+)[:\)]"
action_re = re.compile(
    r"^((\*.+ entered the game\.)|(\*.+ left the game)|(\*.+ has joined the game \(node \d+\))|(\*.+ renamed to [^\n]+)|(\*.+ became a spectator\.)|(.+ has finished the race\.)|(.+ ran out of time\.)|(The round has ended\.)|(Speeding off to level\.\.\.))"
)

bot = commands.Bot(command_prefix=config["prefix"], description=config["description"], case_insensitive=True)

last_log_line = 0

async def chat_bridge():
    global players_n
    global last_log_line
    async with aiohttp.ClientSession() as session:
        while True:

            try: ## TESTE PRA NAO CAIR O BRIDGE TODA HORA

                with open(f"{config['server_folder_path']}log.txt", "r") as f:
                    log = [l.strip() for l in f.readlines()]
                    if last_log_line != 0:
                        for line in log[last_log_line:]:
                            if action_re.match(line) is not None:
                                await bot.get_channel(config["chat_bridge_channel_id"]).send(
                                    discord.utils.escape_mentions(
                                        "*"
                                        + re.search(action_re, line).group(1).replace("*", "")
                                        + "*"
                                    )
                                )
                with open(f"{config['server_folder_path']}log.txt", "r") as f:
                    log = [l.strip() for l in f.readlines()]
                    if last_log_line != 0:
                        for line in log[last_log_line:]:
                            if line.startswith("[HITFEED] "):
                                await bot.get_channel(config["chat_bridge_channel_id"]).send(
                                    "_" + line[10:].replace("_", "\_").replace("*","\*") + "_"
                                )

                            elif line.startswith("Map is now"):
                                mapname = (
                                        line.split(":")[1]
                                        .replace("\"", "")
                                        )
                                mapid = (
                                        line.split(":")[0]
                                        .replace("Map is now \"","")
                                        )
                                embed = discord.Embed(color=0x000099E1)
                                embed.title = "Map is now " + mapid + ":" + mapname
                                embed.set_image(url="http://srb2kbr.com/static/images/" + mapid + "-kart.png")
                                embed.url = "http://srb2kbr.com/maps/" + mapid + ":" + mapname
                                embed.url = embed.url.replace(" ", "%20")
                                try:
                                    await bot.get_channel(
                                        config["chat_bridge_channel_id"]
                                    ).send(embed=embed)
                                except Exception as e:
                                    print(str(e))
                                    continue
                            elif line.startswith("<") and not line.startswith("<~SERVER> [D]"):
                                    webhook_avatar_url = config["webhook_base_avatar_url"] + "default.png"
                                    usrname = (
                                            line.split(">")[0]
                                            .replace("<", "")
                                    )
                                    msg = (
                                            line.split(">")[1]
                                            .replace("@everyone","~~@~~everyone")
                                            .replace("@here","~~@~~here")
                                            .replace("_", "\_")
                                            .replace("*", "\*")
                                            .replace("`", "\`")
                                    ) 
                                    for x in range(1,16):
                                        if (players_s[x].name == usrname or "@" + players_s[x].name == usrname) and not players_s[x].spec:
                                            webhook_avatar_url = webhook_avatar_url[:-11] + players_s[x].skin + "_" + players_s[x].color + ".png"
                                            break

                                    webhook = Webhook.from_url(config["webhook_url"], adapter=AsyncWebhookAdapter(session))
                                    try:
                                        await webhook.send(msg, username=usrname, avatar_url=webhook_avatar_url)
                                    except Exception as e:
                                        print(str(e))
                                        continue
                            elif line.startswith("*") and line.endswith(")"):
                                players_n += 1
                                if players_n == 1:
                                    players_s[1].spec = False
                            elif line.startswith("*") and line.endswith("left the game"):
                                players_n -= 1
                            elif line.startswith("*") and line.endswith("entered the game."):
                                name = line[:-18][1:]
                                for x in range(1,16):
                                    if players_s[x].name == name:
                                        players_s[x].spec = False
                                        break
                            elif line.startswith("*") and line.endswith("became a spectator."):
                                name = line[:-20][1:]
                                for x in range(1,16):
                                    if players_s[x].name == name:
                                        players_s[x].spec = True
                                        break
                                
                            elif line.startswith("[CHAR] "):
                                color = line.split("[CHAR_COLOR] ")[1].split(" [")[0]
                                skin = line.split("[CHAR_SKIN] ")[1].split(" [NUMBER]")[0]
                                name = line.split("[NAME] ")[1]
                                num = int(line.split("[NUMBER]")[1].split("[NAME]")[0])
                                players_s[num].name = name
                                players_s[num].skin = skin
                                players_s[num].color = color
                            elif line.startswith("[RESULTS] "):
                                with open(f"{config['server_folder_path']}log.txt", "r") as f:
                                    log = f.read().split("\n")[::-1]
        
                                data = {
                                    "map": "???",
                                    "players": [],
                                }
        
                                players = list(
                                    filter(
                                        lambda x: x[-1] == "false" and x[-2] == "false",
                                        [player.split(":") for player in line.split(";")[1:-1]],
                                    )
                                )
                                for player in players:
                                    player[3] = int(player[3])
                                contest = list(
                                    sorted(
                                        filter(lambda x: x[3] != 0, players), key=lambda x: x[3]
                                    )
                                )
                                no_contest = list(filter(lambda x: x[3] == 0, players))
                                players = contest + no_contest
                                results_left = []
                                results_right = []
                                for i, player in enumerate(players):
                                    node = int(player[0])
                                    time = int(player[3])
                                    place = min(i, len(contest)) + 1
                                    name = player[1]
        
                                    results_left.append(f"{place}. {name}")
                                    if time != 0:
                                        data_player = {
                                            "name": name,
                                            "time": time,
                                            "place": place,
                                        }
        
                                        for line in log:
                                            match = re.compile(node_ip_re.format(node)).match(
                                                line
                                            )
                                            if match is not None:
                                                data_player["ip"] = match.group(1)
                                                break
        
                                        data["players"].append(data_player)
        
                                        minutes = int(time / 35 / 60)
                                        seconds = int(time / 35 % 60)
                                        hundredths = int((time / 35) % 1 * 100)
                                        results_right.append(
                                            f"{minutes}' {seconds}'' {hundredths}"
                                        )
                                    else:
                                        results_right.append("-")
        
                                embed = discord.Embed(color=0x00FF000)

                                embed.add_field(
                                    name="Resultados",
                                    value="\n".join(results_left),
                                    inline=True,
                                )
                                embed.add_field(
                                    name="\u200B",
                                    value="\n".join(results_right),
                                    inline=True,
                                )
                                try:
                                    await bot.get_channel(
                                        config["chat_bridge_channel_id"]
                                    ).send(embed=embed)
                                except Exception as e:
                                    print(str(e))
                                    continue
        
                                mode = "???"
                                for line in log:
                                    if line.startswith("[GAMETYPE] "):
                                        mode = line.split(" ")[1]
                                        break
        
                                if mode == "Vanilla":
                                    for line in log:
                                        match = map_re.match(line)
                                        if match is not None:
                                            data["map"] = match.group(1)
                                            break
        
                                    await asyncio.sleep(1)
        
                    last_log_line = len(log)
        
                await asyncio.sleep(2)

            except Exception: ## TESTE PRA NAO CAIR O BRIDGE TODA HORA
                pass          ## TESTE PRA NAO CAIR O BRIDGE TODA HORA


async def delete_tmp():
    while True:
        #await bot.change_presence(activity=discord.Game(name="srb2kbr.com"))
        files = [
            config["server_folder_path"] + "tmp/" + f
            for f in os.listdir(config["server_folder_path"] + "tmp")
        ]
        files.sort(key=os.path.getctime)
        for f in files[:-3]:
            os.system("rm " + f)
        await asyncio.sleep(10)


@bot.event
async def on_message(message):
    if message.channel.id == config["chat_bridge_channel_id"]:
        if not message.author.bot:
            text = (
                message.clean_content.replace('"', "")
                .replace("ç", "c")
                .replace("^", "")
                .replace("\n", "")
                .replace(";", "")
            )
            path = config["server_folder_path"] + f"tmp/tmp{message.id}.cfg"
            with open(path, "w") as f:
                f.write(f"say [D] {message.author.name}: {text}")
            os.system(
                f"screen -S {config['screen_name']} -p 0 -X stuff \"exec tmp{message.id}.cfg^M\""
            )
    else:
        await bot.process_commands(message)


def is_admin(ctx):
    for role in ctx.author.roles:
        if role.name in config["admin_roles"]:
            return True
    return False


bridge_running = False


@bot.event
async def on_ready():
    global bridge_running

    print(f"Conectado como {bot.user.name} (id {bot.user.id})")
    if config["chat_bridge"] and not bridge_running:
        bot.loop.create_task(chat_bridge())
        bot.loop.create_task(delete_tmp())
        bridge_running = True


@bot.command(help="Manda la IP del servidor")
async def ip(ctx):
    await ctx.send(config["ip_message"])



@bot.command(help="Reinicia el servidor", checks=[is_admin])
async def restart(ctx):
    os.system(f"pkill {config['server_executable_name']}")
    if config["enable_dkartconfig_corruption_workaround"]:
        try:
            shutil.copyfile(
                config["backup_dkartconfig_path"], config["dkartconfig_path"]
            )  # copies config backup over original config file, incase the original file gets corrupted
        except FileNotFoundError:
            print("No se puede copiar la copia de seguridad de dkartconfig")
    if config["enable_log_backup"]:
        try:
            shutil.copyfile(
                config["log_path"], config["backup_log_path"]
            )  # creates a backup of the log, so it can be analyzed after a server restart
        except FileNotFoundError:
            print("No se puede copiar la copia de seguridad de dkartconfig")
    os.system(
        f"screen -dmS {config['screen_name']} {config['server_executable_name']} {config['server_executable_args']}"
    )
    await ctx.send("Servidor reiniciado")


@bot.command(
    help="Ejecuta un comando en el servidor", checks=[is_admin], aliases=["comando", "cmd"]
)
async def command(ctx, *, cmd):
    # filtro retirado porque so vai ser executado dentro do jogo 
    # text = cmd.replace('"', "").replace("^", "").replace("\n", "").replace(";", "") 
    path = config["server_folder_path"] + f"tmp/tmp{ctx.message.id}.cfg"
    with open(path, "w") as f:
        f.write(cmd)
    os.system(
        f"screen -S {config['screen_name']} -p 0 -X stuff \"exec tmp{ctx.message.id}.cfg^M\""
    )
    await ctx.send("Comando ejecutado")

@bot.command(
    help="Enviar información sobre el servidor y los jugadores conectados",
    aliases=["info", "players"],
)
async def status(ctx, *, server=None):
    status = "ON"
    uptime = 0 
    if server:
        if server.lower().startswith("vanilla"):
            server_url = "http://srb2kbr.com/api/server_browser?ip=tocadorio.ddns.net&port=30100"
        if server.lower().startswith("battle") or server.lower().startswith("batalha"):
            server_url = "http://srb2kbr.com/api/server_browser?ip=tocadorio.ddns.net&port=30200"
        if server.lower().startswith("tsr"):
            server_url = "http://srb2kbr.com/api/server_browser?ip=tocadorio.ddns.net&port=30300"
        if server.lower().startswith("juice") or server.lower().startswith("suco"):
            server_url = "http://srb2kbr.com/api/server_browser?ip=srb2k.mooo.com&port=5029"
        with urllib.request.urlopen(server_url) as url:
            data = json.loads(url.read().decode())
            playerslist = '\u200B'
            playerlist = data['players']['list']
            x = 0
            for i in playerlist:
                pythonbruh = i['team']
                if (pythonbruh == "Playing"):
                    playerslist += "· " + str(i['name']) + "\n"
                else:
                    playerslist += "· " + "*" + str(i['name']) + "*\n"
            battleembed = discord.Embed(color=0x00FF00)
            battleembed.set_image(url="http://srb2kbr.com/static/images/" + data['level']['name'] + "-kart.png")
            battleembed.add_field(
                name = "Jugadores " + str(data['players']['count']) + "/" + str(data['players']['max']),
                value = playerslist,
                inline = False,
            )
            battleembed.add_field(name="Mapa Actual", value=data['level']['name'] + ": " + data['level']['title'], inline=True)
            await ctx.reply(embed=battleembed, mention_author=False)
            return
    try:
        pid = int(
            subprocess.check_output(["pidof", config["server_executable_name"]]).split(
                b" "
            )[0]
        )
        process = psutil.Process(pid)
        uptime = time.time() - process.create_time()
    except subprocess.CalledProcessError:
        status = "OFF"

    state = 0
    players = []
    specs = []
    map_ = "???"
    mode = "Carrera"

    if status == "ON":
        os.system(
            f"screen -S {config['screen_name']} -p 0 -X stuff \"nodes^Mversion^M\""
        )

        await asyncio.sleep(0.5)

        for _ in range(5):
            with open(f"{config['server_folder_path']}log.txt", "r") as f:
                log = f.read().split("\n")[::-1]
                state = 0
                for line in log:
                    if state == 0:
                        if line.startswith("SRB2Kart"):
                            state = 1
                    elif state == 1:
                        match = node_re.match(line)
                        if match is not None:
                            if line[-1] == ")":
                                specs.append(match.group(1))
                            else:
                                players.append(match.group(1))
                        elif line.startswith("$nodes"):
                            state = 2
                    elif state == 2:
                        for line in log:
                            match = map_re.match(line)
                            if match is not None:
                                map_ = match.group(1)
                                break
                        break
                if state == 2:
                    break
                else:
                    continue

        with open(f"{config['server_folder_path']}log.txt", "r") as f:
            log = f.read().split("\n")[::-1]
            for line in log:
                if line.startswith("[GAMETYPE] "):
                    mode = line.split(" ")[1]
                    break

    else:
        state = 2

    if state == 2:
        mapid = map_.split(":")[0]

        if len(players) + len(specs) == 0:
            formatted_players = "\u200B"
        else:
            formatted_players = "· " + "\n· ".join(
                players + list(map(lambda x: f"*{x}*", specs))
            )
        formatted_uptime = (
            f"{int(uptime/60/60):02}:{int(uptime/60%60):02}:{int(uptime%60):02}"
        )

        embed = discord.Embed(color=0x00FF00 if status == "ON" else 0xFF0000)
        embed.set_image(url="http://srb2kbr.com/static/images/" + mapid + "-kart.png")
        embed.add_field(
            name="Estado", value="✅ Encendido" if status == "ON" else "❌ Apagado", inline=True
        )
        embed.add_field(name="Tiempo de actividad", value=formatted_uptime, inline=True)
        embed.add_field(name="\u200B", value="\u200B", inline=True)
        embed.add_field(name="CPU", value=f"{psutil.cpu_percent()}%", inline=True)
        embed.add_field(
            name="RAM", value=f"{psutil.virtual_memory().percent}%", inline=True
        )
        embed.add_field(name="\u200B", value="\u200B", inline=True)
        if status == "ON":
            embed.add_field(name="Modo de juego", value=mode, inline=False)
            embed.add_field(
                name=f"Jugadores {len(players)+len(specs)}/{config['server_max_players']}",
                value=discord.utils.escape_mentions(formatted_players),
                inline=False,
            )
            embed.add_field(name="Mapa Actual", value=map_, inline=True)

        await ctx.reply(embed=embed, mention_author=False)
    else:
        await ctx.reply("No se puede leer el log del servidor", mention_author=False)



@bot.command(help="Muestra una determinada tag")
async def tag(ctx, *, tag):
    LEFT_EMOJI = "\u25C0"
    RIGHT_EMOJI = "\u25B6"
    STOP_EMOJI = "\u23F9"
    ftag = (
            tag[7:]
            .replace("/","")
            .replace("*","")
            .replace("_","")
            .replace("|","")
            .replace("~","")
            )
    message = None
    first = True
    list_number2 = 1
    list_beg = 20
    if tag.startswith("list global"):
        while True:
            if tag[12:]:
                list_number = int(tag[12:])
            else:
                list_number = 1

            if list_number == 0:
                list_number = 1
            check_dirs = os.listdir(config["tag_path"])
            index = math.ceil(len(check_dirs) / list_beg)
            if (list_number > index):
                await ctx.reply("Pagina fora de alcance", mention_author=False)
                return

            dirs = os.listdir(config["tag_path"])[list_beg*(list_number-1):list_beg*list_number]
            tags = "" 
            for file in dirs: 
                tags += file + "\n"

            embed = discord.Embed(color=0x000099E1)
            embed.title = "Tags {0} / {1}".format(list_number, index)
            embed.description = tags
        
            if first:
                message = await ctx.reply(embed=embed)
                if index <= 1:
                    break

                for emoji in (LEFT_EMOJI, STOP_EMOJI, RIGHT_EMOJI):
                    await message.add_reaction(emoji)

                first = False
            else:
                check_dirs = os.listdir(config["tag_path"])
                index = math.ceil(len(check_dirs) / list_beg)
                if list_number2 < 1:
                    list_number2 = 1
                elif list_number2 > index:
                    list_number2 = index
                dirs = os.listdir(config["tag_path"])[list_beg*(list_number2-1):list_beg*list_number2]
                tags = "" 
                for file in dirs:
                    tags += file + "\n"

                embed.title = "Tags {0} / {1}".format(list_number2, index)
                embed.description = tags
                await message.edit(embed=embed)

            try:
                reaction, user = await ctx.bot.wait_for(
                    "reaction_add",
                    timeout=60,
                    check=lambda r, u: r.message.id == message.id
                    and str(r.emoji) in (LEFT_EMOJI, STOP_EMOJI, RIGHT_EMOJI)
                    and u.id != ctx.bot.user.id,
                )
            except asyncio.TimeoutError:
                break

            if str(reaction) == STOP_EMOJI:
                await message.remove_reaction(STOP_EMOJI, user)
                for emoji in (LEFT_EMOJI, STOP_EMOJI, RIGHT_EMOJI):
                    await message.remove_reaction(emoji, ctx.bot.user)
                return

            if str(reaction) == RIGHT_EMOJI:
                list_number2 += 1
                await message.remove_reaction(RIGHT_EMOJI, user)
            else:
                list_number2 -= 1
                await message.remove_reaction(LEFT_EMOJI, user)
    elif tag.startswith("list"):
        while True:
            if tag[5:]:
                list_number = int(tag[5:])
            else:
                list_number = 1

            if list_number == 0:
                list_number = 1

            dirs = os.listdir(config["tag_path"])
            tags = "" 
            i = 0
            for file in dirs:
                with open(config["tag_path"] + file, "r") as f:
                    author = f.read().split("\n")[0].strip()
                    if author.isnumeric and author != '':
                        if ctx.author.id == int(author):
                            tags += file + "\n"
                            i += 1

            index = math.ceil(i / list_beg)
            if index == 0:
                await ctx.reply("Usted no ah creado ninguna tag")
                return

            if (list_number > index):
                await ctx.reply("Pagina fora de alcance")
                return
            embed = discord.Embed(color=0x000099E1)
            embed.title = "Suas Tags {0} / {1}".format(list_number, index)
            embed.description = tags
        
            if first:
                message = await ctx.reply(embed=embed)
                
                if index <= 1:
                    break
                
                for emoji in (LEFT_EMOJI, STOP_EMOJI, RIGHT_EMOJI):
                    await message.add_reaction(emoji)

                first = False
            else:
                check_dirs = os.listdir(config["tag_path"])

                dirs = os.listdir(config["tag_path"])
                tags = "" 
                i = 0
                for file in dirs:
                    with open(config["tag_path"] + file, "r") as f:
                        author = f.read().split("\n")[0].strip()
                        if author.isnumeric and author != '':
                            tags += file + "\n"
                            i += 1

                if list_number2 < 1:
                    list_number2 = 1
                elif list_number2 > index:
                    list_number2 = index

                index = math.ceil(i / list_beg)
                embed.title = "Sus Tags {0} / {1}".format(list_number2, index)
                embed.description = tags
                await message.edit(embed=embed, mention_author=False)

            try:
                reaction, user = await ctx.bot.wait_for(
                    "reaction_add",
                    timeout=60,
                    check=lambda r, u: r.message.id == message.id
                    and str(r.emoji) in (LEFT_EMOJI, STOP_EMOJI, RIGHT_EMOJI)
                    and u.id != ctx.bot.user.id,
                )
            except asyncio.TimeoutError:
                break

            if str(reaction) == STOP_EMOJI:
                await message.remove_reaction(STOP_EMOJI, user)
                for emoji in (LEFT_EMOJI, STOP_EMOJI, RIGHT_EMOJI):
                    await message.remove_reaction(emoji, ctx.bot.user)
                return

            if str(reaction) == RIGHT_EMOJI:
                list_number2 += 1
                await message.remove_reaction(RIGHT_EMOJI, user)
            else:
                list_number2 -= 1
                await message.remove_reaction(LEFT_EMOJI, user)
    elif tag.startswith("create"):
        if config["bot_commands_channel_id"] == ctx.channel.id:
            if not os.path.exists(config["tag_path"] + ftag):
                if ctx.message.attachments:
                    with open(config["tag_path"] + ftag, "w") as f:
                        f.write(f"{ctx.author.id}\n{ctx.message.attachments[0].url}")
                        await ctx.reply("Tag: \"{0}\" creada.".format(ftag), mention_author=False);
                else:
                        await ctx.reply("No es posible crear un tag sin un archivo adjunto.", mention_author=False);
            else:
                await ctx.reply("Error: Tag: \"{0}\" ya creada.".format(ftag), mention_author=False);

    elif tag.startswith("delete"):
        if config["bot_commands_channel_id"] == ctx.channel.id:
            if os.path.exists(config["tag_path"] + ftag):
                with open(config["tag_path"] + ftag, "r") as f:
                    author = f.read().split("\n")[0].strip()
                    if author.isnumeric and author != '':
                        if ctx.author.id == int(author) or is_admin(ctx):
                            os.remove(config["tag_path"] + ftag)
                            await ctx.reply("Tag: \"{0}\" borrada.".format(ftag), mention_author=False)
                        else:
                            await ctx.reply("Sólo el autor de este tag puede eliminarla.", mention_author=False)
            else:
                await ctx.reply("Tag: \"{0}\" no existe.".format(ftag), mention_author=False)
    else:
        if os.path.exists(config["tag_path"] + tag.replace("/","")):
            with open(config["tag_path"] + tag.replace("/",""), "r") as f:
                content = f.read().split("\n")[1]
                await ctx.reply(content, mention_author=False)
        else:
            await ctx.reply("Tag: \"{0}\" no existe.".format(tag))

bot.run(config["token"])
