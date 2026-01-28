# OrderLab Reading Group Website

[https://orderlab.io/reading-groups](https://orderlab.io/reading-groups)


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

Edit the current semester file in `semesters/` (e.g., `semesters/fall25.md`) and
add a new entry to the `sessions` list:

For a paper presentation:
```yaml
  - date: "11/20/2025"
    presenter: "Your Name"
    title: "Paper Title"
    authors: "Author1, Author2, Author3"
    venue: "OSDI '25"
    link: "https://example.com/paper.pdf"
```

For a project presentation or knowledge sharing:
```yaml
  - date: "11/20/2025"
    presenter: "Your Name"
    title: "Project Progress Sharing"
```


## Adding a New Semester

1. Create a new semester file by copying the previous one:
```bash
cp semesters/fall25.md semesters/spring26.md
```

2. Edit `semesters/spring26.md` and update the front matter and description:
```yaml
---
layout: semester
semester_id: spring26
semester: "Spring 2026"
time: "Your meeting time and location"
coordinator: "Coordinator Name"
permalink: /spring26/

sessions:
  - date: "01/15/2026"
    presenter: "Someone"
    title: "Semester Kickoff"
---

# Description
(The description text will be copied from the previous semester - edit as needed)
```

3. Update `_config.yml` to add the new semester and mark it as current:
```yaml
current_semester: spring26

semesters:
  - id: spring26
    name: "Spring 2026"
    active: true
  - id: fall25
    name: "Fall 2025"
    active: false
  # ... rest of the list
```

The new semester will automatically appear in the navigation of all pages.


## Deployment

Commite and push all your changes to the main branch on GitHub.