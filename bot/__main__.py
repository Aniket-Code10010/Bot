from . import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon.utils import get_peer_id

try:
    bot.start(bot_token=BOT_TOKEN)
except Exception as erc:
    log.info(str(erc))

FUTURE = []


@bot.on(events.NewMessage(incoming=True, pattern="^/start"))
async def strt(event):
    if str(event.sender_id) not in OWNER:
        return
    btn = [
        [Button.inline("RESTART BOT", data="restart")],
        [
            Button.inline("Start Every X min Promo", data="startpromo"),
            Button.inline("Stop Every X min Promo", data="stoppromo"),
        ],
        [
            Button.inline("Start Keyword Promo", data="kstartpromo"),
            Button.inline("Stop Keyword Promo", data="mkstoppromo"),
        ],
    ]
    await event.reply("Choose Options", buttons=btn)


@bot.on(events.NewMessage(incoming=True, pattern="^/help"))
async def help(e):
    msg = """
• `/start` - __Most Features Are Here__
• `/addpromo` - __This Will add Promo Massage__
• `/interval <in minutes>` - __To set Interval of promo__
• `/setkeyword <word>` - __To set keyword to trigger promo sender.__ **Default is** - `Over`
"""
    await e.reply(msg)


@bot.on(events.NewMessage(incoming=True, pattern="^/addpromo"))
async def addchh(event):
    if str(event.sender_id) not in OWNER:
        return
    chs = dB.get("PROMO_DATA") or []
    async with bot.conversation(event.sender_id, timeout=500) as cv:
        await cv.send_message(f"Send 1st Promotion Ad")
        repl = (await (await cv.get_response()).forward_to(STORAGE_CHANNEL)).id
        await cv.send_message(f"Send 2nd Promotion Ad")
        repl2 =  (await (await cv.get_response()).forward_to(STORAGE_CHANNEL)).id
        await cv.send_message(f"Send 3rd Promotion Ad")
        repl3 =  (await (await cv.get_response()).forward_to(STORAGE_CHANNEL)).id
        await cv.send_message(f"Send 4th Promotion Ad")
        repl4 =  (await (await cv.get_response()).forward_to(STORAGE_CHANNEL)).id
        await cv.send_message(f"Send 5th Promotion Ad")
        repl5 =  (await (await cv.get_response()).forward_to(STORAGE_CHANNEL)).id
        chs = [repl, repl2, repl3, repl4, repl5]
    dB.set("PROMO_DATA", chs)
    await event.reply("`Succesfully Added`")



@bot.on(events.NewMessage(incoming=True, pattern="^/interval"))
async def intt(event):
    if str(event.sender_id) not in OWNER:
        return
    try:
        inn = event.text.split()[1]
    except:
        return await event.reply("`Invalid Input`")
    dB.set("INTERVAL", int(inn))
    await event.reply("`Done.`")


@bot.on(events.NewMessage(incoming=True, pattern="^/setkeyword"))
async def sett(event):
    if str(event.sender_id) not in OWNER:
        return
    try:
        key = event.text.split(" ", maxsplit=1)[1]
    except:
        return await event.reply("`Invalid Input`")
    dB.set("SPECIAL_WORD", key)
    await event.reply("`Done.`")





async def on_new_post(e):
    x = MAIN_CHANNEL
    sp = dB.get("SPECIAL_WORD") or "over"
    th = await e.get_chat()
    id = get_peer_id(th)
    if id != x:
        return
    try:
        if sp.lower() in e.text.lower():
            promos = dB.get("PROMO_DATA") or []
            xn = random.choice(promos)
            msg = await bot.get_messages(STORAGE_CHANNEL, ids=xn)
            return await bot.send_message(MAIN_CHANNEL, msg)
    except Exception as ex:
        log.error(str(ex))


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("startpromo")))
async def _(e):
    xnx = dB.get("PROMO_DATA") or []
    if not xnx:
        return await e.reply("First Add Promo Msg")
    if not FUTURE:
        await e.reply("Successfully Started msg poster.")
        inter = dB.get("INTERVAL") or 30
        future = AsyncIOScheduler()
        future.add_job(on_every_min, "interval", minutes=inter, id="every_x_job")
        FUTURE.append(future)
        future.start()
    else:
        await e.reply("Msg post funcn already runningF")


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("stoppromo")))
async def _(e):
    if FUTURE:
        x = await e.reply("Trying to stop msg post func.")
        FUTURE[0].remove_job("every_x_job")
        FUTURE.clear()
        await x.edit("`Done.`")
    else:
        await e.reply("Post func is not running.")

@bot.on(events.callbackquery.CallbackQuery(data=re.compile("kstartpromo")))
async def _(e):
    xnx = dB.get("PROMO_DATA") or []
    if not xnx:
        return await e.reply("First Add Promo Msg")
    if not dB.get("KEYPROMO"):
        await e.reply("Successfully Started msg poster.")
        try:
            bot.add_event_handler(on_new_post, events.NewMessage())
        except:
            pass
        dB.set("KEYPROMO", True)
    else:
        await e.reply("Msg post funcn already runningF")

@bot.on(events.callbackquery.CallbackQuery(data=re.compile("mkstoppromo")))
async def _(e):
    if dB.get("KEYPROMO"):
        x = await e.reply("Trying to stop msg post func.")
        try:
            bot.remove_event_handler(on_new_post)
        except:
            pass
        dB.delete("KEYPROMO")
        await x.edit("`Done.`")
    else:
        await e.reply("Post func is not running.")


@bot.on(events.callbackquery.CallbackQuery(data=re.compile("restart")))
async def restart(event):
    x = await event.reply("`Restarting...`")
    dB.set("RESTART", [x.id, x.chat_id])
    os.execl(sys.executable, sys.executable, "-m", "bot")

 
async def on_every_min():
    try:
        promos = dB.get("PROMO_DATA") or []
        xn = random.choice(promos)
        msg = await bot.get_messages(STORAGE_CHANNEL, ids=xn)
        await bot.send_message(MAIN_CHANNEL, msg)
    except Exception as error:
        log.error(str(error))


async def onstart():
    try:
        xx = dB.get("RESTART")
        xxx = dB.get("KEYPROMO")
        if xx:
            x = await bot.get_messages(xx[1], ids=xx[0])
            await x.edit("`Restarted`")
            dB.delete("RESTART")
        if xxx:
            dB.delete("KEYPROMO")
    except BaseException:
        dB.delete("RESTART")
        dB.delete("KEYPROMO")



log.info("Started bot")
bot.loop.run_until_complete(onstart())
bot.run_until_disconnected()
