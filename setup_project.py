import os

files = [
    "main.py",
    "db.py",
    "matcher.py",
    "scraper.py",
    "ui.py",
    "utils.py",
    "requirements.txt"
]

for f in files:
    if not os.path.exists(f):
        open(f, "w").write("")

print("Project setup done 🚀")
