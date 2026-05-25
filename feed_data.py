import os
import httpx
import time

# Primary and fallback URLs for the widely used "Fake or Real News" dataset (~6300 articles)
DATASET_URL = "https://raw.githubusercontent.com/joolsa/fake_real_news_dataset/master/fake_or_real_news.csv"
FALLBACK_URL = "https://raw.githubusercontent.com/lutzhamel/fake-news/master/data/fake_or_real_news.csv"

LOCAL_CSV_PATH = os.path.join("data", "fake_or_real_news.csv")
API_ENDPOINT = "http://127.0.0.1:8000/api/train/csv"

def download_dataset():
    print(f"📥 Downloading dataset from {DATASET_URL}...")
    try:
        # We use httpx which was installed for our tests
        with httpx.Client(follow_redirects=True, timeout=120.0) as client:
            response = client.get(DATASET_URL)
            if response.status_code != 200:
                print(f"Primary URL failed (Status {response.status_code}). Trying fallback URL...")
                response = client.get(FALLBACK_URL)
            
            response.raise_for_status()
            
            os.makedirs("data", exist_ok=True)
            with open(LOCAL_CSV_PATH, "wb") as f:
                f.write(response.content)
                
            mb_size = len(response.content) / 1024 / 1024
            print(f"✅ Successfully downloaded dataset to {LOCAL_CSV_PATH} ({mb_size:.2f} MB)")
            return True
            
    except Exception as e:
        print(f"❌ Failed to download dataset: {e}")
        return False

def feed_to_server():
    print(f"\n🚀 Uploading {LOCAL_CSV_PATH} to {API_ENDPOINT} for training...")
    print("⏳ This might take a few moments as the model extracts bigrams from thousands of articles...")
    start_time = time.time()
    
    try:
        with open(LOCAL_CSV_PATH, "rb") as f:
            file_content = f.read()
            
        # We send it as multipart/form-data exactly like the browser would
        with httpx.Client(timeout=300.0) as client:
            files = {'file': ('fake_or_real_news.csv', file_content, 'text/csv')}
            data = {
                'text_column': 'text',
                'label_column': 'label',
                'test_size': '0.2'
            }
            
            response = client.post(API_ENDPOINT, data=data, files=files)
            
            if response.status_code == 200:
                result = response.json()
                elapsed = time.time() - start_time
                print(f"\n✅ Training completed successfully in {elapsed:.2f} seconds!")
                
                # Extract and format metrics
                metrics = result.get("metrics", {})
                info = result.get("model_info", {})
                
                print("\n" + "="*35)
                print("📊 MODEL EVALUATION REPORT")
                print("="*35)
                print(f"Total Vocabulary Size: {info.get('vocab_size'):,}")
                print(f"Training Set Size:     {info.get('train_size_count'):,} articles")
                print(f"Test Set Size:         {info.get('test_size_count'):,} articles")
                print("-" * 35)
                print(f"Validation Accuracy:   {metrics.get('accuracy', 0) * 100:.2f}%")
                print(f"Precision (Fake):      {metrics.get('precision', 0) * 100:.2f}%")
                print(f"Recall (Fake):         {metrics.get('recall', 0) * 100:.2f}%")
                print(f"F1-Score:              {metrics.get('f1_score', 0) * 100:.2f}%")
                
                cm = metrics.get("confusion_matrix", {})
                print("\n" + "="*35)
                print("🧮 CONFUSION MATRIX (Test Data)")
                print("="*35)
                print(f"True REAL (TN): {cm.get('tn'):<5} | False FAKE (FP): {cm.get('fp')}")
                print(f"False REAL (FN): {cm.get('fn'):<4} | True FAKE (TP): {cm.get('tp')}")
                print("===================================\n")
                
                print("💡 Check your browser UI at http://127.0.0.1:8000 - the model is now live!")
                
            else:
                print(f"❌ Server Error {response.status_code}: {response.text}")
                
    except httpx.ConnectError:
        print("❌ Connection Error: Could not connect to the FastAPI server. Make sure it is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ An error occurred during upload: {e}")

if __name__ == "__main__":
    # 1. Download if not exists
    if not os.path.exists(LOCAL_CSV_PATH):
        success = download_dataset()
        if not success:
            exit(1)
    else:
        print(f"📁 Found existing dataset at {LOCAL_CSV_PATH}")
        
    # 2. Feed to server
    feed_to_server()
