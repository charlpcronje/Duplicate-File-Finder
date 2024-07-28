import os
import hashlib
import json
import argparse
from pathlib import Path
from collections import defaultdict
import psutil
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants from .env file
CPU_USAGE_LIMIT = int(os.getenv("CPU_USAGE_LIMIT", 15))
MAX_RECENT_FOLDERS = int(os.getenv("MAX_RECENT_FOLDERS", 20))
CONFIG_FILE = os.getenv("CONFIG_FILE", "config.json")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "duplicate_files_report.md")
HASH_PARTIAL_SIZES = json.loads(os.getenv("HASH_PARTIAL_SIZES", "{}"))


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to calculate the hash of a file
def get_file_hash(file_path, hash_algo='md5', partial_sizes=None):
    hash_func = hashlib.new(hash_algo)
    try:
        with open(file_path, 'rb') as f:
            if partial_sizes:
                if isinstance(partial_sizes, list) and len(partial_sizes) == 2:
                    start_size = parse_size(partial_sizes[0])
                    end_size = parse_size(partial_sizes[1])
                    hash_func.update(f.read(start_size))
                    f.seek(-end_size, os.SEEK_END)
                    hash_func.update(f.read(end_size))
                else:
                    partial_size = parse_size(partial_sizes)
                    while chunk := f.read(partial_size):
                        hash_func.update(chunk)
            else:
                while chunk := f.read(8192):
                    hash_func.update(chunk)
    except Exception as e:
        logging.warning(f"Could not read file {file_path}: {e}")
        return None
    return hash_func.hexdigest()

def parse_size(size_str):
    size_str = size_str.lower()
    if size_str.endswith('kb'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('mb'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.isdigit():
        return int(size_str)
    return 0

# Function to group files by size
def group_files_by_size(root_folder):
    size_dict = defaultdict(list)
    folder_file_count = defaultdict(int)
    total_file_count = 0
    
    for foldername, subfolders, filenames in os.walk(root_folder):
        logging.info(f"Scanning folder: {foldername}")
        file_count = len(filenames)
        folder_file_count[foldername] += file_count
        total_file_count += file_count
        
        for filename in filenames:
            file_path = Path(foldername) / filename
            try:
                file_size = os.path.getsize(file_path)
                size_dict[file_size].append(file_path)
            except OSError as e:
                logging.warning(f"Could not access file {file_path}: {e}")

    return size_dict, folder_file_count, total_file_count

# Function to find duplicate files from groups of files with the same size
def find_duplicates(size_dict):
    duplicates = defaultdict(list)
    total_files = sum(len(files) for files in size_dict.values() if len(files) > 1)
    processed_files = 0
    
    def process_file(file_path):
        ext = file_path.suffix.lower().lstrip('.')
        partial_sizes = HASH_PARTIAL_SIZES.get(ext)
        file_hash = get_file_hash(file_path, partial_sizes=partial_sizes)
        return file_path, file_hash

    with ThreadPoolExecutor() as executor:
        futures = []
        for size, files in size_dict.items():
            if len(files) > 1:  # Only consider sizes with more than one file
                for file_path in files:
                    futures.append(executor.submit(process_file, file_path))

        hash_dict = {}
        for future in as_completed(futures):
            file_path, file_hash = future.result()
            if file_hash:
                if file_hash in hash_dict:
                    duplicates[file_hash].append(file_path)
                else:
                    hash_dict[file_hash] = file_path
            processed_files += 1
            print(f"Processed {processed_files}/{total_files} files for duplicates detection.", end='\r')

    return duplicates

# Function to sort duplicates by file size in descending order
def sort_duplicates_by_size(duplicates):
    sorted_duplicates = sorted(duplicates.items(), key=lambda item: -os.path.getsize(item[1][0]))
    return sorted_duplicates

# Function to generate markdown report
def generate_markdown_report(duplicates, output_file, folder_file_count, total_file_count):
    with open(output_file, 'w') as f:
        f.write(f"# Duplicate Files Report\n")
        f.write(f"Total files processed: {total_file_count}\n\n")
        
        # Folder size and file count
        f.write(f"## Folder Sizes and File Counts\n")
        for folder, count in folder_file_count.items():
            folder_size = sum(os.path.getsize(Path(folder) / file) for file in os.listdir(folder) if os.path.isfile(Path(folder) / file))
            f.write(f"### {folder} (Size: {folder_size} bytes, Files: {count})\n")
        
        for i, (file_hash, paths) in enumerate(duplicates):
            if len(paths) > 1:  # Ensure there are actually duplicates
                file_size = os.path.getsize(paths[0])
                f.write(f"# Duplicate Set {i+1} (Size: {file_size} bytes)\n")
                for path in paths:
                    depth = len(Path(path).parts) - 1
                    heading_level = min(6, depth)
                    f.write(f"{'#' * heading_level} {path}\n")
                    f.write(f"[Link to file]({path})\n\n")

# Function to limit CPU usage
def limit_cpu_usage():
    p = psutil.Process(os.getpid())
    p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    print(f"CPU usage limited to {CPU_USAGE_LIMIT}%")

# Function to read config file
def read_config():
    if not os.path.exists(CONFIG_FILE):
        return []
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

    
# Function to write config file
def write_config(folders):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(folders, f)

# Function to update the list of recent folders
def update_recent_folders(new_folder):
    folders = read_config()
    if new_folder in folders:
        folders.remove(new_folder)
    folders.insert(0, new_folder)
    if len(folders) > MAX_RECENT_FOLDERS:
        folders = folders[:MAX_RECENT_FOLDERS]
    write_config(folders)
    print(f"Updated recent folders with: {new_folder}")  # Added print statement
    

# Function to display recent folders and choose one
def choose_recent_folder():
    folders = read_config()
    if not folders:
        print("No recent folders found.")
        return None
    print("Choose a folder from the list below:")
    for i, folder in enumerate(folders, start=1):
        print(f"{i}. {folder}")
    choice = input("Enter the number of the folder to scan: ")
    try:
        choice = int(choice)
        if 1 <= choice <= len(folders):
            return folders[choice - 1]
    except ValueError:
        pass
    print("Invalid choice.")
    return None

# Main function
def main(root_folder):
    limit_cpu_usage()
    update_recent_folders(root_folder)
    size_dict, folder_file_count, total_file_count = group_files_by_size(root_folder)
    print(f"Total unique file sizes found: {len(size_dict)}")
    duplicates = find_duplicates(size_dict)
    print(f"Total duplicates found: {sum(len(paths) for paths in duplicates.values() if len(paths) > 1)}")
    sorted_duplicates = sort_duplicates_by_size(duplicates)
    generate_markdown_report(sorted_duplicates, OUTPUT_FILE, folder_file_count, total_file_count)
    logging.info(f"Duplicate files report generated: {OUTPUT_FILE}")
    print(f"Duplicate files report generated: {OUTPUT_FILE}")


# Usage example
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan for duplicate files and generate a report.")
    parser.add_argument("folder", nargs="?", help="The root folder to scan for duplicates.")
    args = parser.parse_args()
    
    if args.folder:
        root_folder = args.folder
    else:
        root_folder = choose_recent_folder()
    
    if not root_folder:
        print("No folder selected.")
    else:
        output_file = "duplicate_files_report.md"
        main(root_folder, output_file)


