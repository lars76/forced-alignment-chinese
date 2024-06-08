from tqdm import tqdm
import os

DATASET_PATH = "/home/SSD/dataset/"
USE_PINYIN = False
# add spacing to treat every character as a single word
ADD_SPACING = True

# fantizi, japanese characters, uncommon characters
REPLACE_HANZI = {'聖':'圣',
                '龑':'䶮',
                '姍':'姗',
                '見':'见',
                '靂':'雳',
                '時':'时',
                '咘':'布',
                '芓':'字',
                '會':'会',
                '甯':'宁',
                '堺':'界',
                '沒':'没',
                '脹':'胀',
                '妳':'你',
                '愛':'爱',
                '後':'后',
                '峯':'峰',
                '給':'给',
                '龍':'龙',
                '魟':'𫚉',
                '扞':'捍',
                '們':'们',
                '鮑':'鲍',
                '堃':'坤',
                '來':'来',
                '渀':'奔'}

MANUAL_FIXES = {"SSB17450244.wav": "他 ta1 不 bu2 到 dao4 两 liang3 岁 sui4 的 de5 儿 er2 子 zi5 碰 peng4 触 chu4 车 che1 钥 yao4 匙 shi5",
                "SSB09660370.wav": "偶 ou3 像 xiang4 喜 xi3 剧 ju4 电 dian4 视 shi4 剧 ju4 有 you3 什 shen2 么 me5"}

def get_sentences(dataset_path):
    for folder in ["train", "test"]:
        path = os.path.join(dataset_path, folder)
        with open(os.path.join(path, "content.txt"), "r") as f:
            lines = f.readlines()

        for line in lines:
            wav_filename, text = line.rstrip().split("\t")
            if wav_filename in MANUAL_FIXES:
                text = MANUAL_FIXES[wav_filename]

            split_text = text.split(" ")
            pinyin = split_text[1::2]
            hanzi = split_text[::2]

            processed_hanzi = []
            for h in hanzi:
                if h in REPLACE_HANZI:
                    h = REPLACE_HANZI[h]
                processed_hanzi.append(h)
            
            processed_pinyin = []
            for p in pinyin:
                # handle erhua: change dianr3 to dian3 r5
                if p != "r5" and p[:-1] != "er" and p[-2] == "r":
                    processed_pinyin.extend([p[:-2] + p[-1] + " r5"])
                else:
                    processed_pinyin.append(p)

            assert len(processed_pinyin) == len(processed_hanzi)

            yield {"word":list(zip(processed_pinyin, processed_hanzi)),
                   "split": folder,
                   "speaker": wav_filename.replace(".wav", "")[:-4],
                   "id": wav_filename.replace('.wav', '')}

def main():
    for sentence in tqdm(get_sentences(DATASET_PATH)):
        processed_text = ""
        for pinyin, hanzi in sentence['word']:
            if USE_PINYIN:
                processed_text += pinyin
            else:
                processed_text += hanzi
            if ADD_SPACING:
                processed_text += " "

        with open(os.path.join(DATASET_PATH, sentence['split'], "wav",
                               sentence['speaker'],
                               sentence['id'] + '.lab'), "w") as text_output:
            text_output.write(processed_text.strip())

if __name__ == '__main__':
    main()