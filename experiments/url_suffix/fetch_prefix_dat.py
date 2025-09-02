import requests
import csv
import collections
import tldextract
import json
import gzip
import io
import zipfile
from io import TextIOWrapper

TRANCO_URL = "https://tranco-list.eu/top-1m.csv.zip"  # Public mirror of Tranco list


def download_tranco_csv():
    print("📥 Downloading Tranco top 1M CSV...")
    response = requests.get(TRANCO_URL)
    response.raise_for_status()
    return response.content


def extract_domains(zip_bytes):
    print("🗂️ Extracting domains from ZIP...")
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for name in zf.namelist():
            with zf.open(name) as f:
                reader = csv.reader(TextIOWrapper(f, encoding='utf-8'))
                for i, row in enumerate(reader):
                    if not row:
                        continue
                    domain = row[-1].strip()  # works with 1- or 2-column format
                    if domain and '.' in domain:
                        if i < 1000:
                            print(f"🔹 Sample domain: {domain}")
                        yield domain


def extract_prefixes(domains, suffix_set):
    counts = collections.Counter()
    for domain in domains:
        ext = tldextract.extract(domain)
        subdomain = ext.subdomain
        if not subdomain:
            continue
        first_label = subdomain.split('.')[0].lower()
        if first_label and first_label not in suffix_set:
            counts[first_label] += 1
    return counts


def load_psl():
    print("📡 Loading Public Suffix List...")
    psl_text = requests.get("https://publicsuffix.org/list/public_suffix_list.dat").text
    suffixes = set()
    for line in psl_text.splitlines():
        line = line.strip()
        if line and not line.startswith("//"):
            suffixes.add(line.lstrip("*."))
    return suffixes


def main(top_n=100):
    #zip_bytes = download_tranco_csv()
    from bes.files.bf_file_ops import bf_file_ops
    zip_bytes = bf_file_ops.read('top-1m.csv.zip')
    domain_gen = extract_domains(zip_bytes)
    suffixes = load_psl()
    prefix_counts = extract_prefixes(domain_gen, suffixes)

    if not prefix_counts:
        print("⚠️ No prefixes found — check extraction logic.")
        return

    common_prefixes = [prefix for prefix, _ in prefix_counts.most_common(top_n)]

    print(f"\n✅ Top {top_n} prefixes:")
    for prefix in common_prefixes:
        print(f"  {prefix}")

    with open("top_prefixes.json", "w") as f:
        json.dump(common_prefixes, f, indent=2)
    print("\n💾 Saved top prefixes to: top_prefixes.json")


if __name__ == "__main__":
    main(top_n=100)
