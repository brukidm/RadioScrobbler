import vlc
import time
import aiohttp
import pylast
import asyncio
import re
from time import gmtime, strftime

url = ""
API_KEY = ""
API_SECRET = ""
username = ""
password_hash = pylast.md5("pwd")
network = pylast.LastFMNetwork(api_key=API_KEY, api_secret=API_SECRET,
                               username=username, password_hash=password_hash)

async def capture_stream(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={"Icy-MetaData": "1"}, timeout=None) as resp:
            skip = int(resp.headers["icy-metaint"])
            while True:
                data = await resp.content.readexactly(skip) #preskok
                if not data:
                    break
                meta_len = await resp.content.readexactly(1)
                if not meta_len:
                    break
                meta_len = meta_len[0] * 16
                if meta_len == 0:
                    continue
                data = await resp.content.readexactly(meta_len)
                if not data:
                    break
                data = data.decode("utf-8", "ignore")
                data = "".join((c for c in data if c.isprintable()))
                data = data.split("=")[1]
                data = re.split(r' ?- ?', data[1:-2])
                if(data[0] != "Unknown"):
                    network.scrobble(artist=data[0], title=data[1], timestamp=int(time.time()))

instance = vlc.Instance('--input-repeat=-1', '--fullscreen')
player=instance.media_player_new()
media=instance.media_new(url)
player.set_media(media)
loop = asyncio.get_event_loop()
loop.create_task(capture_stream(url))
while True:
    player.play()
    loop.run_forever()
