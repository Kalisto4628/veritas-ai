import math
import re
import os
import joblib
from datetime import datetime

# Standard English stopwords list
STOPWORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'arent', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'cant', 'cannot', 'could',
    'couldnt', 'did', 'didnt', 'do', 'does', 'doesnt', 'doing', 'dont', 'down', 'during', 'each', 'few', 'for',
    'from', 'further', 'had', 'hadnt', 'has', 'hasnt', 'have', 'havent', 'having', 'he', 'hed', 'hell', 'hes',
    'her', 'here', 'heres', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'hows', 'i', 'id', 'ill', 'im',
    'ive', 'if', 'in', 'into', 'is', 'isnt', 'it', 'its', 'itself', 'lets', 'me', 'more', 'most', 'mustnt', 'my',
    'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours',
    'ourselves', 'out', 'over', 'own', 'same', 'shannt', 'she', 'shed', 'shell', 'shes', 'should', 'shouldnt',
    'so', 'some', 'such', 'than', 'that', 'thats', 'the', 'their', 'theirs', 'them', 'themselves', 'then',
    'there', 'theres', 'these', 'they', 'theyd', 'theyll', 'theyre', 'theyve', 'this', 'those', 'through',
    'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasnt', 'we', 'wed', 'well', 'were', 'weve', 'werent',
    'what', 'whats', 'when', 'whens', 'where', 'wheres', 'which', 'while', 'who', 'whos', 'whom', 'why', 'whys',
    'with', 'wont', 'would', 'wouldnt', 'you', 'youd', 'youll', 'youre', 'youve', 'your', 'yours', 'yourself',
    'yourselves'
}

def tokenize(text):
    """
    Cleans, lowercases, and tokenizes text into alphabetic tokens.
    """
    if not text:
        return []
    # Replace non-alphabetic characters with space, convert to lowercase
    text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
    # Split by whitespace and filter out empty tokens
    tokens = [w for w in text.split() if w]
    return tokens

