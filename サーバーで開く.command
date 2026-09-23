#!/bin/bash
# ダブルクリックすると、このフォルダを配る小さなサーバーが立ち上がり、
# ブラウザが開きます。iPad からは、表示される LAN のアドレスで開けます。
# 終わるときは、このターミナルの窓で Control+C。
cd "$(dirname "$0")" || exit 1
python3 build.py
PORT=8731
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)
echo
echo "────────────────────────────────────"
echo "  このMac      http://localhost:$PORT/"
[ -n "$IP" ] && echo "  iPadなど     http://$IP:$PORT/    （同じWi-Fiで）"
echo "  終了         Control + C"
echo "────────────────────────────────────"
echo
( sleep 1; open "http://localhost:$PORT/" ) &
python3 -c "
import http.server, socketserver, functools, os
os.chdir('$(pwd)')
H = functools.partial(http.server.SimpleHTTPRequestHandler)
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(('0.0.0.0', $PORT), H) as s:
    s.serve_forever()
"
