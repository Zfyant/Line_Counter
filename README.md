# 📏 Python Line Counter

**Ever wondered just how massive your codebase really is?** This sleek & super quick python script gives you the line count of all text files in a few helpful table-sets within a Markdown document wherever it is ran.

## ✨ What It Does

🔍 **Recursively Scans** your entire project's directory
📊 **Counts** & reports simply the line-count of relevant project files
🎯 **Ignores** the junk (images, docs, cache files, you name it)
📋 **Generates** a gorgeous Markdown report with all the juicy details

Perfect for developers who want to understand their project's scope, managers tracking code complexity, or anyone who loves data about their data.

**IDE AI** Gets bogged down in bigger files, keep track of which ones are getting too big on the fly.

###  To Do: 
- Webpage view & history
- Mermaid charts in the MD document


## 🚀 Quick Start

```bash
# Analyze current directory
python line_counter.py

# Analyze any project
python line_counter.py /path/to/your/awesome-project

# Custom report name + show top 20 files
python line_counter.py ~/my-project -o ProjectStats.md -n 20
```

**That's it!** Your `LINE_COUNT.md` report will be ready in seconds.

## 🎁 What You Get

Your report includes:

- **📈 Project Overview** - Total files and lines at a glance
- **🏆 Hall of Fame** - Your biggest files (configurable top N)
- **🐭 Tiny Files** - The smallest non-empty files  
- **📋 Complete Inventory** - Every file, sorted by size
- **🚫 Exclusions List** - What got filtered out and why

## ⚙️ Smart Defaults

Automatically skips the stuff you don't care about by default:

**🗂️ Directories:** `.git`, `node_modules`, `venv`, `__pycache__`, logs, backups  
**📁 Files:** Images, docs, databases, archives, binaries, cache files

## 🛠️ All the Options

| Option | What It Does | Default |
|--------|-------------|---------|
| `PATH` | Directory to analyze | Current directory |
| `-o, --output` | Report filename | `LINE_COUNT.md` |
| `-n, --top-n` | # of top files to show | `10` |
| `-h, --help` | Show all options | - |

## 🎨 Make It Yours

Want to tweak what gets excluded? Just edit these at the top of `line_counter.py`:

- `DEFAULT_SKIP_DIRS` - Directories to ignore
- `DEFAULT_SKIP_EXTENSIONS_BY_CATEGORY` - File types to skip (nicely organized by category)

## 🔧 Requirements

- Python 3.x (that's it!)

## 📝 License

MIT License - Use it, love it, share it! 

---

*Ready to discover what your codebase is really made of? Give it a spin!* 🎯