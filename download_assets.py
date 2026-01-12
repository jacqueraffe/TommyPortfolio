import os
import re
import glob
import urllib.request
import urllib.parse
import hashlib
import ssl

# Ignore SSL errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

ASSETS_IMG_DIR = 'assets/images'
ASSETS_FILE_DIR = 'assets/files'

# Ensure directories exist
os.makedirs(ASSETS_IMG_DIR, exist_ok=True)
os.makedirs(ASSETS_FILE_DIR, exist_ok=True)

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def download_file(url, directory):
    try:
        if url.startswith('//'):
            url = 'https:' + url
        
        # Clean URL query params for hash but keep for request?
        # Squarespace URLs often have format=1500w. We want that.
        
        # Unique filename using hash
        url_hash = hashlib.md5(url.encode()).hexdigest()
        
        # Extract extension or guess it
        path = urllib.parse.urlparse(url).path
        ext = os.path.splitext(path)[1]
        if not ext or len(ext) > 5:
            ext = '.jpg' # Fallback
            
        filename = f"{url_hash}{ext}"
        filepath = os.path.join(directory, filename)
        
        if not os.path.exists(filepath):
            print(f"Downloading {url} to {filepath}...")
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
                with open(filepath, 'wb') as f:
                    f.write(response.read())
        
        return filename
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return None

def process_html_file(filepath):
    print(f"Processing {filepath}...")
    with open(filepath, 'r') as f:
        content = f.read()

    # Regex for <img> tags
    # Capture the whole tag to modify attributes
    img_regex = re.compile(r'<img[^>]+>', re.IGNORECASE | re.DOTALL)
    
    def replace_img(match):
        tag = match.group(0)
        
        # Extract data-src or src
        # We want the highest res, usually data-src has valid URL without query sometimes?
        # Squarespace data-src often lacks protocol/domain if relative? No, usually absolute.
        
        # Find data-src
        data_src_m = re.search(r'data-src=["\']([^"\']+)["\']', tag)
        src_m = re.search(r'src=["\']([^"\']+)["\']', tag)
        
        url = None
        if data_src_m:
            url = data_src_m.group(1)
        elif src_m:
            url = src_m.group(1)
            
        if url and ('squarespace' in url or url.startswith('http') or url.startswith('//')):
            # Refine check: we only want to download remote assets
            if 'squarespace' in url:
                # Append format=2500w if not present to get high res?
                # Actually, best to use the URL properly.
                # If content-type is image...
                pass
            
            filename = download_file(url, ASSETS_IMG_DIR)
            if filename:
                if '/' in filepath:
                    rel_path = f"../{ASSETS_IMG_DIR}/{filename}"
                else:
                    rel_path = f"{ASSETS_IMG_DIR}/{filename}"
                
                # Reconstruct tag
                # Simply replace src and remove other Squarespace junk
                new_tag = tag
                
                # Replace src value
                if 'src=' in new_tag:
                    new_tag = re.sub(r'src=["\'][^"\']+["\']', f'src="{rel_path}"', new_tag)
                else:
                    # Add src if missing (was lazy loaded)
                     new_tag = new_tag.replace('<img', f'<img src="{rel_path}"')

                # Remove data-src, srcset, data-image, data-load
                new_tag = re.sub(r'data-src=["\'][^"\']+["\']', '', new_tag)
                new_tag = re.sub(r'srcset=["\'][^"\']+["\']', '', new_tag)
                new_tag = re.sub(r'data-image=["\'][^"\']+["\']', '', new_tag)
                new_tag = re.sub(r'data-image-dimensions=["\'][^"\']+["\']', '', new_tag)
                new_tag = re.sub(r'data-load=["\'][^"\']+["\']', '', new_tag)

                return new_tag
        
        return tag

    content = img_regex.sub(replace_img, content)

    # Regex for <a> links to files
    a_regex = re.compile(r'<a[^>]+>', re.IGNORECASE | re.DOTALL)
    
    def replace_a(match):
        tag = match.group(0)
        href_m = re.search(r'href=["\']([^"\']+)["\']', tag)
        
        if href_m:
            url = href_m.group(1)
            if url.startswith('/s/'):
                full_url = f"https://www.thlarsen.com{url}"
                filename = download_file(full_url, ASSETS_FILE_DIR)
                if filename:
                    if '/' in filepath:
                        rel_path = f"../{ASSETS_FILE_DIR}/{filename}"
                    else:
                        rel_path = f"{ASSETS_FILE_DIR}/{filename}"
                    
                    new_tag = re.sub(r'href=["\'][^"\']+["\']', f'href="{rel_path}"', tag)
                    return new_tag
        return tag

    content = a_regex.sub(replace_a, content)
    
    with open(filepath, 'w') as f:
        f.write(content)

files = ['index.html', 'portfolio.html', 'resume.html'] + glob.glob('portfolio/*.html')
print(f"Found {len(files)} files: {files}")
for f in files:
    if os.path.exists(f):
        process_html_file(f)
