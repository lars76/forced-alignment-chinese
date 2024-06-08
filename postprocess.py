import glob
import tgt
import os
from tqdm import tqdm
from copy import copy
from preprocess import get_sentences, DATASET_PATH, USE_PINYIN

def main():
    word_dataset = {}
    for sentence in get_sentences(DATASET_PATH):
        word_dataset[sentence['id']] = [{"pinyins":pinyin, "hanzis":hanzi} for pinyin, hanzi in sentence['word']]

    files = glob.glob(f"{DATASET_PATH}/**/**/**/*.TextGrid")
    for filename in tqdm(files):
        basename = os.path.basename(filename).replace(".TextGrid", "")

        words = word_dataset[basename]
        textgrid = tgt.io.read_textgrid(filename)
        word_tier = textgrid.get_tier_by_name("words")
        
        # already processed pinyins, add new section with hanzis
        if USE_PINYIN:
            name = "hanzis"
        else:
            name = "pinyins"
        new_tier = tgt.core.IntervalTier(start_time=word_tier.start_time, end_time=word_tier.end_time, name=name)
        
        cur_i = 0
        for word in word_tier:
            start_time, end_time, text = word.start_time, word.end_time, word.text
            
            new_anno = copy(word)
            new_anno.text = " ".join([k[name] for k in words[cur_i : cur_i + len(text)]])
            new_tier.add_annotation(new_anno)

            cur_i += len(text)

        textgrid.add_tier(new_tier)
        tgt.write_to_file(textgrid, filename, format="long")

if __name__ == '__main__':
    main()