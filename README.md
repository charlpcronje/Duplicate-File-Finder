# Duplicate File Finder

## Description
Duplicate File Finder is a Python application designed to scan a folder and its subfolders for duplicate files. It keeps track of where each duplicate is located, sorts the files by size in descending order, and outputs the duplicates to a markdown document with links to each file. The application uses partial hashing for different file types to optimize performance.

## Features
- Scans folders and subfolders for duplicate files.
- Uses file size and hash values for efficient duplicate detection.
- Partial hashing for specific file types for optimized performance.
- Outputs duplicates to a markdown report with collapsible headings.
- Configurable CPU usage limit and recent folder management.
- Supports customization through a `.env` file.

## Requirements
- Python 3.x
- `psutil`
- `python-dotenv`

## Installation
1. Clone the repository:
```bash
git clone https://github.com/charlpcronje/Duplicate-File-Finder.git
cd Duplicate-File-Finder
```

2. Install the required Python packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project directory with the following content:
```dotenv
CPU_USAGE_LIMIT=15
MAX_RECENT_FOLDERS=20
CONFIG_FILE=config.json
OUTPUT_FILE=duplicate_files_report.md
HASH_PARTIAL_SIZES={
    "jpg": "5KB",
    "jpeg": "5KB",
    "png": "5KB",
    "gif": "5KB",
    "mp4": ["1MB", "1MB"],
    "avi": ["1MB", "1MB"],
    "mkv": ["1MB", "1MB"],
    "pdf": "50KB",
    "docx": "50KB",
    "txt": "50KB",
    "mp3": "100KB",
    "wav": "100KB",
    "flac": "100KB",
    "zip": "100KB",
    "rar": "100KB",
    "7z": "100KB"
}
```

## Usage
1. To scan a specific folder for duplicate files and generate a report, run the following command:
```bash
python duplicate_file_finder.py /path/to/folder
```

2. To choose from the last 20 recently scanned folders, run the script without any arguments:
```bash
python duplicate_file_finder.py
```

## Configuration
The application can be customized using a `.env` file. The following configurations are supported:

- **CPU_USAGE_LIMIT**: Limit the CPU usage of the application (default: 15%).
- **MAX_RECENT_FOLDERS**: The maximum number of recent folders to keep track of (default: 20).
- **CONFIG_FILE**: Path to the configuration file for storing recent folders (default: `config.json`).
- **OUTPUT_FILE**: Path to the output markdown file (default: `duplicate_files_report.md`).
- **HASH_PARTIAL_SIZES**: JSON string specifying partial hash sizes for different file types. Example:
```json
{
    "jpg": "5KB",
    "jpeg": "5KB",
    "png": "5KB",
    "gif": "5KB",
    "mp4": ["1MB", "1MB"],
    "avi": ["1MB", "1MB"],
    "mkv": ["1MB", "1MB"],
    "pdf": "50KB",
    "docx": "50KB",
    "txt": "50KB",
    "mp3": "100KB",
    "wav": "100KB",
    "flac": "100KB",
    "zip": "100KB",
    "rar": "100KB",
    "7z": "100KB"
}
```

## Roadmap
### Future Enhancements
1. **Support for Multiple Hashing Algorithms**:
    - Allow users to choose from different hashing algorithms (e.g., SHA-256, SHA-1) for better customization and potentially faster hashing.

2. **Customizable Output Format**:
    - Enable users to choose different output formats (e.g., JSON, HTML) for better integration with other tools and platforms.

3. **Parallel Processing**:
    - Implement parallel processing to speed up the scanning and hashing process further by distributing the workload across multiple threads or processes.

4. **Asynchronous I/O**:
    - Utilize asynchronous I/O operations to improve efficiency when dealing with a large number of file read operations.

5. **Disk I/O Optimization**:
    - Reduce the number of disk I/O operations by reading larger chunks of data at once or using memory-mapped files to improve performance.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request with your improvements.

## License
This project is licensed under the MIT License.


### `requirements.txt`

```plaintext
psutil
python-dotenv
```