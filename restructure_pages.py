import os
import shutil
import re
import glob

# Configuration
PORTFOLIO_DIR = 'portfolio'
ASSETS_REL_PATH = '../../assets'
LOCAL_ROOT_REL_PATH = '../../'

def restructure_project(html_file):
    filename = os.path.basename(html_file)
    project_name = os.path.splitext(filename)[0]
    
    # Create directory if not exists
    project_dir = os.path.join(PORTFOLIO_DIR, project_name)
    os.makedirs(project_dir, exist_ok=True)
    
    # Target file
    target_file = os.path.join(project_dir, 'index.html')
    
    print(f"Moving content from {html_file} to {target_file}")
    
    with open(html_file, 'r') as f:
        content = f.read()
        
    # --- Update content for new depth (2 levels deep now) ---
    
    # Update CSS links
    # Was: href="../assets/css/styles.css"
    # Now: href="../../assets/css/styles.css"
    content = content.replace('href="../assets/', f'href="{ASSETS_REL_PATH}/')
    content = content.replace('href="assets/', f'href="{ASSETS_REL_PATH}/') # Just in case

    # Update JS links if any (though usually at bottom)
    content = content.replace('src="../assets/', f'src="{ASSETS_REL_PATH}/')
    
    # Update Image sources
    # Was: src="../assets/images/..."
    # Now: src="../../assets/images/..."
    content = content.replace('src="../assets/', f'src="{ASSETS_REL_PATH}/')
    content = content.replace('src="assets/', f'src="{ASSETS_REL_PATH}/')

    # Update Navigation Links
    # Was: href="../index.html" -> href="../../index.html"
    content = content.replace('href="../index.html"', f'href="{LOCAL_ROOT_REL_PATH}index.html"')
    content = content.replace('href="../portfolio.html"', f'href="{LOCAL_ROOT_REL_PATH}portfolio.html"')
    content = content.replace('href="../resume.html"', f'href="{LOCAL_ROOT_REL_PATH}resume.html"')
    
    # Update sibling project links? 
    # Current: href="actuator.html" (relative)
    # New needs to be: href="../actuator/" or just absolute from root if we could, but relative is safer for GH pages project site?
    # Relative from `portfolio/scorpion/index.html` to `portfolio/actuator/index.html`
    # is `../actuator/`
    
    # Find all project links. They were `href="project.html"`
    # We need to find them strictly.
    # List of known projects
    projects = ['scorpion', 'actuator', 'toylab', 'microcloud', 'cim', 'hot-plate-jig']
    for p in projects:
        # Regex to match href="p.html" or href="./p.html"
        # Be careful not to match partials if any
        pattern = f'href="{p}.html"'
        replacement = f'href="../{p}/"' # Directory style link
        content = content.replace(pattern, replacement)
        
        # Also catch any legacy absolute ones if they exist? No, we fixed those to relative earlier.
        
    # Fix pagination links often found at bottom
    # They look like: href="actuator.html"
    
    # Write to new location
    with open(target_file, 'w') as f:
        f.write(content)
        
    # Remove old file if it's not the target (it shouldn't be)
    if html_file != target_file:
        os.remove(html_file)

def update_root_pages():
    # Update index.html, portfolio.html, resume.html
    # to point to portfolio/project/ instead of portfolio/project.html or /portfolio/project
    
    root_files = ['index.html', 'portfolio.html', 'resume.html']
    projects = ['scorpion', 'actuator', 'toylab', 'microcloud', 'cim', 'hot-plate-jig']
    
    for filename in root_files:
        if not os.path.exists(filename):
            continue
            
        print(f"Updating links in {filename}")
        with open(filename, 'r') as f:
            content = f.read()
            
        for p in projects:
            # Replace /portfolio/p with portfolio/p/
            # Replace /portfolio/p.html with portfolio/p/
            # Replace portfolio/p.html with portfolio/p/
            
            # The current state of portfolio.html has `href="/portfolio/scorpion"`
            # We want `href="portfolio/scorpion/"` (relative directory) to be safe for GH pages subdir
            
            # Regex for absolute path
            content = re.sub(f'href="/portfolio/{p}"', f'href="portfolio/{p}/"', content)
            
            # Regex for relative html file
            content = content.replace(f'href="portfolio/{p}.html"', f'href="portfolio/{p}/"')
            
        # Also fix global nav
        # href="/portfolio" -> href="portfolio.html"
        content = content.replace('href="/portfolio"', 'href="portfolio.html"')
        content = content.replace('href="/resume"', 'href="resume.html"')
        content = content.replace('href="/"', 'href="index.html"')
        # Handle "Home" link which might be just / 
        
        # portfolio.html specific:
        # href="/portfolio/" -> href="portfolio.html" if it exists
        
        with open(filename, 'w') as f:
            f.write(content)

if __name__ == '__main__':
    # Find all HTML files in portfolio/
    # Exclude directories
    files = glob.glob(os.path.join(PORTFOLIO_DIR, '*.html'))
    print(f"Found {len(files)} project pages to restructure.")
    
    for f in files:
        restructure_project(f)
        
    update_root_pages()
    print("Restructuring complete.")
