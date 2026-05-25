import os
import csv
import httpx
import time

# URLs for the widely used LIAR dataset (short political statements)
LIAR_TRAIN_URL = "https://raw.githubusercontent.com/thiagorainmaker77/liar_dataset/master/train.tsv"
LIAR_VALID_URL = "https://raw.githubusercontent.com/thiagorainmaker77/liar_dataset/master/valid.tsv"
LIAR_TEST_URL = "https://raw.githubusercontent.com/thiagorainmaker77/liar_dataset/master/test.tsv"

LOCAL_PREVIOUS_CSV = os.path.join("data", "fake_or_real_news.csv")
COMBINED_CSV_PATH = os.path.join("data", "combined_datasets.csv")
API_ENDPOINT = "http://127.0.0.1:8000/api/train/csv"

def download_and_parse_liar(url):
    print(f"📥 Downloading LIAR dataset from {url}...")
    try:
        with httpx.Client(follow_redirects=True, timeout=60.0) as client:
            response = client.get(url)
            response.raise_for_status()
            
        rows = []
        for line in response.text.strip().split('\n'):
            parts = line.split('\t')
            if len(parts) >= 3:
                label = parts[1].strip().lower()
                text = parts[2].strip()
                
                # Clean and map LIAR's 6-way classification to our binary system
                if label in ['pants-fire', 'false', 'barely-true']:
                    mapped_label = 'FAKE'
                elif label in ['half-true', 'mostly-true', 'true']:
                    mapped_label = 'REAL'
                else:
                    continue
                    
                rows.append({"text": text, "label": mapped_label})
        return rows
    except Exception as e:
        import sys
        sys.exit(f"❌ Failed to fetch {url}: {e}\nAborting Mega-Training to prevent silent data loss.")

def main():
    combined_data = []
    
    # 1. Load our existing data to retain vocabulary and structural knowledge
    if os.path.exists(LOCAL_PREVIOUS_CSV):
        print(f"📁 Loading existing structural data from {LOCAL_PREVIOUS_CSV}...")
        try:
            with open(LOCAL_PREVIOUS_CSV, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Handle possible varying headers dynamically
                text_col = 'text' if 'text' in reader.fieldnames else reader.fieldnames[0]
                label_col = 'label' if 'label' in reader.fieldnames else reader.fieldnames[1]
                
                for row in reader:
                    combined_data.append({
                        "text": row[text_col],
                        "label": row[label_col]
                    })
            print(f"✅ Loaded {len(combined_data)} existing articles (2016-2017 baseline).")
        except Exception as e:
            print(f"Could not load previous dataset: {e}")
    else:
        print("⚠️ Previous dataset not found! We will only train on LIAR data.")
    
    # 2. Download and parse the modern, short-statement LIAR splits
    print("\n🌐 Fetching diverse short-form statements from LIAR dataset...")
    liar_data = []
    liar_data.extend(download_and_parse_liar(LIAR_TRAIN_URL))
    liar_data.extend(download_and_parse_liar(LIAR_VALID_URL))
    liar_data.extend(download_and_parse_liar(LIAR_TEST_URL))
    
    print(f"✅ Extracted and mapped {len(liar_data)} statements from the LIAR dataset.")
    
    # Combine datasets
    combined_data.extend(liar_data)
    
    # 3. Save combined massive dataset locally
    print(f"\n💾 Writing combined mega-dataset ({len(combined_data)} total records) to {COMBINED_CSV_PATH}...")
    os.makedirs("data", exist_ok=True)
    with open(COMBINED_CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['text', 'label'])
        writer.writeheader()
        writer.writerows(combined_data)
        
    # 4. Upload to our local training endpoint
    print(f"\n🚀 Uploading to {API_ENDPOINT} for Full Batch Training...")
    print("⏳ This combines both domain styles simultaneously. It may take 1-2 minutes...")
    start_time = time.time()
    
    try:
        with open(COMBINED_CSV_PATH, "rb") as f:
            file_content = f.read()
            
        with httpx.Client(timeout=600.0) as client:
            files = {'file': ('combined_datasets.csv', file_content, 'text/csv')}
            data = {
                'text_column': 'text',
                'label_column': 'label',
                'test_size': '0.2'
            }
            
            response = client.post(API_ENDPOINT, data=data, files=files)
            
            if response.status_code == 200:
                result = response.json()
                elapsed = time.time() - start_time
                print(f"\n✅ Mega-Training completed successfully in {elapsed:.2f} seconds!")
                
                metrics = result.get("metrics", {})
                info = result.get("model_info", {})
                
                print("\n" + "="*35)
                print("📊 SCALED MODEL EVALUATION REPORT")
                print("="*35)
                print(f"Total Vocabulary Size: {info.get('vocab_size'):,}")
                print(f"Training Set Size:     {info.get('train_size_count'):,} articles/statements")
                print(f"Test Set Size:         {info.get('test_size_count'):,} articles/statements")
                print("-" * 35)
                print(f"Validation Accuracy:   {metrics.get('accuracy', 0) * 100:.2f}%")
                print(f"Precision (Fake):      {metrics.get('precision', 0) * 100:.2f}%")
                print(f"Recall (Fake):         {metrics.get('recall', 0) * 100:.2f}%")
                print(f"F1-Score:              {metrics.get('f1_score', 0) * 100:.2f}%")
                print("===================================\n")
                print("💡 Your model is now multi-domain aware! Check your browser UI.")
                
            else:
                print(f"❌ Server Error {response.status_code}: {response.text}")
                
    except httpx.ConnectError:
        print("❌ Connection Error: Could not connect to the FastAPI server. Make sure it is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ An error occurred during upload: {e}")

if __name__ == "__main__":
    main()
