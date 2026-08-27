# OrderLab Reading Group Website

[https://orderlab.io/reading-group](https://orderlab.io/reading-group)


## Local Development Environment
This website is built with [Jekyll](https://jekyllrb.com/). Install Jekyll on
your local machine:
```bash
gem install bundler jekyll
bundle install
```

You can serve the website locally through:
```bash
git clone https://github.com/OrderLab/reading-group.git
cd reading-group
bundle exec jekyll serve --livereload
```

The above will show a server accessible by a localhost address.


## Adding New Group Meetings

The current semester schedule is pulled live from a Google Sheet. Edit the
sheet; visitors see the update on the next page load. You do not need to commit
or redeploy for schedule changes.

1. Create a Google Sheet (or add a tab) with this header row:

   `date, presenter, title, authors, venue, link, publish`

2. Share the sheet as **Anyone with the link → Viewer**.

3. The live spreadsheet is:

   https://docs.google.com/spreadsheets/d/1BmhrnXLpXjCNOm4JTYM0elFYfnZs6FNbM3LZYieGm6w/edit

   Its ID is already set in `_config.yml`:

   ```yaml
   google_sheet_id: "1BmhrnXLpXjCNOm4JTYM0elFYfnZs6FNbM3LZYieGm6w"
   ```

4. In the current semester file, set the tab name:

   ```yaml
   sheet_tab: "Summer 2026"
   ```

Example rows:

| date | presenter | title | authors | venue | link | publish |
| --- | --- | --- | --- | --- | --- | --- |
| 05/12/2026 | Yuxuan Jiang | AgentSpec: ... | Haoyu Wang, ... | ICSE '26 | https://arxiv.org/abs/2503.18666 | TRUE |
| 06/17/2026 | Ziming Zhou | OpGuard Practice Talk | | | | |

Put a checkbox in `publish`. Only checked rows appear on the website.
Leave it unchecked while a talk is still a draft.

`authors`, `venue`, and `link` can be left blank for project talks or
knowledge-sharing sessions.

Past semesters stay in `_semesters/*.md` as a static archive. If the sheet is
unreachable, the site falls back to the `sessions` list in that markdown file.


## Adding a New Semester

1. Create a new semester file by copying the previous one:
```bash
cp _semesters/fall25.md _semesters/spring26.md
```

2. Edit `_semesters/spring26.md` and update the front matter and description:
Note that all fields are necessary. The `first_date` field allows sorting of the
navigation bar such that the latest semester will appear first.
```yaml
---
layout: semester
semester_id: spring26
semester: "Spring 2026"
first_date: "01/15/2026"
time: "Your meeting time and location"
coordinator: "Coordinator Name"
permalink: /spring26/
sheet_tab: "Spring 2026"

sessions:
  - date: "01/15/2026"
    presenter: "Someone"
    title: "Semester Kickoff"
---

# Description
(The description text will be copied from the previous semester - edit as needed)
```

Create a matching tab in the Google Sheet. After that, add meetings in the
sheet instead of this markdown file. Keep a `sessions` fallback if you want the
page to still render when the sheet cannot be loaded.

The new semester will automatically appear in the navigation of all pages.


## Deployment

Commit and push structural changes (new semester page, description, time,
coordinator) to the main branch on GitHub. Schedule rows themselves do not
need a deploy once the Google Sheet is connected.
