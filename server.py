import os
import json
import csv
import io
import random
from fastapi import FastAPI, HTTPException, UploadFile, Form, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

from model import TextClassifier, calculate_stylometrics

# Setup paths relative to server file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

MODEL_PATH = os.path.join(DATA_DIR, "saved_model.joblib")
DEFAULT_DATASET_PATH = os.path.join(DATA_DIR, "default_dataset.json")

# Initialize classifier
classifier = TextClassifier(alpha=0.5)

# Load existing model or train default one
def initialize_model():
    if classifier.load(MODEL_PATH):
        print(f"Loaded existing model trained on {classifier.train_date} with {classifier.train_size} samples.")
        return
        
    # If saved model not found, look for default dataset to train
    if os.path.exists(DEFAULT_DATASET_PATH):
        try:
            with open(DEFAULT_DATASET_PATH, 'r') as f:
                data = json.load(f)
            
            X = [item["text"] for item in data]
            y = [item["label"] for item in data]
            
            # Shuffle and train
            combined = list(zip(X, y))
            random.seed(42)
            random.shuffle(combined)
            X_shuffled, y_shuffled = zip(*combined)
            
            classifier.fit(list(X_shuffled), list(y_shuffled))
            
            # Self-evaluate
            metrics = classifier.evaluate(list(X_shuffled), list(y_shuffled))
            classifier.accuracy = metrics["accuracy"]
            classifier.save(MODEL_PATH)
            print(f"Initialized new model on default dataset. Training size: {len(data)}, Self-Accuracy: {metrics['accuracy']:.2f}")
        except Exception as e:
            print(f"Error training default dataset during initialization: {e}")
    else:
        print("WARNING: Default dataset not found at initialization. Model is untrained.")

initialize_model()

# Create FastAPI app
app = FastAPI(title="Veritas AI API", version="1.0.0")

# Enable CORS for local development testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Schemas
class PredictionRequest(BaseModel):
    text: str

class SandboxItem(BaseModel):
    text: str
    label: str

class SandboxTrainingRequest(BaseModel):
    items: List[SandboxItem]

