import os, json, random
from pathlib import Path
from utils.loader import collect_files, load_any

random.seed(42)

DATA_DIR = "data/lectures"
OUT_PATH = "data/lecture_instructions.jsonl"

TEMPLATE = (
    "You are a helpful lecturer. Based on the following lecture passage, "
    "answer the user's question concisely.\n\n"
    "### PASSAGE\n{passage}\n\n"
    "### QUESTION\n{question}\n\n"
    "### ANSWER\n{answer}"
)

# toy Q generation; replace with your own Q&A or notes if you have them
GENERIC_QS = [
    # Networking fundamentals
    "What are the key takeaways from this networking concept?",
    "Explain the main idea of this protocol in simple terms.",
    "List 3 important factors that affect network performance.",
    "Give a real-world example of where this networking principle applies.",
    "How does this relate to previous networking topics such as OSI layers?",

    # DNS specific
    "What role does DNS play in network communication?",
    "Explain the difference between recursive and iterative DNS queries.",
    "List 3 common DNS records and their functions.",
    "Give a real-world example of DNS failure and its impact.",
    "How does DNS caching improve network efficiency?",

    # Nodal / Calculations
    "What are the key steps in nodal analysis for a given network?",
    "Explain how Kirchhoff’s Current Law applies in nodal calculations.",
    "List 3 equations commonly derived in nodal network analysis.",
    "Provide a real-world example where nodal analysis is applied in network design.",
    "How does nodal calculation relate to circuit analysis methods like mesh analysis?",

    # Applied / Advanced
    "How do latency, throughput, and bandwidth relate in networking?",
    "What are the implications of packet loss in a DNS-based system?",
    "Explain how subnetting affects nodal connections in IP networks.",
    "List 3 strategies to improve reliability in network node design.",
    "How does fault tolerance relate to nodal and DNS-based systems?"
]


def chunk(text, size=800, overlap=150):
    tokens = text.split()
    out, i = [], 0
    while i < len(tokens):
        out.append(" ".join(tokens[i:i+size]))
        i += size - overlap
    return out

def main():
    files = collect_files(DATA_DIR)
    os.makedirs(Path(OUT_PATH).parent, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as out:
        for fp in files:
            text = load_any(fp)
            for ch in chunk(text):
                q = random.choice(GENERIC_QS)
                # trivial "answer" bootstrap: use the first 3-4 sentences of the chunk
                ans = " ".join(ch.split(".")[:3]).strip()
                prompt = TEMPLATE.format(passage=ch, question=q, answer=ans)
                rec = {"prompt": prompt, "response": ans}
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"Wrote {OUT_PATH}")

if __name__ == "__main__":
    main()
