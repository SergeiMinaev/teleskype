[main]
telegram_token = TOKEN
use_proxy = no
lang = en
python_path = /path/to/teleskype/virtualenv/bin/python

[bot]
name = bot
cmd_without_dash = no

[bot_cmd_aliases]
ping = ('ping', 'say pong')
help = ('help',)
cbr_currency = ('currency',)
stats = ('stats',)

[proxy]
proxy_type = socks5
login = login
password = password
hostname = example.com
port = 1080