@app.post("/api/predict")
async def predict_news(request: PredictionRequest):
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    try:
        label, confidence, word_impacts = classifier.predict(text)
        stylometrics = calculate_stylometrics(text)
        
        # Sort word impacts so the UI can quickly extract top keywords
        top_real = [x for x in word_impacts if x["impact"] > 0.0001][:10]
        top_fake = [x for x in word_impacts if x["impact"] < -0.0001][:10]
        
        return {
            "label": label,
            "confidence": round(confidence, 4),
            "word_impacts": word_impacts,
            "top_words_real": top_real,
            "top_words_fake": top_fake,
            "stylometrics": stylometrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/api/train/sandbox")
async def train_sandbox(request: SandboxTrainingRequest):
    items = request.items
    if len(items) < 4:
        raise HTTPException(status_code=400, detail="At least 4 training examples are required.")
    
    try:
        X = [item.text for item in items]
        y = [item.label for item in items]
        
        # Fit classifier
        classifier.fit(X, y)
        
        # Self-evaluate
        metrics = classifier.evaluate(X, y)
        classifier.accuracy = metrics["accuracy"]
        classifier.save(MODEL_PATH)
        
        return {
            "status": "success",
            "metrics": metrics,
            "model_info": {
                "vocab_size": len(classifier.vocab),
                "train_size": classifier.train_size,
                "train_date": classifier.train_date,
                "accuracy": round(classifier.accuracy, 4)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sandbox training failed: {str(e)}")

@app.post("/api/train/csv")
async def train_csv(
    file: UploadFile = File(...),
    text_column: str = Form("text"),
    label_column: str = Form("label"),
    test_size: float = Form(0.2)
):
    # Verify file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")
        
    try:
        contents = await file.read()
        # Decode contents
        try:
            decoded = contents.decode("utf-8")
        except UnicodeDecodeError:
            decoded = contents.decode("latin-1")
            
        csv_file = io.StringIO(decoded)
        reader = csv.DictReader(csv_file)
        
        # Check if columns exist
        headers = reader.fieldnames
        if not headers:
            raise HTTPException(status_code=400, detail="CSV file is empty or invalid.")
            
        # Clean headers (strip spaces)
        cleaned_headers = [h.strip() for h in headers]
        text_col = text_column.strip()
        label_col = label_column.strip()
        
        matched_text_col = next((h for h in headers if h.strip() == text_col), None)
        matched_label_col = next((h for h in headers if h.strip() == label_col), None)
        
        if not matched_text_col or not matched_label_col:
            raise HTTPException(
                status_code=400, 
                detail=f"Columns not found. Provided text column: '{text_col}', label column: '{label_col}'. Available columns: {cleaned_headers}"
            )
            
        # Extract rows
        X = []
        y = []
        for row in reader:
            txt = row[matched_text_col]
            lbl = row[matched_label_col]
            if txt and lbl:
                lbl_clean = lbl.strip().upper()
                # Map label to REAL or FAKE
                if "FAKE" in lbl_clean or "0" == lbl_clean or "FALSE" in lbl_clean or "LIE" in lbl_clean:
                    mapped_lbl = "FAKE"
                else:
                    mapped_lbl = "REAL"
                X.append(txt.strip())
                y.append(mapped_lbl)
                
        if len(X) < 10:
            raise HTTPException(status_code=400, detail=f"Insufficient data in CSV. Found {len(X)} valid rows. Minimum of 10 rows required.")
            
        # Split train/test sets
        combined = list(zip(X, y))
        random.seed(42)
        random.shuffle(combined)
        
        split_idx = int(len(combined) * (1 - test_size))
        train_set = combined[:split_idx]
        test_set = combined[split_idx:]
        
        if not train_set or not test_set:
            raise HTTPException(status_code=400, detail="Test split size is too large or too small.")
            
        X_train, y_train = zip(*train_set)
        X_test, y_test = zip(*test_set)
        
        # Train new model
        new_classifier = TextClassifier(alpha=0.5)
        new_classifier.fit(list(X_train), list(y_train))
        
        # Evaluate on test set
        metrics = new_classifier.evaluate(list(X_test), list(y_test))
        new_classifier.accuracy = metrics["accuracy"]
        
        # Swap main classifier and save
        global classifier
        classifier = new_classifier
        classifier.save(MODEL_PATH)
        
        return {
            "status": "success",
            "metrics": metrics,
            "model_info": {
                "vocab_size": len(classifier.vocab),
                "train_size": classifier.train_size,
                "train_date": classifier.train_date,
                "accuracy": round(classifier.accuracy, 4),
                "test_size_count": len(X_test),
                "train_size_count": len(X_train)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to train on CSV file: {str(e)}")

@app.get("/api/model/info")
async def get_model_info():
    # Calculate top weights based on likelihood differences
    top_real = []
    top_fake = []
    if classifier.likelihoods and "REAL" in classifier.likelihoods and "FAKE" in classifier.likelihoods:
        real_likelihoods = classifier.likelihoods["REAL"]
        fake_likelihoods = classifier.likelihoods["FAKE"]
        
        diffs = []
        for w in classifier.vocab:
            if w in real_likelihoods and w in fake_likelihoods:
                diff = real_likelihoods[w] - fake_likelihoods[w]
                diffs.append((w, diff, real_likelihoods[w], fake_likelihoods[w]))
        
        # Sort by diff: positive diff indicates strongly associated with REAL
        diffs.sort(key=lambda x: x[1], reverse=True)
        top_real = [{"word": w, "diff": round(d, 4), "real_log": round(rl, 4), "fake_log": round(fl, 4)} for w, d, rl, fl in diffs[:50]]
        
        # Sort by diff ascending: negative diff indicates strongly associated with FAKE
        diffs_sorted_asc = sorted(diffs, key=lambda x: x[1])
        top_fake = [{"word": w, "diff": round(d, 4), "real_log": round(rl, 4), "fake_log": round(fl, 4)} for w, d, rl, fl in diffs_sorted_asc[:50]]
        
    return {
        "vocab_size": len(classifier.vocab),
        "train_size": classifier.train_size,
        "train_date": classifier.train_date or "Untrained",
        "accuracy": round(classifier.accuracy, 4),
        "alpha": classifier.alpha,
        "classes": list(classifier.priors.keys()) if classifier.priors else ["REAL", "FAKE"],
        "top_real": top_real,
        "top_fake": top_fake
    }

# Serve static files
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    # Run server locally on port 8000
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
