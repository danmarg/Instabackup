import argparse
import json
import os.path
import re

from retry import retry
from pyinstapaper import instapaper
instapaper.REQUEST_DELAY_SECS = 0
from pyinstapaper.instapaper import Instapaper

def slugify(value):
    return re.sub(r'[^\w\- ]', '', value)

@retry(delay=1, backoff=2, tries=3)
def get_text(bookmark):
    return bookmark.get_text()['data']

def main():
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
    INDEX_FILE = os.path.join(args.backup, '.index')
    index = {}
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, 'r') as index_file:
            index = json.load(index_file)

    folders = instapaper.get_folders()

    folders = [(folder.folder_id, folder.title) for folder in folders] + [
               ('unread', 'unread'), ('archive', 'archive')]
    for (fid, ftitle) in folders:
        print(f'Syncing "{ftitle}"')
        out = os.path.join(args.backup, ftitle)
        if not os.path.exists(out):
            os.makedirs(out)
        bs, dels = instapaper.get_bookmarks_with_deleted(
                       fid, limit=500, have=index.get(str(fid), []))
        i = 0
        tot = len(bs)
        for b in bs:
            i += 1
            fname = os.path.join(out, slugify(b.title))
            if os.path.exists(fname + '.html'):
                fname += b.hash
            fname += '.html'
            key = str(b.bookmark_id)
            # If there was an older copy of this article somewhere else, just
            # move it.
            success = False
            if key in index:
                print(f'\t[{i} of {tot}] - Moving existing "{b.title}"')
                try:
                    os.rename(index[key], fname)
                    success = True
                except FileNotFoundError:
                    print('\t\tFile not found - trying to download instead')
                    index.pop(key)
            # Otherwise, download the full text.
            if not success:
                print(f'\t[{i} of {tot}] - Downloading "{b.title}"')
                text = None
                try:
                    text = get_text(b)
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(f'Fatal error downloading "{b.title}": {e}')
                    continue
                with open(fname, 'wb') as output:
                    output.write(text)
            # Save in the index the location of this item, and append this item
            # to the items we have for this folder.
            index[key] = fname
            index[str(fid)] = index.get(str(fid), []) + [
                    str(b.bookmark_id) + ':' + b.hash]
        # Remove deleted bookmarks.
        for key in dels:
            if key in index:
                print(f'\tRemoving {index[key]}')
                try:
                    os.remove(index[key])
                except Exception as e:
                    print(f'Error removing file: {e}')
                    continue

    # Save the backup index.
    with open(INDEX_FILE, 'w') as index_file:
        json.dump(index, index_file)
