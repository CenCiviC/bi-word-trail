# Word Trail

Word Autocomplete Recommendation System

A system that recommends words based on frequency when entering prefixes in English, Italian, and Japanese.

## Features

- Prefix-based word recommendation (e.g., "wo" → "word", "world")
- Frequency-based sorting using the wordfreq library
- Multi-language support (English, Italian, Japanese)
- Personalized recommendation based on user feedback
- Sentence pattern analysis and profile building per user

## Installation

```bash
uv sync
```

## Usage

### Web Application

Run the Flask web application:

```bash
uv run python app.py
```

The application will be available at `http://localhost:5050`

### Basic Recommendation System

Run the command-line interface:

```bash
uv run python main.py
```

### User Simulation and Personalized Recommendation Testing

**Method 1: Run All (Recommended)**
```bash
uv run python user_simulate/run_all.py
```

**Method 2: Step-by-Step Execution**
```bash
# Step 1: Generate user-specific sentences
uv run python user_simulate/generate_user_data.py

# Step 2: Build profiles
uv run python user_simulate/build_profiles.py

# Step 3: Test personalized recommendations
uv run python user_simulate/test_personalization.py
```

## Example

```python
from src.recommender import MultiLanguageRecommender

# Initialize multi-language recommendation system
recommender = MultiLanguageRecommender(languages=["en", "it", "ja"])

# Recommend English words
recommendations = recommender.recommend("wo", lang="en", top_n=10)
for word, freq in recommendations:
    print(f"{word}: {freq:.2e}")
```

