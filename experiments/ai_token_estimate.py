from pathlib import Path
import tiktoken

# pick model tokenizer, e.g. "gpt-4o-mini"
#enc = tiktoken.encoding_for_model("cl100k_base")
enc = tiktoken.get_encoding("cl100k_base")

with open("all_code.py", "r", encoding="utf-8", errors="ignore") as f:
  text = f.read()
tokens = len(enc.encode(text))
print(f"Total tokens: {tokens:,}")
