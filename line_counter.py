#!/usr/bin/env python3
import os
import argparse
from typing import List, Dict, Any, Set, Optional

# --- Configuration ---
# Customize these for your project.

# Directories to skip during the scan.
DEFAULT_SKIP_DIRS = {
    '__pycache__', '.git', 'node_modules', 'venv', 'env', '.venv', '.env',
    'logs', '!backups'
}

# File extensions to skip, organized by category.
# The script generates an exclusion list in the report based on this structure.
DEFAULT_SKIP_EXTENSIONS_BY_CATEGORY = {
    "Document Files": {
        '.md', '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
        '.odt', '.ods', '.odp', '.rtf', '.txt', '.csv', '.tsv'
    },
    "Database Files": {
        '.db', '.sqlite', '.sqlite3', '.db3', '.mdb', '.accdb', '.sql',
        '.frm', '.myd', '.myi'
    },
    "Image Files": {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp',
        '.svg', '.ico', '.psd', '.ai', '.eps', '.raw', '.heic', '.heif',
        '.indd', '.cr2', '.nef', '.arw', '.dng'
    },
    "Archive/Compressed Files": {
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'
    },
    "Backup and Cache Files": {
        '.bak', '.tmp', '.swp', '.swo', '~'
    },
    "Binary/Compiled Files": {
        '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.class'
    },
    "System and Config Files": {
        '.ini', '.cfg', '.conf', '.log', '.lock', '.lnk'
    }
}

# Flatten the categorized extensions into a single set for efficient lookup.
DEFAULT_SKIP_EXTENSIONS = {
    ext for category in DEFAULT_SKIP_EXTENSIONS_BY_CATEGORY.values() for ext in category
}

