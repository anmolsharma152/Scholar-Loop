---
difficulty: easy
last_sent:
review_count: 0
tags:
  - nlp
  - fundamentals
topic: ml-ai
---

# NLP Fundamentals

Natural Language Processing (NLP) is the field of enabling machines to understand, interpret, and generate human language. The NLP pipeline transforms raw text into structured representations that models can learn from.

## The NLP Pipeline

Raw text → Tokenization → Cleaning → Feature Extraction → Modeling

Each step reduces the complexity of language while preserving meaningful information.

## Tokenization

Tokenization splits text into individual units (tokens). It's the first and most critical preprocessing step.

| Method | Unit | Example | When to Use |
|--------|------|---------|-------------|
| Word-level | Words | `["I", "love", "NLP"]` | Simple tasks, large vocab |
| Character-level | Characters | `["I", " ", "l", "o", "v", "e"]` | Morphologically rich languages |
| Subword (BPE) | Byte pairs | `["I", "lov", "e", "NLP"]` | Modern LLMs, open vocabulary |
| Sentencepiece | Subword | `["▁I", "▁love", "▁NLP"]` | Language-agnostic tokenization |

Subword tokenization (BPE, WordPiece, SentencePiece) is the modern standard — it balances vocabulary size with the ability to handle rare words via decomposition.

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokens = tokenizer.encode("Reinforcement learning is fascinating")
print(tokenizer.convert_ids_to_tokens(tokens))
# ['Re', 'inforcement', ' learning', ' is', ' fascinating']
```

## Text Cleaning

Common preprocessing steps applied before feature extraction:

- **Lowercasing**: Reduces vocabulary size (but loses case information — bad for NER)
- **Stop word removal**: Removes common words ("the", "is", "and") — useful for bag-of-words, harmful for transformers
- **Stemming**: Crude suffix removal — "running" → "run", "better" → "better" (fails)
- **Lemmatization**: Dictionary-based normalization — "better" → "good", "ran" → "run"

```python
import nltk
from nltk.stem import WordNetLemmatizer, PorterStemmer

lemmatizer = WordNetLemmatizer()
stemmer = PorterStemmer()

words = ["running", "better", "studies", "geese"]
for w in words:
    print(f"{w} → stem: {stemmer.stem(w)}, lemma: {lemmatizer.lemmatize(w)}")
# running → stem: run, lemma: running
# better → stem: better, lemma: better (needs POS tag for correct lemmatization)
# studies → stem: studi, lemma: study
# geese → stem: gees, lemma: goose
```

## Bag of Words (BoW)

Represents documents as vectors of word counts. Ignores word order — a fundamental limitation.

```python
from sklearn.feature_extraction.text import CountVectorizer

corpus = [
    "the cat sat on the mat",
    "the dog sat on the log"
]
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(corpus)
print(vectorizer.get_feature_names_out())
print(X.toarray())
# Features: ['cat', 'dog', 'log', 'mat', 'on', 'sat', 'the']
# Doc 1:   [  1,    0,    0,    1,    1,    1,    2 ]
# Doc 2:   [  0,    1,    1,    0,    1,    1,    2 ]
```

## TF-IDF

Term Frequency–Inverse Document Frequency weights words by importance — frequent in a document but rare across documents get higher scores.

$$\text{TF-IDF}(t, d) = \text{TF}(t,d) \times \log\frac{N}{\text{DF}(t)}$$

- **TF**: How often term $t$ appears in document $d$
- **IDF**: How rare term $t$ is across all $N$ documents
- High TF-IDF = distinctive word for that document

```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(corpus)
print(vectorizer.get_feature_names_out())
print(X.toarray().round(2))
```

## N-grams

Capture local word order by considering sequences of $n$ words:

| N-gram | Tokens | Captures |
|--------|--------|----------|
| Unigram (1) | "the", "cat" | Individual words |
| Bigram (2) | "the cat", "cat sat" | Word pairs |
| Trigram (3) | "the cat sat", "cat sat on" | Three-word phrases |

Bigrams help distinguish "not good" from "good" — unigrams would lose this negation.

```python
vectorizer = CountVectorizer(ngram_range=(1, 2))  # uni + bigrams
X = vectorizer.fit_transform(["not good", "very good"])
print(vectorizer.get_feature_names_out())
# ['good', 'not', 'not good', 'very', 'very good']
```

## Word Embeddings

Dense, low-dimensional vector representations that capture semantic meaning. Words with similar meanings have similar vectors.

### Word2Vec

Two architectures:
- **CBOW**: Predict center word from context
- **Skip-gram**: Predict context words from center word

Key property: `vector("king") - vector("man") + vector("woman") ≈ vector("queen")`

### GloVe

Global Vectors builds embeddings from co-occurrence statistics across the entire corpus, balancing local (like Word2Vec) and global matrix factorization approaches.

```python
import gensim.downloader as api

model = api.load("word2vec-google-news-300")
print(model.most_similar("python", topn=5))
# [('snake', 0.72), ('ruby', 0.68), ...]
print(model["king"] - model["man"] + model["woman"])  # ≈ vector("queen")
```

## Key Takeaways

- Tokenization choice impacts downstream performance; subword (BPE) is the modern default
- TF-IDF improves over raw counts by downweighting ubiquitous terms
- Stop word removal and stemming help simple models but hurt transformer-based models
- Word embeddings capture semantic relationships that bag-of-words misses
- The NLP pipeline has been simplified by end-to-end models — but understanding preprocessing remains essential
- Modern LLMs handle tokenization internally — but knowing the fundamentals explains their failure modes

## Common Bugs

| Bug | Symptom | Fix |
|-----|---------|-----|
| Tokenizing before lowercasing | Duplicate features | Apply lowercasing first |
| Using word-level tokens with OOV words | Unknown tokens at inference | Use subword tokenization |
| Removing stop words for transformer input | Performance drops | Let transformers handle raw text |
| Applying stemming after lemmatization | Redundant, worse results | Use one or the other |
| Fitting TF-IDF on test data | Data leakage | `fit_transform(train)`, `transform(test)` |
