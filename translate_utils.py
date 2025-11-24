# translate_utils.py
import requests

def translate(text, target_lang="es"):
    url = (
        "https://translate.googleapis.com/translate_a/single?"
        f"client=gtx&sl=en&tl={target_lang}&dt=t&q={text}"
    )
    r = requests.get(url)
    return r.json()[0][0][0]
