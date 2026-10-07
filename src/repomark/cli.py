"""
repomark: A lightweight zero-dependency repository context packer for LLMs.
"""

import os
import sys
import argparse
from pathlib import Path

# 預設過濾的常見開發目錄與編譯快取
DEFAULT_IGNORE_DIRS = {
    ".git", ".github", "__pycache__", "node_modules", "dist", "build",
    ".vscode", ".idea", "venv", ".venv", "env"
}

# 二進位檔案擴展名過濾表
BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf", ".zip",
    ".tar", ".gz", ".7z", ".exe", ".bin", ".pyc", ".pyd", ".so", ".dylib"
}

def is_text_file(path: Path) -> bool:
    """判斷檔案是否為純文字檔案（副檔名檢查與前 1024 位元組檢查）"""
    if path.suffix.lower() in BINARY_EXTENSIONS:
        return False
    try:
        with open(path, "rb") as f:
            chunk = f.read(1024)
            if b"\x00" in chunk:
                return False
        return True
    except (OSError, IOError):
        return False

def generate_tree(dir_path: Path, prefix: str = "", ignore_dirs: set = None) -> list[str]:
    """遞迴生成 ASCII 目錄樹狀圖"""
    if ignore_dirs is None:
        ignore_dirs = DEFAULT_IGNORE_DIRS

    lines = []
    entries = sorted([
        e for e in dir_path.iterdir()
        if not (e.name.startswith(".") and e.name not in {".gitignore"}) and e.name not in ignore_dirs
    ], key=lambda x: (not x.is_dir(), x.name.lower()))

    total = len(entries)
    for idx, entry in enumerate(entries):
        connector = "└── " if idx == total - 1 else "├── "
        lines.append(f"{prefix}{connector}{entry.name}")
        if entry.is_dir():
            extension = "    " if idx == total - 1 else "│   "
            lines.extend(generate_tree(entry, prefix + extension, ignore_dirs))
    return lines

def estimate_tokens(text: str) -> int:
    """以字元比例粗估 Token 數量（約 4 個英文字元 / 1 Token）"""
    return max(1, len(text) // 4)

def pack_repository(target_dir: Path, output_file: Path | None = None) -> str:
    """將專案結構與所有程式碼合併為標準 Markdown 格式"""
    target_dir = target_dir.resolve()
    if not target_dir.is_dir():
        raise ValueError(f"Target path '{target_dir}' is not a directory.")

    output_lines = []
    output_lines.append(f"# Repository Context: `{target_dir.name}`\n")
    output_lines.append("## Directory Tree\n```text")
    output_lines.append(target_dir.name)
    output_lines.extend(generate_tree(target_dir))
    output_lines.append("```\n")

    output_lines.append("## File Contents\n")

    scanned_files = []
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in DEFAULT_IGNORE_DIRS and not d.startswith(".")]
        for file in files:
            file_path = Path(root) / file
            if file.startswith(".") and file != ".gitignore":
                continue
            if is_text_file(file_path):
                scanned_files.append(file_path)

    for file_path in sorted(scanned_files):
        rel_path = file_path.relative_to(target_dir)
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
            lang = file_path.suffix.lstrip(".") or "text"
            output_lines.append(f"### File: `{rel_path}`\n")
            output_lines.append(f"```{lang}\n{content}\n```\n")
        except Exception as e:
            output_lines.append(f"> Warning: Failed to read `{rel_path}`: {e}\n")

    full_output = "\n".join(output_lines)
    approx_tokens = estimate_tokens(full_output)
    final_result = f"> Estimated context tokens: ~{approx_tokens:,} tokens\n\n" + full_output

    if output_file:
        output_file.write_text(final_result, encoding="utf-8")

    return final_result

def main():
    parser = argparse.ArgumentParser(
        description="repomark: Pack code repository files into LLM-ready context."
    )
    parser.add_argument("path", nargs="?", default=".", help="Target directory (default: .)")
    parser.add_argument("-o", "--output", help="Output Markdown file path")

    args = parser.parse_args()
    target_path = Path(args.path)
    out_path = Path(args.output) if args.output else None

    try:
        result = pack_repository(target_path, out_path)
        if out_path:
            print(f"[✓] Bundled `{target_path.name}` into `{out_path}`.")
            print(f"[i] Estimated size: ~{estimate_tokens(result):,} tokens")
        else:
            print(result)
    except Exception as e:
        print(f"[✗] Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
