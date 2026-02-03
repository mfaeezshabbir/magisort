import os
import shutil
import argparse
import json
from pathlib import Path
from datetime import datetime

# Mapping of file extensions to folder names
EXTENSION_MAP = {
    # ... (same as before)
}

# The rest of the extensions from the previous step
EXTENSION_MAP.update({
    # Images
    '.jpg': 'Images', '.jpeg': 'Images', '.png': 'Images', '.gif': 'Images', 
    '.bmp': 'Images', '.svg': 'Images', '.webp': 'Images', '.ico': 'Images', 
    '.tif': 'Images', '.tiff': 'Images',
    
    # Documents
    '.pdf': 'Documents', '.doc': 'Documents', '.docx': 'Documents', '.txt': 'Documents', 
    '.rtf': 'Documents', '.xls': 'Documents', '.xlsx': 'Documents', '.ppt': 'Documents', 
    '.pptx': 'Documents', '.csv': 'Documents', '.md': 'Documents', '.epub': 'Documents', 
    '.pages': 'Documents',
    
    # Audio
    '.mp3': 'Audio', '.wav': 'Audio', '.aac': 'Audio', '.flac': 'Audio', 
    '.m4a': 'Audio', '.ogg': 'Audio',
    
    # Video
    '.mp4': 'Video', '.mkv': 'Video', '.mov': 'Video', '.avi': 'Video', 
    '.wmv': 'Video', '.flv': 'Video', '.webm': 'Video',
    
    # Archives
    '.zip': 'Archives', '.rar': 'Archives', '.7z': 'Archives', '.tar': 'Archives', 
    '.gz': 'Archives', '.bz2': 'Archives', '.xz': 'Archives',
    
    # Scripts & Programming
    '.py': 'Scripts', '.js': 'Scripts', '.ts': 'Scripts', '.jsx': 'Scripts', 
    '.tsx': 'Scripts', '.html': 'Scripts', '.css': 'Scripts', '.scss': 'Scripts', 
    '.cpp': 'Scripts', '.c': 'Scripts', '.h': 'Scripts', '.hpp': 'Scripts', 
    '.java': 'Scripts', '.go': 'Scripts', '.rs': 'Scripts', '.php': 'Scripts', 
    '.sh': 'Scripts', '.bat': 'Scripts', '.ps1': 'Scripts', '.rb': 'Scripts', 
    '.swift': 'Scripts', '.kt': 'Scripts', '.dart': 'Scripts', '.lua': 'Scripts',
    
    # Data & Config
    '.json': 'Data', '.xml': 'Data', '.yaml': 'Data', '.yml': 'Data', 
    '.toml': 'Data', '.ini': 'Data', '.env': 'Data', '.conf': 'Data', 
    '.sql': 'Data', '.db': 'Data', '.sqlite': 'Data',
    
    # GIS & Mapping
    '.kml': 'GIS_Data', '.kmz': 'GIS_Data', '.geojson': 'GIS_Data', 
    '.gpx': 'GIS_Data', '.shp': 'GIS_Data',
    
    # Executables & Packages
    '.exe': 'Executables', '.bin': 'Executables', '.deb': 'Executables', 
    '.rpm': 'Executables', '.msi': 'Executables', '.apk': 'Executables', 
    '.app': 'Executables', '.dmg': 'Executables', '.pkg': 'Executables',
    
    # Disk Images
    '.iso': 'Disk_Images', '.img': 'Disk_Images', '.vmdk': 'Disk_Images', 
    '.ova': 'Disk_Images',
    
    # Fonts
    '.ttf': 'Fonts', '.otf': 'Fonts', '.woff': 'Fonts', '.woff2': 'Fonts',
    
    # Others
    '.log': 'Logs', '.bak': 'Backups', '.tmp': 'Temporary',
})

HISTORY_FILE = ".organizer_history.json"

def organize_folder(target_path):
    """
    Organizes files in the given folder into subfolders based on their extensions.
    Records the moves into a history file for undo functionality.
    """
    path = Path(target_path)
    
    if not path.exists() or not path.is_dir():
        print(f"Error: '{target_path}' is not a valid directory.")
        return

    print(f"Organizing files in: {path.absolute()}")
    
    history = []
    
    for item in path.iterdir():
        if item.is_dir() or item.name == HISTORY_FILE:
            continue
            
        extension = item.suffix.lower()
        folder_name = EXTENSION_MAP.get(extension, 'Others')
        
        dest_dir = path / folder_name
        dest_dir.mkdir(exist_ok=True)
        
        try:
            dest_path = dest_dir / item.name
            
            # Handle naming conflicts
            if dest_path.exists():
                count = 1
                while True:
                    new_name = f"{item.stem}_{count}{item.suffix}"
                    dest_path = dest_dir / new_name
                    if not dest_path.exists():
                        break
                    count += 1
            
            original_path = str(item.absolute())
            new_path = str(dest_path.absolute())
            
            shutil.move(str(item), str(dest_path))
            history.append({"from": new_path, "to": original_path})
            print(f"Moved: {item.name} -> {folder_name}/")
        except Exception as e:
            print(f"Failed to move {item.name}: {e}")

    if history:
        with open(path / HISTORY_FILE, 'w') as f:
            json.dump(history, f, indent=4)
        print(f"\nSaved organization history to {HISTORY_FILE}")
    else:
        print("No files were moved.")

def undo_organization(target_path):
    """
    Reverses the last organization session using the history file.
    """
    path = Path(target_path)
    history_path = path / HISTORY_FILE
    
    if not history_path.exists():
        print(f"Error: No history file found in '{target_path}'. Nothing to undo.")
        return

    try:
        with open(history_path, 'r') as f:
            history = json.load(f)
        
        print(f"Undoing last organization in: {path.absolute()}")
        
        for move in history:
            src = Path(move["from"])
            dst = Path(move["to"])
            
            if src.exists():
                # Ensure destination directory exists (though it should be the parent)
                dst.parent.mkdir(exist_ok=True, parents=True)
                shutil.move(str(src), str(dst))
                print(f"Restored: {src.name} -> {dst.parent}")
            else:
                print(f"Warning: Could not find {src.name} to restore.")

        # Remove history file after successful undo
        history_path.unlink()
        
        # Optionally clean up empty folders created during organization
        # We only clean folders that are in our EXTENSION_MAP
        folders_to_check = set(EXTENSION_MAP.values())
        folders_to_check.add('Others')
        for folder in folders_to_check:
            folder_path = path / folder
            if folder_path.exists() and folder_path.is_dir() and not any(folder_path.iterdir()):
                folder_path.rmdir()
                print(f"Removed empty folder: {folder}/")
                
        print("\nUndo complete.")
    except Exception as e:
        print(f"An error occurred during undo: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize files in a folder into subfolders by type.")
    parser.add_argument("path", help="Path to the folder to organize")
    parser.add_argument("--undo", action="store_true", help="Undo the last organization session in the target folder")
    
    args = parser.parse_args()
    
    if args.undo:
        undo_organization(args.path)
    else:
        organize_folder(args.path)
