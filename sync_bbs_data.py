#!/usr/bin/env python3
"""
1-Click Sync Script for Coach Adib / Blueprint Business Service.
Pulls newly published lessons, notes, and videos from the Coach Adib API (https://coachadib.com/)
and regenerates the offline site.
"""
import urllib.request
import json
import os
import glob
import re

def get_auth_token():
    # Attempt to extract token from local Chrome profile
    ldb_files = glob.glob(".chrome-profile/Default/Local Storage/leveldb/*.ldb") + \
                glob.glob(".chrome-profile/Default/Local Storage/leveldb/*.log")
    for f in ldb_files:
        try:
            with open(f, "rb") as fh:
                data = fh.read()
                tokens = re.findall(rb"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9\.[a-zA-Z0-9_\-\.]+", data)
                if tokens:
                    return tokens[0].decode("utf-8")
        except Exception:
            pass
    # Fallback default cached token
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuYWltbXVsbXVraW5AZ21haWwuY29tIiwiZXhwIjoxNzk4NDUwMDUzLCJpYXQiOjE3OTA2NzQwNTMsInNzb193b3Jrc3BhY2VzIjpbXSwiYXBwX3VzZXJfYXV0aF9wcm9vZiI6IjBkNGRjOTk2ZmM0M2Y3OWNjMTMzNWYwNDJiZTNiNmUxOGE3Y2NkZGIxNDQyMzE1MDk3OTRiZmNhZmUxMmM2N2EiLCJhcHBfdXNlcl9qd3RfdjIiOiJleUpoYkdjaU9pSklVekkxTmlJc0luUjVjQ0k2SWtwWFZDSjkuZXlKemRXSWlPaUp1WVdsdGJYVnNiWFZyYVc1QVoyMWhhV3d1WTI5dElpd2laWGh3SWpveE56azRORFV3TURVekxDSnBZWFFpT2pFM09UQTJOelF3TlRNc0luTnpiMTkzYjNKcmMzQmhZMlZ6SWpwYlhTd2lZWEJ3WDNWelpYSmZZWFYwYUY5d2NtOXZaaUk2SWpCa05HUmpPVGsyWm1NME0yWTNPV05qTVRNek5XWXdOREppWlROaU5tVXhPR0UzWTJOa1pHSXhORFF5TXpFMU1EazNPVFJpWm1NaFptVXhNbU0yTjJFaWZRLllMV0dHMDVPTUhOR1E0akQ2MmFUcUhWTlRQSC01bVY0VExORnBROC01ak0ifQ.mMeh3Vc1u9SWSMfT9QOc3xC1EA8-6scFFFacMmh3XH8"

def sync():
    token = get_auth_token()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    entities = ["Program", "Course", "Chapter", "Module", "Level"]
    data = {}
    print("Connecting to Coach Adib API (https://coachadib.com/)...")

    for ent in entities:
        url = f"https://coachadib.com/api/entities/{ent}"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data[ent] = json.loads(resp.read().decode("utf-8"))
                print(f"  ✓ Synced {ent}: {len(data[ent])} records")
        except Exception as e:
            print(f"  ✗ Error syncing {ent} from coachadib.com: {e}")
            # Fallback to blueprintbusinessservice.com if needed
            try:
                fb_url = f"https://blueprintbusinessservice.com/api/entities/{ent}"
                req = urllib.request.Request(fb_url, headers=headers)
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data[ent] = json.loads(resp.read().decode("utf-8"))
                    print(f"  ✓ Fallback synced {ent}: {len(data[ent])} records")
            except Exception as fe:
                print(f"  ✗ Fallback error for {ent}: {fe}")

    if data.get("Module"):
        with open("bbs_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("✓ bbs_data.json successfully updated from Coach Adib!")
        
        # Regenerate offline site
        import generate_offline_site
        generate_offline_site.build_offline_site()
        print("✓ Offline site refreshed with latest content!")
    else:
        print("Sync failed: No module data received.")

if __name__ == "__main__":
    sync()