class TextClassifier:
    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.vocab = set()
        self.idf = {}
        self.priors = {}
        self.likelihoods = {}  # {class: {word: log_prob}}
        self.accuracy = 0.0
        self.train_size = 0
        self.train_date = ""

    def fit(self, X, y):
        """
        Fits a TF-IDF weighted Naive Bayes Classifier.
        X: list of news texts
        y: list of labels (e.g. 'REAL', 'FAKE')
        """
        n_docs = len(X)
        self.train_size = n_docs
        self.train_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1. Tokenize docs and track word frequencies
        self.vocab = set()
        tokenized_docs = []
        df_counts = {}
        
        for doc in X:
            tokens = tokenize(doc)
            # Remove stopwords
            filtered = [w for w in tokens if w not in STOPWORDS]
            
            # Generate unigrams and bigrams
            ngrams = list(filtered)
            for j in range(len(filtered) - 1):
                ngrams.append(filtered[j] + " " + filtered[j+1])
                
            tokenized_docs.append(ngrams)
            
            # Document frequency (DF) tracking
            unique_words = set(ngrams)
            for w in unique_words:
                df_counts[w] = df_counts.get(w, 0) + 1
                self.vocab.add(w)

        vocab_size = len(self.vocab)
        if vocab_size == 0:
            vocab_size = 1

        # 2. Calculate IDF for each word in vocabulary
        # Smooth IDF: log(1 + n_docs / df) + 1
        for w in self.vocab:
            self.idf[w] = math.log(1.0 + (n_docs / df_counts[w])) + 1.0

        # 3. Calculate TF-IDF vectors for all documents
        tfidf_docs = []
        for doc_tokens in tokenized_docs:
            tfidf = {}
            doc_len = len(doc_tokens)
            if doc_len == 0:
                tfidf_docs.append(tfidf)
                continue
            
            # Term Frequency (TF) occurrences (Binary Naive Bayes)
            counts = {}
            for w in doc_tokens:
                counts[w] = 1.0  # Binary presence
            
            # TF-IDF calculation
            for w, cnt in counts.items():
                tfidf[w] = cnt * self.idf[w]
            
            tfidf_docs.append(tfidf)

        # 4. Group documents by class and calculate counts
        class_docs = {}
        for i, label in enumerate(y):
            if label not in class_docs:
                class_docs[label] = []
            class_docs[label].append(tfidf_docs[i])

        # 5. Compute class priors and term likelihoods
        self.priors = {}
        self.likelihoods = {}
        
        for label, docs in class_docs.items():
            # Class Prior
            self.priors[label] = len(docs) / n_docs
            
            # Calculate sum of TF-IDF weights per word in this class
            word_sums = {}
            total_tfidf_sum = 0.0
            
            for tfidf in docs:
                for w, val in tfidf.items():
                    word_sums[w] = word_sums.get(w, 0.0) + val
                    total_tfidf_sum += val

            # Calculate word likelihoods with Laplace smoothing
            # P(w|c) = (tfidf_sum_w + alpha) / (tfidf_sum_total + alpha * vocab_size)
            self.likelihoods[label] = {}
            denominator = total_tfidf_sum + self.alpha * vocab_size
            
            for w in self.vocab:
                word_sum = word_sums.get(w, 0.0)
                prob = (word_sum + self.alpha) / denominator
                self.likelihoods[label][w] = math.log(prob)
            
            # Save default for out-of-vocabulary words
            oov_prob = self.alpha / denominator
            self.likelihoods[label]["_OOV_"] = math.log(oov_prob)

    def predict_log_scores(self, text):
        """
        Calculates log probability scores for each class.
        """
        tokens = tokenize(text)
        filtered = [w for w in tokens if w not in STOPWORDS]
        
        # Generate unigrams and bigrams
        ngrams = list(filtered)
        for j in range(len(filtered) - 1):
            ngrams.append(filtered[j] + " " + filtered[j+1])
            
        doc_len = len(ngrams)
        
        # Initialize scores with log priors
        scores = {}
        for label, prior in self.priors.items():
            scores[label] = math.log(prior)

        if doc_len == 0:
            return scores, {}

        # Calculate TF of words in input (Binary occurrence)
        counts = {}
        for w in ngrams:
            counts[w] = 1.0

        tfidf = {}
        for w, cnt in counts.items():
            idf_val = self.idf.get(w, 1.0)  # Default IDF is 1 for unseen words
            tfidf[w] = cnt * idf_val

        # Add likelihoods
        word_contributions = {}
        for label in self.priors:
            likelihood_dict = self.likelihoods[label]
            oov_log_prob = likelihood_dict["_OOV_"]
            
            for w, tfidf_val in tfidf.items():
                log_prob = likelihood_dict.get(w, oov_log_prob)
                scores[label] += tfidf_val * log_prob
                
                # Track word contributions for explaining decision
                # Contribution is tfidf * log_prob
                if w not in word_contributions:
                    word_contributions[w] = {}
                word_contributions[w][label] = tfidf_val * log_prob

        return scores, tfidf

    def predict(self, text):
        """
        Predicts the label and returns confidence scores.
        """
        if not self.priors:
            return "REAL", 0.5, {}

        scores, tfidf = self.predict_log_scores(text)
        
        # Stable softmax-like conversion from log probabilities to probabilities
        max_score = max(scores.values())
        exp_scores = {label: math.exp(score - max_score) for label, score in scores.items()}
        total_exp = sum(exp_scores.values())
        
        probs = {label: val / total_exp for label, val in exp_scores.items()}
        
        # Find prediction
        prediction = max(probs, key=probs.get)
        confidence = probs[prediction]
        
        # Calculate feature contributions for each word
        # Feature impact = log P(w|REAL) - log P(w|FAKE)
        # Weight it by tfidf to get local word contribution
        word_impacts = []
        for w, tfidf_val in tfidf.items():
            # Get likelihoods
            log_prob_real = self.likelihoods["REAL"].get(w, self.likelihoods["REAL"]["_OOV_"])
            log_prob_fake = self.likelihoods["FAKE"].get(w, self.likelihoods["FAKE"]["_OOV_"])
            
            impact = tfidf_val * (log_prob_real - log_prob_fake)
            word_impacts.append({
                "word": w,
                "impact": impact,  # Positive indicates REAL, Negative indicates FAKE
                "tfidf": tfidf_val
            })
            
        # Sort word impacts by magnitude of impact
        word_impacts.sort(key=lambda x: abs(x["impact"]), reverse=True)

        return prediction, confidence, word_impacts

    def evaluate(self, X_test, y_test):
        """
        Evaluates the model on test data and returns metrics.
        """
        correct = 0
        tp, tn, fp, fn = 0, 0, 0, 0
        
        for doc, true_label in zip(X_test, y_test):
            pred_label, _, _ = self.predict(doc)
            if pred_label == true_label:
                correct += 1
            
            # Binary classification metrics: FAKE is positive, REAL is negative
            if true_label == "FAKE" and pred_label == "FAKE":
                tp += 1
            elif true_label == "REAL" and pred_label == "REAL":
                tn += 1
            elif true_label == "REAL" and pred_label == "FAKE":
                fp += 1
            elif true_label == "FAKE" and pred_label == "REAL":
                fn += 1

        total = len(y_test)
        accuracy = correct / total if total > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "confusion_matrix": {
                "tp": tp, "tn": tn, "fp": fp, "fn": fn
            }
        }

    def save(self, filepath):
        """
        Saves the model state to a binary file using joblib.
        """
        state = {
            "alpha": self.alpha,
            "vocab": self.vocab,
            "idf": self.idf,
            "priors": self.priors,
            "likelihoods": self.likelihoods,
            "accuracy": self.accuracy,
            "train_size": self.train_size,
            "train_date": self.train_date
        }
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(state, filepath)

    def load(self, filepath):
        """
        Loads the model state from a joblib file.
        """
        if not os.path.exists(filepath):
            return False
        try:
            state = joblib.load(filepath)
            self.alpha = state.get("alpha", 1.0)
            self.vocab = state.get("vocab", set())
            self.idf = state.get("idf", {})
            self.priors = state.get("priors", {})
            self.likelihoods = state.get("likelihoods", {})
            self.accuracy = state.get("accuracy", 0.0)
            self.train_size = state.get("train_size", 0)
            self.train_date = state.get("train_date", "")
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False


