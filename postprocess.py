import glob
import tgt
import os
from tqdm import tqdm
from copy import copy
from preprocess import get_sentences, DATASET_PATH

def main():
    word_dataset = {}
    for sentence in get_sentences(DATASET_PATH, remove_tone=False):
        word_dataset[sentence['id']] = [{"pinyins":pinyin, "hanzis":hanzi} for pinyin, hanzi in sentence['word']]

    files = glob.glob(f"{DATASET_PATH}/**/**/**/*.TextGrid")
    for filename in tqdm(files):
        basename = os.path.basename(filename).replace(".TextGrid", "")

        words = word_dataset[basename]
        textgrid = tgt.io.read_textgrid(filename)
        pinyin_tier = textgrid.get_tier_by_name("words")
        phones_tier = textgrid.get_tier_by_name("phones")
        
        # add new section with hanzis, pinyins (containing tone)
        new_tier_pinyin = tgt.core.IntervalTier(start_time=pinyin_tier.start_time, end_time=pinyin_tier.end_time, name="pinyins")
        new_tier_hanzi = tgt.core.IntervalTier(start_time=pinyin_tier.start_time, end_time=pinyin_tier.end_time, name="hanzis")

        for cur_i, word in enumerate(pinyin_tier):
            new_anno = copy(word)
            new_anno.text = words[cur_i]["pinyins"]
            new_tier_pinyin.add_annotation(new_anno)
            
            new_anno = copy(word)
            new_anno.text = words[cur_i]["hanzis"]
            new_tier_hanzi.add_annotation(new_anno)

        textgrid_new = tgt.core.TextGrid(basename)
        textgrid_new.add_tier(new_tier_hanzi)
        textgrid_new.add_tier(new_tier_pinyin)
        textgrid_new.add_tier(phones_tier)
        tgt.write_to_file(textgrid_new, filename, format="long")

if __name__ == '__main__':
    main()