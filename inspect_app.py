
import re, json, urllib.request

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuYWltbXVsbXVraW5AZ21haWwuY29tIiwiZXhwIjoxNzk4NDUwMDUzLCJpYXQiOjE3OTA2NzQwNTMsInNzb193b3Jrc3BhY2VzIjpbXSwiYXBwX3VzZXJfYXV0aF9wcm9vZiI6IjBkNGRjOTk2ZmM0M2Y3OWNjMTMzNWYwNDJiZTNiNmUxOGE3Y2NkZGIxNDQyMzE1MDk3OTRiZmNhZmUxMmM2N2EiLCJhcHBfdXNlcl9qd3RfdjIiOiJleUpoYkdjaU9pSklVekkxTmlJc0luUjVjQ0k2SWtwWFZDSjkuZXlKemRXSWlPaUp1WVdsdGJYVnNiWFZyYVc1QVoyMWhhV3d1WTI5dElpd2laWGh3SWpveE56azRORFV3TURVekxDSnBZWFFpT2pFM09UQTJOelF3TlRNc0luTnpiMTkzYjNKcmMzQmhZMlZ6SWpwYlhTd2lZWEJ3WDNWelpYSmZZWFYwYUY5d2NtOXZaaUk2SWpCa05HUmpPVGsyWm1NME0yWTNPV05qTVRNek5XWXdOREppWlROaU5tVXhPR0UzWTJOa1pHSXhORFF5TXpFMU1EazNPVFJpWm1OaFptVXhNbU0yTjJFaWZRLllMV0dHMDVPTUhOR1E0akQ2MmFUcUhWTlRQSC01bVY0VExORnBROC01ak0ifQ.mMeh3Vc1u9SWSMfT9QOc3xC1EA8-6scFFFacMmh3XH8"
headers = {"User-Agent": "Mozilla/5.0", "Authorization": f"Bearer {token}", "Accept": "application/json"}

entities = ["Level", "Course", "Chapter", "Module", "User", "Team", "UserProgress", "Note", "Bookmark", "Feedback"]
data = {}
for ent in entities:
    try:
        req = urllib.request.Request(f"https://blueprintbusinessservice.com/api/entities/{ent}", headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data[ent] = json.loads(resp.read().decode("utf-8"))
            print(f"Saved {ent}: {len(data[ent]) if isinstance(data[ent], list) else type(data[ent])}")
    except Exception as e:
        print(f"Failed {ent}: {e}")

with open("bbs_data.json", "w", encoding="utf-8") as out:
    json.dump(data, out, ensure_ascii=False, indent=2)
print("bbs_data.json written!")
