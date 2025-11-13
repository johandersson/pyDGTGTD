#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick database check script"""

import os
from wxgtd.lib.appconfig import AppConfig
from wxgtd.model import db
from wxgtd.model import objects as OBJ

# Initialize database
config = AppConfig('wxgtd.cfg', 'wxgtd')
dbfile = db.find_db_file(config)
print(f"Database file: {dbfile}")
db.connect(dbfile)

# Create session
session = OBJ.Session()

# Query all data
tasks = session.query(OBJ.Task).all()
folders = session.query(OBJ.Folder).all()
contexts = session.query(OBJ.Context).all()
goals = session.query(OBJ.Goal).all()

print(f"\n=== DATABASE CONTENTS ===")
print(f"Tasks: {len(tasks)}")
print(f"Folders: {len(folders)}")
print(f"Contexts: {len(contexts)}")
print(f"Goals: {len(goals)}")

if tasks:
    print(f"\n=== RECENT TASKS ===")
    for task in tasks[-10:]:
        status = "✓" if task.completed else " "
        context = f"@{task.context.title}" if task.context else ""
        folder = f"[{task.folder.title}]" if task.folder else ""
        print(f"  [{status}] {task.title} {context} {folder}")

if folders:
    print(f"\n=== FOLDERS/PROJECTS ===")
    for folder in folders:
        print(f"  - {folder.title}")

if contexts:
    print(f"\n=== CONTEXTS ===")
    for context in contexts:
        print(f"  - {context.title}")

session.close()
