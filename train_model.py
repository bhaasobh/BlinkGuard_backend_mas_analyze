import numpy as np
import pandas as pd
import torch
from datasets import Dataset
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

torch.manual_seed(42)

MODEL_NAME = "distilbert-base-uncased"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

df = pd.read_csv(
    "dataset/SMSSpamCollection",
    sep="\t",
    header=None,
    names=["label", "text"],
)

df["label"] = df["label"].map({"spam": 1, "ham": 0})

dataset = Dataset.from_pandas(df)
dataset = dataset.shuffle(seed=42)
split = dataset.train_test_split(test_size=0.2)

train_ds = split["train"]
val_ds = split["test"]


def tokenize_fn(batch):
    return tokenizer(batch["text"], truncation=True)


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=1)
    return {
        "accuracy": accuracy_score(labels, predictions),
        "precision": classification_report(
            labels,
            predictions,
            target_names=["ham", "spam"],
            output_dict=True,
            zero_division=0,
        )["spam"]["precision"],
        "recall": classification_report(
            labels,
            predictions,
            target_names=["ham", "spam"],
            output_dict=True,
            zero_division=0,
        )["spam"]["recall"],
        "f1": classification_report(
            labels,
            predictions,
            target_names=["ham", "spam"],
            output_dict=True,
            zero_division=0,
        )["spam"]["f1-score"],
    }


train_ds = train_ds.map(tokenize_fn, batched=True)
val_ds = val_ds.map(tokenize_fn, batched=True)

data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=2,
)

args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=2,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=2e-5,
    logging_steps=100,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

trainer.train()

metrics = trainer.evaluate()
print("\n=== Validation Metrics ===")
for key, value in metrics.items():
    if key.startswith("eval_"):
        print(f"{key}: {value:.4f}")

predictions = trainer.predict(val_ds)
predicted_labels = np.argmax(predictions.predictions, axis=1)
true_labels = predictions.label_ids

print("\n=== Classification Report ===")
print(
    classification_report(
        true_labels,
        predicted_labels,
        target_names=["ham", "spam"],
        digits=4,
        zero_division=0,
    )
)

print("=== Confusion Matrix ===")
print(confusion_matrix(true_labels, predicted_labels))

trainer.save_model("spam_model")
tokenizer.save_pretrained("spam_model")
