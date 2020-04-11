import argparse
import json
import os.path
import re

from retry import retry
from pyinstapaper.instapaper import Instapaper

INDEX_FILE = '.index'

def slugify(value):
    return re.sub(r'[^\w\- ]', '', value)

@retry(delay=1, backoff=2, tries=3)
def get_text(bookmark):
    return bookmark.get_text()['data']

parser = argparse.ArgumentParser(description = 'Backup Instapaper')
parser.add_argument('--username', type=str, help='Instapaper username')
parser.add_argument('--password', type=str, help='Instapaper password')
parser.add_argument('--backup', type=str, help='Backup directory')
parser.add_argument('--client_id', type=str, help='Instapaper OAuth client ID')
parser.add_argument('--client_secret', type=str, help='Instapaper OAuth client secret')
args = parser.parse_args()

instapaper = Instapaper(args.client_id, args.client_secret)
instapaper.login(args.username, args.password)

# Load the backup index.
INDEX_FILE = os.path.join(args.backup, INDEX_FILE)
index = {}
if os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, 'r') as index_file:
        index = json.load(index_file)

folders = instapaper.get_folders()
seen = []  # Use to skip bookmarks that were in a folder and unread/archived.

folders = [(folder.folder_id, folder.title) for folder in folders] + [
           ('unread', 'unread'), ('archive', 'archive')]
for (fid, ftitle) in folders:
    print(f'Syncing "{ftitle}"')
    out = os.path.join(args.backup, ftitle)
    if not os.path.exists(out):
        os.makedirs(out)
    bs = instapaper.get_bookmarks(fid, limit=500, have=index.get(fid, []))
    for b in bs:
        if b.bookmark_id not in seen:
            print(f'\tDownloading "{b.title}"')
            text = None
            try:
              text = get_text(b)
            except:
                print(f'Fatal error downloading "{b.title}"!')
                continue
            fname = os.path.join(out, slugify(b.title))
            if os.path.exists(fname + '.html'):
                fname  += b.hash
            fname += '.html'
            with open(os.path.join(out, fname), 'wb') as output:
                output.write(text)
            seen.append(b.bookmark_id)
        index[fid] = index.get(fid, []) + [str(b.bookmark_id) + ':' + b.hash] 

with open(INDEX_FILE, 'w') as index_file:
    json.dump(index, index_file)
