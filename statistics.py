import glob
import tgt
import os
from tqdm import tqdm
from copy import copy
from preprocess import get_sentences, DATASET_PATH, USE_PINYIN
from collections import Counter

MAPPER = [("˨˩˦","3"),
          ("˥˩","4"),
          ("˧˥", "2"),
          ("˥", "1")]

# 5647 with own
# 2 with TextGrid
# 0 with aishell3_alignment_tone
def main():
    files = glob.glob("../dataset/**/**/**/*.TextGrid")
    #files = glob.glob("TextGrid/**/*.TextGrid")
    #files = glob.glob("aishell3_alignment_tone/**/*.TextGrid")
    #print(files)
    ok = 0
    count_spn = 0
    chars = set()
    for filename in tqdm(files):
        basename = os.path.basename(filename).replace(".TextGrid", "")

        textgrid = tgt.io.read_textgrid(filename)

        pinyin_tier = textgrid.get_tier_by_name("pinyins")
        hanzi_tier = textgrid.get_tier_by_name("words")
        phones_tier = textgrid.get_tier_by_name("phones")
        #s = []
        all_ = ""
        for pinyin, hanzi in zip(pinyin_tier, hanzi_tier):
            all_ += hanzi.text
            #s.append((pinyin.start_time, pinyin.end_time, pinyin.text, hanzi.text))

            res = ""
            for phone in phones_tier:
                if phone.start_time >= pinyin.start_time and phone.end_time <= pinyin.end_time:
                    res += phone.text + " "
            #for k, v in MAPPER:
            #    res = res.replace(k, pinyin.text[-1])
            if "儿" in hanzi.text:
                print(hanzi.text, res, all_)#pinyin.text, 
        """
        print(s)

        res = ""
        for word in phones_tier:
            start_time, end_time, text = word.start_time, word.end_time, word.text
            for word_start, word_end, pinyin, hanzi in s:
                if start_time >= word_start and end_time <= word_end:
                    res += text

            #text == "spn" or 
            if text == "sp" or text == "spn":
                count_spn += 1#.append(filename)
                #print(filename, word)
            else:
                ok += 1
            c = text
            for k, v in MAPPER:
                c = c.replace(k, v)
            chars.add(c)
            
            #break
        print(res)
        """
    #print(Counter(count_spn).most_common(5))
    print(count_spn / (count_spn + ok))
    print(count_spn, ok)
    print(chars, len(chars))

if __name__ == '__main__':
    main()