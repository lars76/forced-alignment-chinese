from pinyin_to_ipa import pinyin_to_ipa
import glob
import os
from typing import Set, List, Tuple
from preprocess import get_processor, DATASET_PATH

DICTIONARY_NAME = "pinyin_dictionary"

ERHUA_SUFFIX_TO_IPA = {
    "anr": "ɐ ɻ",
    "enr": "ɚ",
    "inr": "ɚ",
    "unr": "ɚ",
    "angr": "ɑ̃ ɻ",
    "engr": "ɤ̃ ɻ",
    "ingr": "ɤ̃ ɻ",
    "iongr": "ʊ̃ ɻ",
    "ongr": "ʊ̃ ɻ",
    "our": "ou̯˞",
    "iur": "ou̯ ɻ",
    "aor": "ou̯˞",
    "iaor": "ɑu̯ ɻ",
    "eir": "ɚ",
    "uir": "ɚ",
    "air": "ɐ ɻ",
    "ier": "ɛ ɻ",
    "uer": "œ ɻ",
    "er": "ɤ ɻ",
    "or": "ɔ ɻ",
    "ar": "ɐ ɻ",
    "ir": "ɚ",
    "ur": "u˞",
    "vr": "ɚ",
}

STRIP_TWO = {"anr", "enr", "inr", "unr", "angr", "engr", "ingr", "iongr", "ongr"}


def pinyin_to_ipa_erhua(pinyin: str) -> List[str]:
    ipas = list(pinyin_to_ipa(pinyin[:-1]))

    new_ipas = []
    for ipa in ipas:
        ipa = list(ipa)
        for suffix, replacement in ERHUA_SUFFIX_TO_IPA.items():
            if pinyin.endswith(suffix):
                ipa = ipa[:-2] if suffix in STRIP_TWO else ipa[:-1]
                if pinyin in {"jur", "yur"}:
                    ipa.append("ɥɚ")
                else:
                    ipa.append(replacement)
                break
        new_ipas.append(ipa)
    return new_ipas


def is_erhua(pinyin: str) -> bool:
    return pinyin.endswith("r") and pinyin != "er"


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
        ipas = (
            pinyin_to_ipa_erhua(pinyin) if is_erhua(pinyin) else pinyin_to_ipa(pinyin)
        )
        entries.extend((pinyin, " ".join(ipa)) for ipa in ipas)
    return sorted(set(entries))


def write_dictionary(entries: List[Tuple[str, str]], filename: str) -> None:
    with open(filename, "w") as f:
        for pinyin, ipa in entries:
            if pinyin == "yo" and ipa == "w o":
                ipa = "j ɔ"
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