def count_lines(filepath: str) -> int:
    """Count the number of lines in a file.
    
    Args:
        filepath: Path to the file
        
    Returns:
        int: Number of lines in the file, or 0 if file can't be read
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except (IOError, UnicodeDecodeError):
        # Return 0 if the file cannot be opened or read.
        return 0

def get_file_info(
    startpath: str,
    skip_dirs: Optional[Set[str]] = None,
    skip_extensions: Optional[Set[str]] = None
) -> List[Dict[str, Any]]:
    """Get information about all files in a directory tree.
    
    Args:
        startpath: Root directory to scan
        skip_dirs: Set of directory names to skip
        skip_extensions: Set of file extensions to skip (including leading dot)
        
    Returns:
        List of dictionaries with file information
    """
    if skip_dirs is None:
        skip_dirs = DEFAULT_SKIP_DIRS
    if skip_extensions is None:
        skip_extensions = DEFAULT_SKIP_EXTENSIONS
        
    file_info = []
    
    for root, dirs, files in os.walk(startpath, topdown=True):
        # Modify dirs in-place to prune the search space
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            # Skip hidden files (starting with '.'), __init__.py, and desktop.ini
            if file.startswith('.') or file == 'desktop.ini' or file == '__init__.py':
                continue
                
            # Get file extension and normalize to lowercase
            _, ext = os.path.splitext(file)
            ext = ext.lower()
            
            # Skip files with blacklisted extensions
            if ext in skip_extensions:
                continue
                
            filepath = os.path.join(root, file)
            # Create a consistent, forward-slash-based relative path
            rel_path = os.path.relpath(filepath, startpath).replace('\\', '/')
            
            # Skip files that are inaccessible
            try:
                size_kb = os.path.getsize(filepath) / 1024
            except OSError:
                continue
                
            line_count = count_lines(filepath)
            
            file_info.append({
                'path': rel_path,
                'lines': line_count,
                'size_kb': size_kb,
                'ext': ext[1:] if ext else 'none'  # Store extension without the dot
            })
    
    return sorted(file_info, key=lambda x: x['path'].lower())

def generate_markdown_table(file_info: List[Dict[str, Any]]) -> str:
    """Generate a markdown table from file information, sorted by line count (descending).
    
    Args:
        file_info: List of file information dictionaries
        
    Returns:
        str: Formatted markdown table
    """
    if not file_info:
        return "*No files found matching the criteria.*"
    
    # Sort by line count (descending) then by filename (ascending)
    sorted_info = sorted(
        file_info,
        key=lambda x: (-x['lines'], x['path'].lower())
    )
        
    table = ["| File | Extension | Lines | Size (KB) |", "|------|-----------|-------|-----------|"]
    for info in sorted_info:
        # Format numbers with commas for readability
        table.append(f"| `{info['path']}` | {info['ext']} | {info['lines']:,} | {info['size_kb']:.1f} |")
    
    return '\n'.join(table)

def generate_file_table(files: List[Dict[str, Any]], show_rank: bool = False) -> str:
    """Generate a markdown table from file information.
    
    Args:
        files: List of file information dictionaries
        show_rank: Whether to show rank column
        
    Returns:
        str: Formatted markdown table
    """
    if not files:
        return "*No files found matching the criteria.*"
    
    headers = ["Rank", "File", "Lines", "Size (KB)"] if show_rank else ["File", "Lines", "Size (KB)"]
    separator = ["------"] * len(headers)
    
    table = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(separator) + "|"
    ]
    
    for i, info in enumerate(files, 1):
        row = []
        if show_rank:
            row.append(str(i))
        row.extend([
            f"`{info['path']}`",
            f"{info['lines']:,}",
            f"{info['size_kb']:.1f}"
        ])
        table.append(f"| {' | '.join(row)} |")
    
    return '\n'.join(table)

def generate_top_files_table(file_info: List[Dict[str, Any]], top_n: int = 10) -> str:
    """Generate a table of the largest files by line count.
    
    Args:
        file_info: List of file information dictionaries
        top_n: Number of top files to include
        
    Returns:
        str: Formatted markdown table
    """
    if not file_info:
        return "*No files found matching the criteria.*"
        
    # Filter out empty files and sort by line count (descending)
    non_empty_files = [f for f in file_info if f['lines'] > 0]
    if not non_empty_files:
        return "*No non-empty files found.*"
        
    sorted_files = sorted(non_empty_files, key=lambda x: x['lines'], reverse=True)[:top_n]
    return generate_file_table(sorted_files, show_rank=True)

def generate_bottom_files_table(file_info: List[Dict[str, Any]], bottom_n: int = 5) -> str:
    """Generate a table of the smallest files by line count.
    
    Args:
        file_info: List of file information dictionaries
        bottom_n: Number of bottom files to include
        
    Returns:
        str: Formatted markdown table
    """
    if not file_info:
        return "*No files found matching the criteria.*"
        
    # Filter out empty files and sort by line count (ascending)
    non_empty_files = [f for f in file_info if f['lines'] > 0]
    if not non_empty_files:
        return "*No non-empty files found.*"
        
    sorted_files = sorted(non_empty_files, key=lambda x: x['lines'])[:bottom_n]
    return generate_file_table(sorted_files, show_rank=True)

def generate_exclusions_list() -> str:
    """Generate a formatted list of excluded file types and directories."""
    lines = ["## Excluded File Types and Directories"]
    lines.append("")
    
    # Generate the list of excluded file extensions from the categorized dictionary
    for category, extensions in sorted(DEFAULT_SKIP_EXTENSIONS_BY_CATEGORY.items()):
        lines.append(f"### {category}")
        # Sort extensions for consistent ordering
        lines.append(", ".join(f"`{ext}`" for ext in sorted(extensions)))
        lines.append("")  # Add a blank line for spacing
    
    lines.append("### Excluded Directories")
    lines.append(", ".join(f"`{d}`" for d in sorted(DEFAULT_SKIP_DIRS)))
    lines.append(
        "\n*Note: The scan also excludes hidden files (names starting with a `.period` ), "
        "`__init__.py`, and `desktop.ini` files.*"
    )
    
    return "\n".join(lines)


def generate_report(start_path: str, file_info: List[Dict[str, Any]], top_n: int) -> str:
    """Generates the full markdown report string."""
    report_parts = [
        "# Line Count Report",
        f"*Generated at: `{start_path}`*",
        "",
        "## File Statistics",
        f"- **Total files analyzed:** {len(file_info):,}",
        f"- **Total lines of code:** {sum(f['lines'] for f in file_info):,}",
        "",
        "## Largest Files",
        f"*Top {top_n} files by line count*",
        "",
        generate_top_files_table(file_info, top_n),
        "",
        "---",
        "",
        "## Smallest Files",
        "*Top 5 smallest non-empty files*",
        "",
        generate_bottom_files_table(file_info, 5),
        "",
        "---",
        "",
        "## Complete File List",
        "*Sorted by line count (descending), then by filename*",
        "",
        generate_markdown_table(file_info),
        "",
        "---",
        "",
        generate_exclusions_list()
    ]
    return "\n".join(report_parts)

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate a line count report for a codebase.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'path', 
        nargs='?', 
        default=os.getcwd(),
        help='Path to analyze (default: current directory).'
    )
    parser.add_argument(
        '-o', '--output',
        default='LINE_COUNT.md',
        help='Output file name (default: LINE_COUNT.md).'
    )
    parser.add_argument(
        '-n', '--top-n',
        type=int,
        default=10,
        help='Number of top files to show in the summary table (default: 10).'
    )
    return parser.parse_args()


def main() -> None:
    """Main function to generate the line count report."""
    args = parse_arguments()
    
    # Normalize the path to be absolute
    start_path = os.path.abspath(args.path)
    
    if not os.path.isdir(start_path):
        print(f"Error: '{start_path}' is not a valid directory.")
        return
    
    print(f"Analyzing files in: {start_path}...")
    file_info = get_file_info(start_path)
    
    if not file_info:
        print("No files found matching the criteria. Report not generated.")
        return
    
    # Generate the report content
    report_content = generate_report(start_path, file_info, args.top_n)
    
    # Write the report to the specified output file
    output_path = os.path.abspath(args.output)
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"Report generated successfully: {output_path}")
    except IOError as e:
        print(f"Error writing to {output_path}: {e}")


if __name__ == "__main__":
    main()
