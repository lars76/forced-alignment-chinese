import glob
import os
from typing import Set, List, Tuple
from preprocess import get_processor, DATASET_PATH
from pinyin_to_ipa import pinyin_to_ipa

DICTIONARY_NAME = "pinyin_dictionary"

# Dictionary for erhua transformations
# https://en.wikipedia.org/wiki/Erhua#Standard_rules
ERHUA_SUFFIX_TO_IPA = {
    "uangr": [["w", "ɑ̃ʵ"]],
    "iangr": [["j", "ɑ̃ʵ"]],
    "iongr": [["j", "ʊ̃ʵ"]],
    "vanr": [["ɥ", "ɐʵ"]],
    "uair": [["w", "ɐʵ"]],
    "ianr": [["j", "ɐʵ"]],
    "iaor": [["j", "ɑu̯˞"]],
    "uanr": [["w", "ɐʵ"]],
    "engr": [["ɤ̃ʵ"], ["ʊ̃˞"]],
    "angr": [["ɑ̃ʵ"]],
    "ongr": [["w", "ɤ̃ʵ"], ["ʊ̃˞"]],
    "ingr": [["j", "ɤ̃ʵ"]],
    "ver": [["ɥ", "œʵ"]],
    "uar": [["w", "äʵ"], ["w", "ɐʵ"]],
    "uor": [["w", "ɔʵ"]],
    "air": [["ɐʵ"]],
    "eir": [["ɚ"]],
    "aor": [["ɑu̯˞"]],
    "our": [["ou̯˞"]],
    "anr": [["ɐʵ"]],
    "enr": [["ɚ"]],
    "iar": [["j", "äʵ"], ["j", "ɐʵ"]],
    "ier": [["j", "ɛʵ"]],
    "iur": [["j", "ou̯ʵ"]],
    "inr": [["j", "ɚ"]],
    "uir": [["w", "ɚ"]],
    "unr": [["w", "ɚ"]],
    "vnr": [["ɥ", "ɚ"]],
    "ar": [["äʵ"], ["ɐʵ"]],
    "or": [["ɔʵ"]],
    "er": [["ɤʵ"]],
    "ur": [["u˞"]],
    "vr": [["ɥ", "ɚ"]],
    "ir": [["ɚ"]],
}


def apply_erhua(pinyin: str, ipa: List[str]) -> List[str]:
    """
    Apply erhua transformation to the given IPA representation.
    """
    # Remove final 'n' or 'ŋ' if present
    if ipa[-1] in ["ŋ", "n"]:
        ipa = ipa[:-1]

    # Remove last character if IPA has more than one character
    if len(ipa) > 1:
        ipa = ipa[:-1]

    result = []
    for pinyin_ending, ipa_endings in ERHUA_SUFFIX_TO_IPA.items():
        if pinyin.endswith(pinyin_ending) and pinyin != pinyin_ending:
            for ipa_ending in ipa_endings:
                # Remove first character of ipa_ending if it matches the last character of ipa
                if ipa[-1] == ipa_ending[0]:
                    ipa_ending = ipa_ending[1:]
                result.append(ipa + ipa_ending)
            break
    return result


def convert_pinyin_to_ipa(pinyin: str) -> List[List[str]]:
    """
    Convert a Pinyin string to its IPA representation(s).
    """
    # Check for erhua
    erhua = pinyin.endswith("r") and pinyin != "er"
    if erhua:
        pinyin = pinyin[:-1]

    ipa_output = []
    for ipa in pinyin_to_ipa(pinyin):
        ipa = list(ipa)

        # Special case for "yo"
        if pinyin == "yo" and ipa == ["w", "o"]:
            ipa = ["j", "ɔ"]

        if erhua:
            erhua_ipas = apply_erhua(pinyin + "r", ipa)
            ipa_output.extend([i for i in erhua_ipas if i not in ipa_output])
        else:
            ipa_output.append(ipa)

    return ipa_output


def process_dataset(dataset_path: str, dataset_name: str) -> Set[str]:
    pinyins = set()
    processor = get_processor(dataset_name)
    if processor:
        for sentence in processor.process(dataset_path):
            pinyins.update(pinyin for pinyin, _ in sentence["word"])
    else:
        print(f"No processor found for dataset: {dataset_name}")
    print(f"Number of pinyins: {len(pinyins)}")
    return pinyins


def generate_dictionary_entries(pinyins: Set[str]) -> List[Tuple[str, str]]:
    entries = []
    for pinyin in pinyins:
        ipas = convert_pinyin_to_ipa(pinyin)
        entries.extend((pinyin, " ".join(ipa).replace("ʵ", " ɻ")) for ipa in ipas)
    return sorted(set(entries))


def write_dictionary(entries: List[Tuple[str, str]], filename: str) -> None:
    with open(filename, "w") as f:
        for pinyin, ipa in entries:
            f.write(f"{pinyin}\t{ipa}\n")


def main():
    for dataset_path in glob.glob(os.path.join(DATASET_PATH, "*")):
        if not os.path.isdir(dataset_path):
            continue

        dataset_name = os.path.basename(dataset_path)
        print(f"Processing dataset: {dataset_name}")

        pinyins = process_dataset(dataset_path, dataset_name)
        entries = generate_dictionary_entries(pinyins)
        write_dictionary(entries, f"{dataset_name}_{DICTIONARY_NAME}.txt")


if __name__ == "__main__":
    main()
