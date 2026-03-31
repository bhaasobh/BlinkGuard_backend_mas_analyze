# Blinkguard Spam & Phishing Analysis Server

A proof-of-concept FastAPI server that analyzes messages for spam and phishing risk using a combination of a transformer-based spam detector and psychological phishing signals.

## Features

- Analyzes text messages with ML and psychology-based risk scoring
- Returns structured analysis including risk band, final decision, and psychological factors
- Persists reported phishing messages to MongoDB
- Includes model training helper and spam dataset resources

## Repository Structure

- `server.py` - FastAPI application exposing `/analyze` and `/report`
- `analyze_message.py` - Core analysis logic combining ML and psychological risk scoring
- `psychology_rules.py` - Rules for detecting psychological phishing signals
- `mongodb_handler.py` - Saves phishing reports to MongoDB
- `train_model.py` - Training script for building the spam classifier
- `dataset/SMSSpamCollection` - Spam dataset used for model training
- `spam_model/` - Saved model and tokenizer artifacts

## Requirements

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Environment

Create a `.env` file in the project root with at least the following values:

```env
MONGO_URI=mongodb+srv://<user>:<password>@<cluster>/<dbname>
PORT=3000
```

## Run the Server

Start the FastAPI server:

```bash
python server.py
```

Or use the provided batch file on Windows:

```bash
run_server.bat
```

The service will be available at `http://0.0.0.0:3000/` by default.

## API Endpoints

### `POST /analyze`

Analyzes a message and returns risk details.

Request body:

```json
{
  "message": "Your message text here"
}
```

Example curl:

```bash
curl -X POST http://localhost:3000/analyze \
  -H "Content-Type: application/json" \
  -d '{"message":"URGENT: Verify your account now"}'
```

### `POST /report`

Reports a phishing message to MongoDB.

Request body:

```json
{
  "message": "Suspicious phishing message text",
  "metadata": {
    "source": "frontend",
    "user": "example"
  }
}
```

## Example Output

The `/analyze` response includes:

- `ml_prediction`
- `ml_confidence`
- `ml_risk_score`
- `final_decision`
- `risk_band`
- `final_risk_score`
- `psychological_factors`
- `psychology_risk_scores`

## Notes

- The model is loaded from the local `spam_model/` directory, while the `model.safetensors` weights are downloaded from the Hugging Face repo at `https://huggingface.co/bahaasobeh/blinkguard/blob/main/model.safetensors`.
- If MongoDB is unavailable, analysis still works, but phishing reports may not be persisted.
- The project combines standard NLP with behavior-based phishing signals such as urgency, authority, fear, scarcity, and link presence.

## Training

To retrain or fine-tune the classifier, inspect `train_model.py` and the dataset in `dataset/`.
"# BlinkGuard_backend_mas_analyze" 
