import requests
import json
from collections import defaultdict

PSL_URL = "https://publicsuffix.org/list/public_suffix_list.dat"

def download_psl():
    print("Downloading Public Suffix List...")
    response = requests.get(PSL_URL)
    response.raise_for_status()
    return response.text.splitlines()

def clean_psl(lines):
    suffixes = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('//'):
            suffixes.append(line)
    return suffixes

def save_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {filename}")

def build_suffix_trie(suffixes):
    trie = {}
    for suffix in suffixes:
        parts = suffix.split('.')[::-1]  # reverse for trie
        node = trie
        for part in parts:
            node = node.setdefault(part, {})
        node['$'] = True  # end marker
    return trie

def main():
    lines = download_psl()
    suffixes = clean_psl(lines)
    save_json(suffixes, 'public_suffix_list.json')

    trie = build_suffix_trie(suffixes)
    save_json(trie, 'public_suffix_trie.json')

if __name__ == "__main__":
    main()

