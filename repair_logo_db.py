
# -*- coding: utf-8 -*-
"""
Logo Database Repair Script for M3U Editor
Fixes corrupted logos_db.json file
"""

import json
import os
import shutil
from datetime import datetime

def repair_logo_database():
    """Repair corrupted logos_db.json file"""
    
    logo_db_path = "logos_db.json"
    backup_path = f"logos_db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    print(f"Starting logo database repair...")
    
    # Create backup if file exists
    if os.path.exists(logo_db_path):
        try:
            shutil.copy2(logo_db_path, backup_path)
            print(f"✅ Backup created: {backup_path}")
        except Exception as e:
            print(f"⚠️  Warning: Could not create backup: {e}")
    
    # Try to repair the JSON file
    repaired_data = {}
    
    if os.path.exists(logo_db_path):
        print(f"Attempting to repair {logo_db_path}...")
        
        try:
            # Method 1: Try to load as-is
            with open(logo_db_path, 'r', encoding='utf-8') as f:
                repaired_data = json.load(f)
            print("✅ File was actually valid - no repair needed")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON Error: {e}")
            print("Attempting to repair...")
            
            # Method 2: Try to fix common JSON issues
            try:
                with open(logo_db_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remove null bytes and control characters
                content = content.replace('\x00', '')
                content = ''.join(char for char in content if ord(char) >= 32 or char in '\n\r\t')
                
                # Try to find the first valid JSON object
                brace_count = 0
                start_pos = content.find('{')
                
                if start_pos == -1:
                    raise ValueError("No JSON object found")
                
                end_pos = start_pos
                for i, char in enumerate(content[start_pos:], start_pos):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_pos = i + 1
                            break
                
                # Extract the valid JSON portion
                json_content = content[start_pos:end_pos]
                repaired_data = json.loads(json_content)
                
                print(f"✅ Successfully extracted {len(repaired_data)} logo entries")
                
            except Exception as e2:
                print(f"❌ Repair failed: {e2}")
                print("Creating fresh logo database...")
                repaired_data = {}
    
    else:
        print("No existing logo database found, creating new one...")
    
    # Write the repaired/new database
    try:
        with open(logo_db_path, 'w', encoding='utf-8') as f:
            json.dump(repaired_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Logo database repaired successfully")
        print(f"   Entries: {len(repaired_data)}")
        print(f"   Size: {os.path.getsize(logo_db_path):,} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to write repaired database: {e}")
        return False

def validate_logo_database():
    """Validate the logo database structure"""
    
    logo_db_path = "logos_db.json"
    
    if not os.path.exists(logo_db_path):
        print("❌ Logo database does not exist")
        return False
    
    try:
        with open(logo_db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            print("❌ Logo database is not a dictionary")
            return False
        
        # Validate structure
        valid_entries = 0
        invalid_entries = 0
        
        for channel_name, logo_data in data.items():
            if isinstance(channel_name, str):
                if isinstance(logo_data, (str, list)):
                    if isinstance(logo_data, list):
                        if all(isinstance(url, str) for url in logo_data):
                            valid_entries += 1
                        else:
                            invalid_entries += 1
                    else:
                        valid_entries += 1
                else:
                    invalid_entries += 1
            else:
                invalid_entries += 1
        
        print(f"✅ Logo database validation complete:")
        print(f"   Valid entries: {valid_entries}")
        print(f"   Invalid entries: {invalid_entries}")
        print(f"   Total size: {os.path.getsize(logo_db_path):,} bytes")
        
        return invalid_entries == 0
        
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    print("=== M3U Editor Logo Database Repair ===\n")
    
    # Step 1: Repair the database
    if repair_logo_database():
        print()
        # Step 2: Validate the repair
        validate_logo_database()
        print("\n🎉 Logo database repair completed!")
        print("\nYou can now restart the M3U Editor application.")
    else:
        print("\n❌ Logo database repair failed!")
        print("The application will still work but without logo functionality.")
    
    input("\nPress Enter to exit...")