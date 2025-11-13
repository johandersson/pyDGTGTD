#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script to reimport data and verify contexts and metadata."""

import os
import sys
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
_LOG = logging.getLogger(__name__)

# Add wxgtd to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wxgtd.lib import appconfig
from wxgtd.model import db, loader, objects


def delete_database():
    """Delete the existing database."""
    config = appconfig.AppConfig('wxgtd.cfg', 'wxgtd')
    config.load_defaults(config.get_data_file('defaults.cfg'))
    config.load()
    
    db_file = db.find_db_file(config)
    _LOG.info(f"Database file: {db_file}")
    
    if os.path.exists(db_file):
        _LOG.info(f"Deleting database: {db_file}")
        os.remove(db_file)
        _LOG.info("Database deleted successfully")
    else:
        _LOG.info("No database file found")
    
    return db_file


def import_json_file(json_file_path):
    """Import data from JSON file."""
    _LOG.info(f"Reading JSON file: {json_file_path}")
    
    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_data = f.read()
    
    # Import the data
    def progress_callback(progress, msg):
        _LOG.info(f"[{progress}%] {msg}")
    
    _LOG.info("Starting import...")
    result = loader.load_json(json_data.encode('utf-8'), progress_callback, force=True)
    _LOG.info(f"Import completed: {result}")
    
    return result


def verify_import():
    """Verify that contexts and metadata were imported correctly."""
    session = objects.Session()
    
    _LOG.info("\n" + "="*60)
    _LOG.info("VERIFICATION RESULTS")
    _LOG.info("="*60)
    
    # Check contexts
    contexts = session.query(objects.Context).all()
    _LOG.info(f"\nCONTEXTS: {len(contexts)} found")
    for ctx in contexts:
        _LOG.info(f"  - ID: {ctx.uuid[:8]}... | Title: {ctx.title} | Color: {ctx.bg_color} | Parent: {ctx.parent_uuid[:8] if ctx.parent_uuid else 'None'}...")
    
    # Check goals
    goals = session.query(objects.Goal).all()
    _LOG.info(f"\nGOALS: {len(goals)} found")
    for goal in goals:
        _LOG.info(f"  - ID: {goal.uuid[:8]}... | Title: {goal.title} | Archived: {goal.archived}")
    
    # Check folders
    folders = session.query(objects.Folder).all()
    _LOG.info(f"\nFOLDERS: {len(folders)} found")
    for folder in folders:
        _LOG.info(f"  - ID: {folder.uuid[:8]}... | Title: {folder.title}")
    
    # Check tasks
    tasks = session.query(objects.Task).all()
    _LOG.info(f"\nTASKS: {len(tasks)} found")
    
    # Sample tasks with contexts
    tasks_with_context = [t for t in tasks if t.context_uuid][:5]
    if tasks_with_context:
        _LOG.info(f"\nSample tasks with contexts:")
        for task in tasks_with_context:
            context = session.query(objects.Context).filter_by(uuid=task.context_uuid).first()
            context_title = context.title if context else "CONTEXT NOT FOUND!"
            _LOG.info(f"  - Task: {task.title[:50]} | Context: {context_title}")
    
    # Tasks without contexts
    tasks_without_context = [t for t in tasks if not t.context_uuid]
    _LOG.info(f"\nTasks without context: {len(tasks_without_context)}")
    
    # Check notebooks
    notebooks = session.query(objects.NotebookPage).all()
    _LOG.info(f"\nNOTEBOOKS: {len(notebooks)} found")
    for nb in notebooks:
        _LOG.info(f"  - ID: {nb.uuid[:8]}... | Title: {nb.title}")
    
    _LOG.info("\n" + "="*60)
    
    session.close()


def main():
    """Main function."""
    # Path to your JSON file
    json_file = input("Enter path to JSON file (or press Enter for default test data): ").strip()
    
    if not json_file:
        # Create test JSON with your data
        test_data = {
            "version": 3,
            "CONTEXT": [
                {
                    "ID": 6,
                    "UUID": "",
                    "PARENT": 0,
                    "CHILDREN": 0,
                    "CREATED": "2025-06-13 19:35:00.000",
                    "MODIFIED": "2025-06-13 19:35:00.000",
                    "TITLE": "@agenda",
                    "COLOR": -8876889,
                    "VISIBLE": 1
                },
                {
                    "ID": 8,
                    "UUID": "",
                    "PARENT": 0,
                    "CHILDREN": 0,
                    "CREATED": "2025-06-13 19:36:00.000",
                    "MODIFIED": "2025-06-16 12:45:00.000",
                    "TITLE": "@anywhere",
                    "COLOR": -7886984,
                    "VISIBLE": 1
                }
            ],
            "GOAL": [
                {
                    "ID": 1,
                    "UUID": "",
                    "PARENT": 0,
                    "CREATED": "2025-06-08 20:57:00.000",
                    "MODIFIED": "2025-06-08 20:57:00.000",
                    "TITLE": "TwT",
                    "NOTE": "",
                    "LEVEL": 2,
                    "ARCHIVED": 0,
                    "COLOR": -8876889,
                    "VISIBLE": 1
                }
            ],
            "TASK": []
        }
        
        json_file = "test_import_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2)
        _LOG.info(f"Created test data file: {json_file}")
    
    if not os.path.exists(json_file):
        _LOG.error(f"File not found: {json_file}")
        return 1
    
    try:
        # Step 1: Delete existing database
        db_file = delete_database()
        
        # Step 2: Reconnect to create new database
        _LOG.info("Creating new database...")
        db.connect(db_file, debug_sql=False)
        
        # Step 3: Import JSON data
        import_json_file(json_file)
        
        # Step 4: Verify import
        verify_import()
        
        _LOG.info("\n✓ Import test completed successfully!")
        return 0
        
    except Exception as e:
        _LOG.error(f"Error during import: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
