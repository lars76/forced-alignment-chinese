from pinyin_to_ipa import pinyin_to_ipa
from tqdm import tqdm
from preprocess import get_sentences, DATASET_PATH

DICTIONARY_NAME = "aishell3_pinyin_dictionary"

def pinyin_to_ipa_erhua(pinyin):
    ipas = list(pinyin_to_ipa(pinyin[:-1]))
    suffix_to_ipa = {
        "anr": "ɐʵ",
        "enr": "ɚ", "inr": "ɚ", "unr": "ɚ",
        "angr": "ɑ̃ʵ",
        "engr": "ɤ̃ʵ", "ingr": "ɤ̃ʵ",
        "iongr": "ʊ̃ʵ", "ongr": "ʊ̃ʵ",
        "our": "ou̯˞",
        "iur": "ou̯ʵ",
        "aor": "ou̯˞",
        "iaor": "ɑu̯ʵ",
        "eir": "ɚ", "uir": "ɚ",
        "air": "ɐʵ",
        "ier": "ɛʵ",
        "uer": "œʵ",
        "er": "ɤʵ",
        "or": "ɔʵ",
        "ar": "ɐʵ",
        "ir": "ɚ",
        "ur": "u˞",
        "vr": "ɚ"
    }
    strip_two = ["anr", "enr", "inr", "unr", "angr", "engr", "ingr", "iongr", "ongr"]
    
    new_ipas = []
    for ipa in ipas:
        ipa = list(ipa)
        for k, v in suffix_to_ipa.items():
            if pinyin.endswith(k):
                if k in strip_two:
                    ipa = ipa[:-2]
                else:
                    ipa = ipa[:-1]
                if pinyin == "jur" or pinyin == "yur":
                    ipa += ["ɥɚ"]
                else:
                    ipa += [v]
                break
        new_ipas.append(ipa)

    return new_ipas

def is_erhua(pinyin):
    return pinyin[-1] == 'r' and pinyin != "er"

def main():
    pinyins = set()
    for sentence in tqdm(get_sentences(DATASET_PATH)):
        for pinyin, hanzi in sentence['word']:
            pinyins.add(pinyin)
    pinyins = sorted(pinyins)
    
    print(f"Number of pinyins: {len(pinyins)}")
    
    erhuas = []
    for pinyin in pinyins:
        erhua = pinyin[-1] == 'r' and pinyin != "er"
        if erhua:
            erhuas.append(pinyin)

    new_entries = []
    for pinyin in pinyins:
        erhua = is_erhua(pinyin)
        if erhua:
            ipas = pinyin_to_ipa_erhua(pinyin)
        else:
            ipas = pinyin_to_ipa(pinyin)
        
        for ipa in ipas:
            ipa = ' '.join(ipa)
            if erhua:
                new_entries.append((pinyin, ipa))
            else:
                new_entries.append((pinyin, ipa))
    new_entries = sorted(set(new_entries))

    with open(f"{DICTIONARY_NAME}.txt", "w") as f:
        for pinyin, ipa in new_entries:
            if "yo	w o" == f"{pinyin}\t{ipa}":
                ipa = "j ɔ"
            f.write(f"{pinyin}\t{ipa}\n")
    
if __name__ == '__main__':
    main()