import os
import re
import glob
import string
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Generator

DATASET_PATH = "datasets"


class DatasetProcessor(ABC):
    @abstractmethod
    def process(
        self, dataset_path: str, remove_tone: bool = False
    ) -> Generator[Dict, None, None]:
        pass

    @staticmethod
    def process_text(text: str, punctuation: str) -> List[str]:
        text = re.sub(r"#\d+", "", text)
        return [char for char in text if char not in punctuation]


class Aishell3Processor(DatasetProcessor):
    REPLACE_HANZI = {
        "聖": "圣",
        "龑": "䶮",
        "姍": "姗",
        "見": "见",
        "靂": "雳",
        "時": "时",
        "咘": "布",
        "芓": "字",
        "會": "会",
        "甯": "宁",
        "堺": "界",
        "沒": "没",
        "脹": "胀",
        "妳": "你",
        "愛": "爱",
        "後": "后",
        "峯": "峰",
        "給": "给",
        "龍": "龙",
        "魟": "𫚉",
        "扞": "捍",
        "們": "们",
        "鮑": "鲍",
        "堃": "坤",
        "來": "来",
        "渀": "奔",
    }

    MANUAL_FIXES = {
        "SSB17450244.wav": "他 ta1 不 bu2 到 dao4 两 liang3 岁 sui4 的 de5 儿 er2 子 zi5 碰 peng4 触 chu4 车 che1 钥 yao4 匙 shi5",
        "SSB09660370.wav": "偶 ou3 像 xiang4 喜 xi3 剧 ju4 电 dian4 视 shi4 剧 ju4 有 you3 什 shen2 么 me5",
    }

    def process(
        self, dataset_path: str, remove_tone: bool = True
    ) -> Generator[Dict, None, None]:
        for folder in ["train", "test"]:
            path = os.path.join(dataset_path, folder)
            with open(os.path.join(path, "content.txt"), "r") as f:
                lines = f.readlines()

            for line in lines:
                wav_filename, text = line.rstrip().split("\t")
                if wav_filename in self.MANUAL_FIXES:
                    text = self.MANUAL_FIXES[wav_filename]

                split_text = text.split(" ")
                pinyin = split_text[1::2]
                hanzi = split_text[::2]

                processed_hanzi = [self.REPLACE_HANZI.get(h, h) for h in hanzi]

                processed_pinyin = []
                for p in pinyin:
                    assert p[-1].isdigit()
                    if remove_tone:
                        p = p[:-1]
                        assert p.isalpha()
                    processed_pinyin.append(p)

                if len(pinyin) != len(hanzi):
                    print(f"Warning: Mismatch in lengths for ID {wav_filename}")
                    print(f"Hanzi: {hanzi}")
                    print(f"Pinyin: {pinyin}")
                    continue

                yield {
                    "word": list(zip(processed_pinyin, processed_hanzi)),
                    "wav_path": os.path.join(
                        folder, "wav", wav_filename.replace(".wav", "")[:-4]
                    ),
                    "speaker": wav_filename.replace(".wav", "")[:-4],
                    "id": wav_filename.replace(".wav", ""),
                }


class BiaobeiProcessor(DatasetProcessor):
    def process(
        self, dataset_path: str, remove_tone: bool = True
    ) -> Generator[Dict, None, None]:
        punctuation = string.punctuation + "。，、；：“”" "（）《》〈〉【】{}！？…—"

        def process_pinyin(pinyin: str, hanzi: List[str]) -> List[str]:
            words = pinyin.split()

            result = []
            hanzi_index = 0
            i = 0
            while i < len(words):
                if (
                    i + 1 < len(words)
                    and words[i + 1].startswith("er")
                    and hanzi_index < len(hanzi)
                ):
                    if hanzi[hanzi_index].endswith("儿"):
                        if remove_tone:
                            result.append(words[i][:-1] + "r")
                        else:
                            result.append(words[i][:-1] + "r" + words[i][-1])
                        i += 2
                        hanzi_index += 1
                    else:
                        result.append(words[i][:-1] if remove_tone else words[i])
                        i += 1
                        hanzi_index += 1
                else:
                    result.append(words[i][:-1] if remove_tone else words[i])
                    i += 1
                    hanzi_index += 1
            return result

        def process_hanzi(text: str) -> List[str]:
            result = []
            i = 0
            while i < len(text):
                if (
                    i + 1 < len(text)
                    and text[i + 1] == "儿"
                    and text[i] != "虐"
                    and text[i] != "二"
                ):
                    result.append(text[i] + "儿")
                    i += 2
                else:
                    result.append(text[i])
                    i += 1
            return result

        file_path = os.path.join(dataset_path, "ProsodyLabeling", "000001-010000.txt")
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        for i in range(0, len(lines), 2):
            if i + 1 >= len(lines):
                break

            first_line = lines[i].strip().split("\t")
            second_line = lines[i + 1].strip()

            if len(first_line) != 2 or not second_line:
                continue

            id_str, chinese_text = first_line

            if chinese_text == "这图#2难不成#2是#1Ｐ过的#4？":
                second_line = "zhe4 tu2 nan2 bu4 cheng2 shi4 pi1 guo4 de5"

            hanzi = process_hanzi(self.process_text(chinese_text, punctuation))
            pinyin = process_pinyin(second_line, hanzi)

            if len(pinyin) != len(hanzi):
                print(f"Warning: Mismatch in lengths for ID {id_str}")
                print(f"Hanzi: {hanzi}")
                print(f"Pinyin: {pinyin}")
                continue

            yield {
                "word": list(zip(pinyin, hanzi)),
                "wav_path": "Wave",
                "speaker": "0",
                "id": id_str,
            }


def get_processor(dataset_name: str) -> DatasetProcessor:
    processors = {"biaobei": BiaobeiProcessor(), "aishell3": Aishell3Processor()}
    return processors.get(dataset_name)


def process_dataset(dataset_path: str, processor: DatasetProcessor) -> None:
    for sentence in processor.process(dataset_path):
        processed_text = " ".join(pinyin for pinyin, _ in sentence["word"])

        output_path = os.path.join(
            dataset_path, sentence["wav_path"], f"{sentence['id']}.lab"
        )
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w") as text_output:
            text_output.write(processed_text.strip())


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
