import os
import pytest
from model import TextClassifier, tokenize, calculate_stylometrics

def test_tokenize():
    text = "Hello world! This is a test... shocking discovery!"
    tokens = tokenize(text)
    assert "hello" in tokens
    assert "world" in tokens
    assert "test" in tokens
    assert "shocking" in tokens
    assert "discovery" in tokens
    # Ensure punctuation is removed
    assert "!" not in tokens

def test_model_fit_and_predict():
    classifier = TextClassifier(alpha=1.0)
    X_train = [
        "fake news is bad", 
        "real news is good", 
        "shocking discovery made", 
        "this is trustworthy and factual"
    ]
    y_train = ["FAKE", "REAL", "FAKE", "REAL"]
    
    classifier.fit(X_train, y_train)
    
    # Check if ngrams (bigrams) are created
    # "shocking discovery" should be in vocab since stopwords are removed
    assert "shocking discovery" in classifier.vocab
    
    pred_label, confidence, impacts = classifier.predict("shocking discovery made")
    assert pred_label == "FAKE"
    assert confidence > 0.5
    
    pred_label_real, conf_real, _ = classifier.predict("real news is good")
    assert pred_label_real == "REAL"

def test_model_save_and_load(tmp_path):
    classifier = TextClassifier(alpha=1.0)
    X_train = ["fake news is bad", "real news is good"]
    y_train = ["FAKE", "REAL"]
    classifier.fit(X_train, y_train)
    
    model_path = tmp_path / "test_model.json"
    classifier.save(str(model_path))
    
    assert os.path.exists(str(model_path))
    
    # Load into new instance
    new_classifier = TextClassifier()
    assert new_classifier.load(str(model_path)) == True
    
    assert new_classifier.vocab == classifier.vocab
    assert new_classifier.priors == classifier.priors

def test_stylometrics():
    metrics = calculate_stylometrics("SHOCKING! You won't believe this secret conspiracy.")
    assert metrics["uppercase_ratio"] > 0
    assert metrics["exclamation_ratio"] > 0
    assert metrics["word_count"] > 5
