# Quick Start Guide - Multi-Language Documentation

## 🚀 Quick Commands

### First Time Setup
```bash
# 1. Fork this repo on GitHub, then clone your fork
git clone https://github.com/<your-username>/ou-documentation.git
cd ou-documentation

# (optional) track the upstream repo to pull in updates later
git remote add upstream https://github.com/omegaup/documentation.git

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate it
source .venv/bin/activate  # macOS/Linux

# 4. Install dependencies
pip install zensical
```

### Daily Development Workflow

```bash
# 1. Activate virtual environment (if not already active)
source .venv/bin/activate

# 2. Build all languages
python3 build_all.py

# 3. Start the development server
python3 serve_multilang.py

# 4. Open browser to http://localhost:8000/
```

### Making Content Changes

```bash
# 1. Edit files in docs/en/
vim docs/en/getting-started/index.md

# 2. Rebuild (will rebuild all languages)
python3 build_all.py

# 3. Refresh browser - changes will appear immediately
```

### Updating Translations

```bash
# After updating English content, re-translate
python3 scripts/translate_docs.py

# Then rebuild
python3 build_all.py
```

## 🌍 Available URLs

When running `python3 serve_multilang.py`:

- **Root (auto-redirects):** http://localhost:8000/
- **English:** http://localhost:8000/en/
- **Spanish:** http://localhost:8000/es/  
- **Portuguese:** http://localhost:8000/pt/
- **Brazilian Portuguese:** http://localhost:8000/pt-BR/

## 🔧 Troubleshooting

### Problem: 404 when switching languages

**DON'T USE:**
```bash
zensical serve  # ❌ Only serves one language
```

**USE INSTEAD:**
```bash
python3 serve_multilang.py  # ✅ Serves all languages
```

### Problem: Virtual environment not found

```bash
# Create it first
python3 -m venv .venv
source .venv/bin/activate
pip install zensical
```

### Problem: Command not found: zensical

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Verify zensical is installed
which zensical
# Should output: .venv/bin/zensical
```

### Problem: Port 8000 already in use

The server auto-falls back to the next free port (8001, 8002, …) and prints the
URL it landed on. To pick a port yourself:

```bash
python3 serve_multilang.py 8080
```

### Problem: Changes not showing

```bash
# Hard rebuild
rm -rf .cache site
python3 build_all.py
# Then refresh browser with Cmd+Shift+R (hard refresh)
```

## 📝 File Structure at a Glance

```
docs/
├── docs/
│   ├── en/          ← Edit English content here
│   ├── es/          ← Spanish (auto-translated)
│   ├── pt/          ← Portuguese (auto-translated)
│   └── pt-BR/       ← Brazilian Portuguese (auto-translated)
│
├── site/            ← Built output (don't edit)
│   ├── en/
│   ├── es/
│   ├── pt/
│   └── pt-BR/
│
├── build_all.py         ← Build all languages
└── serve_multilang.py   ← Development server
```

## 💡 Pro Tips

1. **Always use the multi-language server** for development:
   ```bash
   python3 serve_multilang.py
   ```

2. **Only edit `docs/en/`** - other languages are auto-translated:
   ```bash
   # Edit English content
   vim docs/en/some-file.md
   
   # Re-translate
   python3 scripts/translate_docs.py
   
   # Rebuild
   python3 build_all.py
   ```

3. **Keep virtual environment active** during development to avoid path issues

4. **Use hard refresh** (Cmd+Shift+R on Mac, Ctrl+Shift+R on Windows/Linux) to see changes

## 🎯 Common Tasks

### Add a new page (English):
```bash
# 1. Create the file
vim docs/en/new-section/new-page.md

# 2. Translate to other languages
python3 scripts/translate_docs.py --only "new-section"

# 3. Rebuild
python3 build_all.py
```

### Update existing content:
```bash
# 1. Edit English version
vim docs/en/getting-started/index.md

# 2. Re-translate that section
python3 scripts/translate_docs.py --only "getting-started"

# 3. Rebuild
python3 build_all.py
```

### Build only one language (faster for testing):
```bash
# Build only Portuguese
.venv/bin/zensical build --clean --config-file zensical.pt.toml

# Note: Language switching won't work without all languages built
```
