import os
import re
import glob
import string
from tqdm import tqdm
from abc import ABC, abstractmethod
from typing import Dict, List, Generator, Any, Tuple


class DatasetProcessor(ABC):
    @abstractmethod
    def process(
        self, dataset_path: str, remove_tone: bool = False
    ) -> Generator[Dict[str, Any], None, None]:
        pass

    @staticmethod
    def process_text(text: str) -> List[str]:
        punctuation = (
            string.punctuation + "。，、；：“”" "（）《》〈〉【】{}！？…—「」～•■『』·"
        )
        text = re.sub(r"#\d+", "", text)
        return [char for char in text if char not in punctuation]

    @staticmethod
    def process_pinyin(
        pinyin: str, hanzi: List[str], remove_tone: bool = True
    ) -> List[str]:
        words = pinyin.split()
        result = []
        hanzi_len = len(hanzi)
        i = 0
        hanzi_index = 0

        while i < len(words):
            current_word = words[i]
            next_word = words[i + 1] if i + 1 < len(words) else ""
            append_er = (
                next_word.startswith("er")
                and hanzi_index < hanzi_len
                and hanzi[hanzi_index].endswith("儿")
            )

            if append_er and current_word[-2] != "r":
                result.append(
                    current_word[:-1] + "r" if remove_tone else current_word + "r"
                )
                i += 2  # Skip the next word
            else:
                result.append(current_word[:-1] if remove_tone else current_word)
                i += 1

            hanzi_index += 1

        return result

    @staticmethod
    def process_hanzi(text: str) -> List[str]:
        result = []
        i = 0
        while i < len(text):
            if (
                i + 1 < len(text)
                and text[i + 1] == "儿"
                and text[i] not in ["虐", "二"]
            ):
                result.append(text[i] + "儿")
                i += 2
            else:
                result.append(text[i])
                i += 1
        return result


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
    ) -> Generator[Dict[str, Any], None, None]:
        for folder in ["train", "test"]:
            path = os.path.join(dataset_path, folder)
            with open(os.path.join(path, "content.txt"), "r") as f:
                for line in f:
                    wav_filename, text = line.rstrip().split("\t")
                    text = self.MANUAL_FIXES.get(wav_filename, text)

                    split_text = text.split(" ")
                    pinyin, hanzi = split_text[1::2], split_text[::2]

                    processed_hanzi = [self.REPLACE_HANZI.get(h, h) for h in hanzi]
                    processed_pinyin = self.process_pinyin(
                        " ".join(pinyin), processed_hanzi, remove_tone
                    )

                    if len(processed_pinyin) != len(processed_hanzi):
                        print(pinyin, hanzi)
                        print(f"Warning: Mismatch in lengths for ID {wav_filename}")
                        continue

                    yield {
                        "word": list(zip(processed_pinyin, processed_hanzi)),
                        "wav_path": os.path.join(folder, "wav", wav_filename[:-8]),
                        "speaker": wav_filename[:-8],
                        "id": wav_filename[:-4],
                    }


class GeneralProcessor(DatasetProcessor):
    def convert_characters_to_pinyin(self, conv, text: str) -> List[str]:
        predicted_pinyin = conv(text)[0]
        return " ".join([p for p in predicted_pinyin if p is not None])

    def process(
        self,
        dataset_path: str,
        remove_tone: bool = True,
        character_type: str = "simplified",
    ) -> Generator[Dict[str, Any], None, None]:
        try:
            from g2pw import G2PWConverter
        except ImportError:
            raise ImportError(
                "The 'g2pw' package is required. Please install it using 'pip install g2pw'."
            )

        conv = G2PWConverter(
            style="pinyin",
            enable_non_tradional_chinese=(character_type == "simplified"),
        )

        for speaker_folder in glob.glob(os.path.join(dataset_path, "*")):
            if not os.path.isdir(speaker_folder):
                continue
            speaker_name = os.path.basename(speaker_folder)

            for lab_file in tqdm(
                glob.glob(os.path.join(speaker_folder, "*.hanzi")), desc=speaker_name
            ):
                with open(lab_file, "r") as f:
                    chinese_text = f.read().strip()

                pinyin_file = lab_file.replace(".hanzi", ".pinyin")
                if os.path.exists(pinyin_file):
                    with open(pinyin_file, "r") as f:
                        pinyin_text = f.read()
                else:
                    pinyin_text = self.convert_characters_to_pinyin(conv, chinese_text)
                    with open(pinyin_file, "w") as f:
                        f.write(pinyin_text)

                hanzi = self.process_hanzi(self.process_text(chinese_text))

                pinyin = self.process_pinyin(pinyin_text, hanzi, remove_tone)

                id_str = os.path.basename(lab_file).replace(".hanzi", "")
                if len(pinyin) != len(hanzi):
                    print(pinyin, hanzi)
                    print(f"Warning: Mismatch in lengths for ID {id_str}")
                    continue

                yield {
                    "word": list(zip(pinyin, hanzi)),
                    "wav_path": os.path.basename(speaker_folder),
                    "speaker": speaker_name,
                    "id": id_str,
                }


class BiaobeiProcessor(DatasetProcessor):
    def process(
        self, dataset_path: str, remove_tone: bool = True
    ) -> Generator[Dict[str, Any], None, None]:
        file_path = os.path.join(dataset_path, "ProsodyLabeling", "000001-010000.txt")
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()

        for i in range(0, len(lines), 2):
            if i + 1 >= len(lines):
                break

            id_str, chinese_text = lines[i].strip().split("\t")
            pinyin_text = lines[i + 1].strip()

            if chinese_text == "这图#2难不成#2是#1Ｐ过的#4？":
                pinyin_text = "zhe4 tu2 nan2 bu4 cheng2 shi4 pi1 guo4 de5"

            hanzi = self.process_hanzi(self.process_text(chinese_text))
            pinyin = self.process_pinyin(pinyin_text, hanzi, remove_tone)

            if len(pinyin) != len(hanzi):
                print(pinyin, hanzi)
                print(f"Warning: Mismatch in lengths for ID {id_str}")
                continue

            yield {
                "word": list(zip(pinyin, hanzi)),
                "wav_path": "Wave",
                "speaker": "0",
                "id": id_str,
            }


def get_processor(dataset_name: str) -> DatasetProcessor:
    processors = {
        "biaobei": BiaobeiProcessor(),
        "aishell3": Aishell3Processor(),
        "general": GeneralProcessor(),
    }
    return processors.get(dataset_name, GeneralProcessor())
