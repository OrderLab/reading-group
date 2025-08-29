#!/usr/bin/env python3

import json
import os
import re
from pathlib import Path

def load_template(template_name):
    """Load a template file"""
    with open(f'templates/{template_name}', 'r') as f:
        return f.read()

def load_semesters():
    """Load semester configuration"""
    with open('config/semesters.json', 'r') as f:
        return json.load(f)

def generate_semester_links(semesters, current_semester=None):
    """Generate semester navigation links"""
    links = []
    for semester in semesters:
        if current_semester and semester['id'] == current_semester:
            links.append(f'  <li class="current-semester"><a href="https://orderlab.io/reading-group/{semester["id"]}">{semester["name"]}</a></li>')
        else:
            links.append(f'  <li><a href="https://orderlab.io/reading-group/{semester["id"]}">{semester["name"]}</a></li>')
    return '\n'.join(links)

def extract_schedule_from_existing(html_file):
    """Extract schedule table rows from existing HTML file"""
    if not os.path.exists(html_file):
        return ""
    
    with open(html_file, 'r') as f:
        content = f.read()
    
    # Find schedule table content between <tr> tags (excluding header)
    pattern = r'<tr class="info">.*?</tr>\s*(.*?)</table>'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def extract_config_from_existing(html_file, semester_id):
    """Extract configuration from existing HTML file"""
    if not os.path.exists(html_file):
        return get_default_config(semester_id)
    
    with open(html_file, 'r') as f:
        content = f.read()
    
    config = {}
    
    # Extract title from <title> tag
    title_match = re.search(r'<title>(.*?)</title>', content)
    config['title'] = title_match.group(1) if title_match else semester_id.title()
    
    # Extract description from meta tag
    desc_match = re.search(r'<meta name="description" content="(.*?)"', content)
    config['description'] = desc_match.group(1) if desc_match else f'OrderLab Reading Group, {semester_id}'
    
    # Extract main title from h1
    main_title_match = re.search(r'<h1>(.*?)</h1>', content)
    config['main_title'] = main_title_match.group(1) if main_title_match else 'OrderLab Reading Group'
    
    # Extract semester from h2
    semester_match = re.search(r'<h2 class="semester">(.*?)</h2>', content)
    config['semester'] = semester_match.group(1) if semester_match else semester_id.title()
    
    # Extract time/location from h3
    time_match = re.search(r'<h3>(.*?)</h3>', content)
    config['time_location'] = time_match.group(1) if time_match else 'TBD'
    
    # Extract coordinator from h4
    coord_match = re.search(r'<h4>(.*?)</h4>', content)
    config['coordinator'] = coord_match.group(1) if coord_match else 'Coordinator: TBD'
    
    # Extract mailing list from description section
    mail_match = re.search(r'<a href="mailto:([^"]+)"[^>]*>([^<]+)</a>,?\s*which will also be used', content)
    if mail_match:
        config['mailing_list'] = mail_match.group(1)
    else:
        # Fallback - look for any mailing list mention
        mail_fallback = re.search(r'<a href="mailto:([^"]+)"', content)
        config['mailing_list'] = mail_fallback.group(1) if mail_fallback else 'orderlab-talk@umich.edu'
    
    # Extract signup email
    signup_match = re.search(r'please email <a href="mailto:([^"]+)"', content)
    config['signup_email'] = signup_match.group(1) if signup_match else 'ryanph@umich.edu'
    
    # Determine format type based on content
    if '601.817' in config['main_title'] or 'Selected Topics in Systems Research' in config['main_title']:
        config['format_type'] = 'jhu'
    else:
        config['format_type'] = 'orderlab'
    
    return config

def get_default_config(semester_id):
    """Get default configuration for a semester"""
    return {
        'title': semester_id.title(),
        'main_title': 'OrderLab Reading Group',
        'description': f'OrderLab Reading Group, {semester_id}',
        'semester': semester_id.title(),
        'time_location': 'TBD',
        'coordinator': 'Coordinator: TBD',
        'mailing_list': 'orderlab-talk@umich.edu',
        'signup_email': 'ryanph@umich.edu',
        'format_type': 'orderlab'
    }

