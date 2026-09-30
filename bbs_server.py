#!/usr/bin/env python3
"""
Local streaming server for Blueprint Business Service offline player.
Proxies Bunny CDN streams with the required Referer header so video plays without login.
"""
import http.server
import socketserver
import urllib.request
import urllib.error
import re
import os
import sys

PORT = 5500
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "offline_site")
CDN_BASE = "https://vz-b7e89a3b-a06.b-cdn.net"

class BBSHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path.startswith("/video-proxy/"):
            self.handle_video_proxy()
        else:
            super().do_GET()

    def handle_video_proxy(self):
        # Path format: /video-proxy/<video_id>/<subpath...>
        match = re.match(r"^/video-proxy/([a-zA-Z0-9_\-]+)/(.*)$", self.path)
        if not match:
            self.send_error(400, "Invalid proxy path")
            return

        video_id = match.group(1)
        subpath = match.group(2)
        target_url = f"{CDN_BASE}/{video_id}/{subpath}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://blueprintbusinessservice.com/",
            "Origin": "https://blueprintbusinessservice.com"
        }

        # Forward Range header for video seeking
        if "Range" in self.headers:
            headers["Range"] = self.headers["Range"]

        req = urllib.request.Request(target_url, headers=headers)
        try:
            resp = urllib.request.urlopen(req, timeout=15)
            content_type = resp.headers.get("Content-Type", "application/octet-stream")
            content = resp.read()

            # If it's an m3u8 playlist, rewrite relative URLs to use /video-proxy/<video_id>/
            if "mpegurl" in content_type.lower() or subpath.endswith(".m3u8"):
                text = content.decode("utf-8", errors="ignore")
                lines = text.splitlines()
                new_lines = []
                current_dir = "/".join(subpath.split("/")[:-1])
                for line in lines:
                    line_str = line.strip()
                    if line_str and not line_str.startswith("#"):
                        if line_str.startswith("http"):
                            new_lines.append(line_str)
                        else:
                            if current_dir:
                                resolved = f"/video-proxy/{video_id}/{current_dir}/{line_str}"
                            else:
                                resolved = f"/video-proxy/{video_id}/{line_str}"
                            new_lines.append(resolved)
                    else:
                        new_lines.append(line)
                content = "\n".join(new_lines).encode("utf-8")
                content_type = "application/vnd.apple.mpegurl"

            self.send_response(resp.status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Access-Control-Allow-Origin", "*")
            for h in ["Content-Range", "Accept-Ranges"]:
                if resp.headers.get(h):
                    self.send_header(h, resp.headers.get(h))
            self.end_headers()
            self.wfile.write(content)

        except urllib.error.HTTPError as e:
            self.send_error(e.code, f"Upstream error: {e.reason}")
        except Exception as e:
            self.send_error(500, f"Proxy error: {str(e)}")

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), BBSHandler) as httpd:
        print(f"BBS Local Server running at http://127.0.0.1:{PORT}/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    run()
