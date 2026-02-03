import os
from config import DOMAINS, EXAMPLE_TOPICS

DATA_DIR = "data"
OUTPUT_FILE = "domain_topics_list.txt"

def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        # Sort domains to ensure consistent order, maybe by English key
        sorted_keys = sorted(DOMAINS.keys())
        
        for domain_key in sorted_keys:
            chinese_name = DOMAINS[domain_key]
            topic_file = os.path.join(DATA_DIR, domain_key, f"{domain_key}.txt")
            
            out_f.write(f"Domain: {domain_key} ({chinese_name})\n")
            out_f.write("-" * 50 + "\n")
            
            # Add Example Topic first
            if domain_key in EXAMPLE_TOPICS:
                out_f.write(f"【Expert Example】{EXAMPLE_TOPICS[domain_key]}\n")

            if os.path.exists(topic_file):
                with open(topic_file, "r", encoding="utf-8") as f:
                    topics = [line.strip() for line in f if line.strip()]
                    for i, topic in enumerate(topics, 1):
                        out_f.write(f"{topic}\n")
            else:
                out_f.write("(No topic file found)\n")
            
            out_f.write("\n" + "=" * 50 + "\n\n")

    print(f"Topics list saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
