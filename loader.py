import json
def load_pages():
    with open("pages.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
def load_weights():
    with open("ranks.json", "r",encoding="utf-8") as f:
        data = json.load(f)
    return data
def load_texts():
    with open("texts.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data
def load_titles():
    with open("titles.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def combined(pages, texts, titles, weights):
    comb={}
    for number in pages:
        url = pages[number]
        comb[url] = {
            "title": titles[number],
            "text": texts[number],
            "weight": weights[number]
        }
    return comb
pages=load_pages()
weights=load_weights()
texts=load_texts()
titles=load_titles()

combined_data=combined(pages, texts, titles, weights)


