# Reading Group Website

This repository contains the HTML files for the OrderLab reading group website, with a consolidated template system to reduce duplication.

## Structure

- **Individual semester folders** (`fall24/`, `spring22/`, etc.) - Contains `index.html` for each semester
- **`templates/`** - Shared HTML template components
- **`config/`** - Configuration files
- **`generate.py`** - Script to generate all HTML files from templates

## Template System

The consolidation system extracts shared content into reusable templates:

### Templates (`templates/`)

- `head.html` - HTML head section with meta tags, CSS links, favicon
- `header.html` - Page header with title, semester, time/location, coordinator
- `sidebar.html` - Semester navigation sidebar
- `description.html` - Main content section (supports both OrderLab and JHU formats)

### Configuration (`config/`)

- `semesters.json` - List of all semesters for navigation

## Usage

### Generating HTML Files

Run the generation script to create all semester HTML files:

```bash
python generate.py
```

This will:
1. Read existing HTML files to extract semester-specific configurations
2. Generate standardized HTML using the template system
3. Preserve all existing schedule content
4. Update semester navigation across all files

### Adding a New Semester

1. Add the semester to `config/semesters.json`:
```json
{"id": "spring26", "name": "Spring 2026"}
```

2. Create the semester directory:
```bash
mkdir spring26
```

3. Run the generator to create the initial HTML file:
```bash
python3 generate.py
```

4. Edit the generated `spring26/index.html` to add schedule content

### Updating Shared Content

To update content that appears on all pages:

1. Edit the appropriate template in `templates/`
2. Run `python3 generate.py` to update all HTML files
