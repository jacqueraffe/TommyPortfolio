
import urllib.request
import urllib.error
import sys

url = sys.argv[1]
output_file = sys.argv[2]

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        content = response.read()
        with open(output_file, 'wb') as f:
            f.write(content)
    print(f"Successfully fetched {url} to {output_file}")
except Exception as e:
    print(f"Failed to fetch {url}: {e}")
    sys.exit(1)