def calculate_stylometrics(text):
    """
    Computes linguistic/stylometric indicators from raw text.
    """
    if not text:
        return {}
    
    chars = len(text)
    words = len(text.split())
    if words == 0:
        words = 1
        
    sentences = len(re.split(r'[.!?]+', text))
    if sentences == 0:
        sentences = 1
        
    # Uppercase character ratio (for SHOUTING checks)
    caps_count = sum(1 for c in text if c.isupper())
    caps_ratio = (caps_count / chars) if chars > 0 else 0
    
    # Exclamation mark ratio
    excl_count = text.count('!')
    excl_ratio = (excl_count / words) * 100  # exclamations per 100 words
    
    # Question mark ratio
    q_count = text.count('?')
    q_ratio = (q_count / words) * 100
    
    # Average word length
    avg_word_len = sum(len(w) for w in text.split()) / words
    
    # Average sentence length
    avg_sentence_len = words / sentences
    
    # Readability estimate: Flesch-Kincaid Reading Ease approximation
    # Ease = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
    # Simple syllable count approximation
    def approx_syllables(w):
        w = w.lower()
        count = 0
        vowels = "aeiouy"
        if len(w) == 0:
            return 0
        if w[0] in vowels:
            count += 1
        for index in range(1, len(w)):
            if w[index] in vowels and w[index - 1] not in vowels:
                count += 1
        if w.endswith("e"):
            count -= 1
        if count == 0:
            count = 1
        return count
        
    total_syllables = sum(approx_syllables(w) for w in text.split())
    readability = 206.835 - 1.015 * avg_sentence_len - 84.6 * (total_syllables / words)
    # Clamp readability to [0, 100]
    readability = max(0, min(100, readability))
    
    # Sentiment/Subjectivity heuristics
    # Emotional clickbait words list
    emotional_words = {
        'shocking', 'unbelievable', 'secret', 'conspiracy', 'furious', 'banned', 'warning', 'exposed', 
        'lying', 'leak', 'insider', 'destroy', 'collapse', 'breaking', 'miracle', 'elite', 'alien', 'cure', 
        'jail', 'scandal', 'hidden', 'ban', 'spiked', 'hiding', 'desperately', 'truth', 'exposed'
    }
    tokens = tokenize(text)
    emo_count = sum(1 for w in tokens if w in emotional_words)
    subjectivity_score = (emo_count / words) * 100  # emotional word percentage
    
    return {
        "word_count": words,
        "sentence_count": sentences,
        "uppercase_ratio": round(caps_ratio * 100, 2),
        "exclamation_ratio": round(excl_ratio, 2),
        "question_ratio": round(q_ratio, 2),
        "avg_word_length": round(avg_word_len, 2),
        "avg_sentence_length": round(avg_sentence_len, 2),
        "readability_score": round(readability, 2),
        "subjectivity_score": round(subjectivity_score, 2)
    }
