import glob
import tgt
import os
from copy import copy
from typing import Dict, List, Tuple
from preprocess import get_processor, DATASET_PATH


def create_new_tier(
    start_time: float,
    end_time: float,
    name: str,
    annotations: List[Tuple[tgt.core.Interval, str]],
) -> tgt.core.IntervalTier:
    new_tier = tgt.core.IntervalTier(
        start_time=start_time, end_time=end_time, name=name
    )
    for interval, text in annotations:
        new_anno = copy(interval)
        new_anno.text = text
        new_tier.add_annotation(new_anno)
    return new_tier


def process_textgrid(textgrid_path: str, sentence: Dict) -> tgt.core.TextGrid:
    textgrid = tgt.io.read_textgrid(textgrid_path)

    if not textgrid.has_tier("words") or not textgrid.has_tier("phones"):
        raise ValueError(f"Warning: {textgrid_path} was already preprocessed.")

    pinyin_tier = textgrid.get_tier_by_name("words")
    phones_tier = textgrid.get_tier_by_name("phones")

    pinyin_annotations = [
        (word, sentence["word"][i][0]) for i, word in enumerate(pinyin_tier)
    ]
    hanzi_annotations = [
        (word, sentence["word"][i][1]) for i, word in enumerate(pinyin_tier)
    ]

    new_tier_pinyin = create_new_tier(
        pinyin_tier.start_time, pinyin_tier.end_time, "pinyins", pinyin_annotations
    )
    new_tier_hanzi = create_new_tier(
        pinyin_tier.start_time, pinyin_tier.end_time, "hanzis", hanzi_annotations
    )

    textgrid_new = tgt.core.TextGrid(sentence["id"])
    textgrid_new.add_tier(new_tier_hanzi)
    textgrid_new.add_tier(new_tier_pinyin)
    textgrid_new.add_tier(phones_tier)

    return textgrid_new


def process_dataset(dataset_path: str, processor: object) -> None:
    for sentence in processor.process(dataset_path, remove_tone=False):
        text_grid_file = os.path.join(
            dataset_path, sentence["wav_path"], f"{sentence['id']}.TextGrid"
        )

        if not os.path.exists(text_grid_file):
            print(f"Dataset {dataset_path} is missing TextGrid files")
            break

        try:
            textgrid_new = process_textgrid(text_grid_file, sentence)
            tgt.write_to_file(textgrid_new, text_grid_file, format="long")
        except Exception:
            break


def main():
    for dataset_path in glob.glob(os.path.join(DATASET_PATH, "*")):
        if not os.path.isdir(dataset_path):
            continue

        dataset_name = os.path.basename(dataset_path)
        print(f"Processing dataset: {dataset_name}")

        processor = get_processor(dataset_name)
        if processor:
            process_dataset(dataset_path, processor)
        else:
            print(f"No processor found for dataset: {dataset_name}")


if __name__ == "__main__":
    main()
