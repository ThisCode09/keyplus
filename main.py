from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open('words.json', 'r') as file:
    words_list = json.load(file)


class WPMRequest(BaseModel):
    prompt: str
    typed: str
    elapsed_time: float
    mode: str = "words"


def calculate_metrics(prompt: str, typed: str, elapsed_time: float, mode: str):
    total_typed_len = len(typed)
    if total_typed_len == 0 or elapsed_time <= 0:
        return {"wpm": 0, "net_wpm": 0, "accuracy": 0.0, "errors": 0}

    time_in_mins = max(elapsed_time / 60.0, 0.001)

    # 1. Compare character by character up to typed length
    correct_chars = 0
    incorrect_chars = 0
    min_length = min(len(prompt), total_typed_len)

    for i in range(min_length):
        if prompt[i] == typed[i]:
            correct_chars += 1
        else:
            incorrect_chars += 1

    # Any extra characters typed beyond prompt length count as errors
    if total_typed_len > len(prompt):
        incorrect_chars += (total_typed_len - len(prompt))

    # 2. Gross WPM (Raw speed regardless of errors)
    gross_wpm = (total_typed_len / 5.0) / time_in_mins

    # 3. Net WPM (Gross WPM penalized by error rate per minute)
    error_penalty = incorrect_chars / time_in_mins
    net_wpm = max(0, round(gross_wpm - error_penalty))

    # 4. Accuracy percentage
    raw_accuracy = (correct_chars / total_typed_len) * 100.0
    accuracy = round(min(max(raw_accuracy, 0.0), 100.0), 2)

    return {
        "wpm": net_wpm,               # Primary WPM score (Net WPM)
        "gross_wpm": round(gross_wpm), # Raw speed score
        "accuracy": accuracy,
        "errors": incorrect_chars
    }


@app.get("/api/words")
def get_words(count: int = Query(default=25, ge=1, le=200)):
    selected_words = random.choices(words_list, k=count)
    return {"words": selected_words}


@app.post("/api/calculate")
def calculate_wpm(data: WPMRequest):
    metrics = calculate_metrics(data.prompt, data.typed, data.elapsed_time, data.mode)
    return {
        "wpm": metrics["wpm"],
        "gross_wpm": metrics["gross_wpm"],
        "accuracy": metrics["accuracy"],
        "errors": metrics["errors"],
        "elapsed_time": round(data.elapsed_time, 2)
    }