def get_description_template(format_type):
    """Get the appropriate description template based on format type"""
    if format_type == 'jhu':
        return """    <div class="col-9">
      <h1>Description</h1>
      <p>601.817 is a weekly seminar organized by the <a href="https://orderlab.io/">OrderLab</a>.
        It covers latest advances in the research of computer systems including operating systems, 
        distributed system, mobile and cloud computing. Students will read and discuss recent papers 
        in top systems conferences such as OSDI, SOSP, NSDI, EuroSys, MobiSys, ASPLOS and FAST.
      </p>
      <p>Each week, one student will present the paper and lead the discussion for the week. Other students
        <b>MUST</b> read the paper to be presented <b class="text-danger">before</b> the seminar. Do not come to the seminar to
        read the paper. This seminar is supposed to generate in-depth discussions. It is impossible to do so 
        without reading the paper first. During the reading group discussion, there might be some questions 
        that were left unanswered and required further investigation. In that case, the discussion lead 
        should start a email thread to <a href="mailto:{{MAILING_LIST}}">{{MAILING_LIST}}</a> 
        afterwards to follow up. 
      </p>
      <p>The focus topics covered in the papers vary semester to semester. Example topics include 
        fault-tolerance, reliability, verification, energy efficiency, and virtualization. The presenter 
        decides which paper to present. In general, select
        the papers that are relevant to your research project first (i.e., depth-first). If you are not sure, 
        it is a good idea to check with me first before preparing the presentation. Also, try to avoid picking papers
        that have already been picked in the past (the past schedules are linked on the leftside menu).
      </p>
      <p>The presentation announcements are sent via the mailing list <a href="mailto:{{MAILING_LIST}}">{{MAILING_LIST}}</a>.
        Students who registered for the course please email me to sign up for the mailing list.
      </p>

      <h1>Schedule</h1>
      <table class="table-bordered schedule">
        <tr class="info">
          <th class="date">Date</th>
          <th class="presenter">Presenter</th>
          <th class="title">Title</th>
          <th class="conference">Conference</th>
          <th class="material">Material</th>
        </tr>
{{SCHEDULE_ROWS}}
      </table>
    </div>
    <div class="col-2">
    </div>  
  </div>
</body>
</html>"""
    else:  # orderlab format
        return """    <div class="col-9">
      <h1>Description</h1>
      <p>The reading group organized by the <a href="https://orderlab.io/">OrderLab</a>
        covers latest advances in the research of computer systems. Students will
        read and discuss recent papers in top systems conferences such as OSDI, SOSP,
        NSDI, EuroSys, and ASPLOS.
      </p>
      <p>Each week, one student will present the paper and lead the discussion. Other students
        should read the paper to be presented <b class="text-danger">before</b> the seminar.
        This seminar is supposed to generate in-depth discussions. It is impossible to do so
        without reading the paper first.
      </p>
      <p>The focus topics covered in the papers vary semester to semester. Example topics include
        fault-tolerance, reliability, verification, energy efficiency, and
        virtualization. The presenter decides which paper to present. In general,
        select the papers that are relevant to your research project first (i.e.,
        depth-first). If you are not sure, check with me first
        before preparing the presentation. Also, try to avoid picking papers that
        have already been picked in the past (the past schedules are linked on the
        left-side menu).
      </p>
      <p>
        If you are set to present, please first sign up
        <a href="https://docs.google.com/spreadsheets/d/1IsobQdv8d5yy9ZR2SNJn3dMg3lM5XpaPV46Q-roQkEQ/edit?usp=sharing">here</a>
        at least two weeks in advance. Then, around one week before the meeting, you should send another
        reminder to the group via our reading group mailing list <a href="mailto:orderlab-talk@umich.edu">orderlab-talk@umich.edu</a>, 
        which will also be used to generate follow-up discussions of the presented paper. 
        Students who wish to sign up for the mailing list should email <a href="mailto:ryanph@umich.edu">ryanph@umich.edu</a>.
        If you would like to invite an external presenter, you should first contact Ryan
        and the coordinator, then sign up on the spreadsheet and send the reminder email
        as if you are presenting.
      </p>

      <h1>Schedule</h1>
      <table class="table-bordered schedule">
        <tr class="info">
          <th class="date">Date</th>
          <th class="presenter">Presenter</th>
          <th class="title">Title</th>
          <th class="conference">Conference</th>
          <th class="material">Material</th>
        </tr>
{{SCHEDULE_ROWS}}
      </table>
    </div>
    <div class="col-2">
    </div>  
  </div>
</body>
</html>"""

def generate_html(semester_id):
    """Generate HTML file for a semester"""
    semesters = load_semesters()
    
    # Extract config from existing file
    existing_file = f'{semester_id}/index.html'
    config = extract_config_from_existing(existing_file, semester_id)
    
    # Load templates
    head = load_template('head.html')
    header = load_template('header.html')
    sidebar = load_template('sidebar.html')
    
    # Generate semester links
    semester_links = generate_semester_links(semesters, semester_id)
    
    # Extract existing schedule
    schedule_rows = extract_schedule_from_existing(existing_file)
    
    # Get appropriate description template
    description = get_description_template(config['format_type'])
    
    # Replace placeholders in head
    html = head.replace('{{DESCRIPTION}}', config['description'])
    html = html.replace('{{TITLE}}', config['title'])
    
    # Add header
    html += '\n\n' + header.replace('{{MAIN_TITLE}}', config['main_title'])
    html = html.replace('{{SEMESTER}}', config['semester'])
    html = html.replace('{{TIME_LOCATION}}', config['time_location'])
    html = html.replace('{{COORDINATOR}}', config['coordinator'])
    
    # Add sidebar
    html += '\n' + sidebar.replace('{{SEMESTER_LINKS}}', semester_links)
    
    # Add description with appropriate template  
    html += '\n' + description.replace('{{MAILING_LIST}}', config['mailing_list'])
    html = html.replace('{{SIGNUP_EMAIL}}', config['signup_email'])
    html = html.replace('{{SCHEDULE_ROWS}}', schedule_rows)
    
    return html

def main():
    """Main function"""
    semesters = load_semesters()
    
    print("Generating HTML files from templates...")
    
    for semester in semesters:
        semester_id = semester['id']
        
        # Create directory if it doesn't exist
        os.makedirs(semester_id, exist_ok=True)
        
        # Generate HTML
        html = generate_html(semester_id)
        
        # Write to file
        output_file = f'{semester_id}/index.html'
        with open(output_file, 'w') as f:
            f.write(html)
        
        print(f"✓ Generated {output_file}")
    
    print(f"\nSuccessfully generated {len(semesters)} HTML files!")

if __name__ == '__main__':
    main()