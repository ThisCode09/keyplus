import json
import random

with open('words.json','r') as file:
    words = json.load(file)

words_no = [10,25,50,100]
def generate_words(n):
    return random.choices(words,k=n)
        

