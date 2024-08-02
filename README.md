# Forced Alignment for Chinese Speech

This repository shows how the Chinese speech datasets can be aligned using *Montreal Forced Aligner*. Annotations and models are provided for several popular datasets (AISHELL-3, biaobei).

![Alt text](praat.jpg?raw=true)

## What is Forced Alignment?

Forced Alignment takes as input an audio file and a transcript of what has been said in the audio file. The start and end time of a sentence, word, phoneme or paragraph is then determined. For example, in the case of an audio book and the corresponding text, forced alignment could align the sentence with the audio.

## Montreal Forced Aligner

[Montreal Forced Aligner](https://montreal-forced-aligner.readthedocs.io/en/latest/) (MFA) is a popular library for creating such alignments. MFA was notably used in [FastSpeech-2](https://arxiv.org/pdf/2006.04558).

The library takes as input the text (English text, pinyin transcription, Chinese characters, ...) and the audio. The inputs are ".lab" files containing the text and ".wav" audio files. The outputs are ".TextGrid" files containing the start and end time of each word and phoneme.

Currently, there is only an acoustic model for the alignment of Chinese characters and no pinyin model. However, a pinyin model would be much better. Many datasets provide more accurate information with pinyin, which we could use. Also, the MFA dictionary model does not treat Erhua and other aspects of Chinese phonology in an optimal way.

Therefore, I trained my own model, using a dictionary based on IPA.

## Generated TextGrid files and pretrained model

Instead of following the instruction below, you can also download the generated files from the [releases](https://github.com/lars76/forced-alignment-chinese/releases).

| Dataset    | Model | TextGrid |
|------------|-------|----------|
| AISHELL-3  | [url](https://github.com/lars76/forced-alignment-chinese/releases/download/model_files/aishell3_pinyin.zip) | [url](https://github.com/lars76/forced-alignment-chinese/releases/download/textgrid_files/aishell3_textgrid_files.zip)    |
| biaobei    | [url](https://github.com/lars76/forced-alignment-chinese/releases/download/model_files/biaobei_pinyin.zip) | [url](https://github.com/lars76/forced-alignment-chinese/releases/download/textgrid_files/biaobei_textgrid_files.zip)    |

## Instruction

### Download dataset(s)

- AISHELL-3: https://www.openslr.org/93/
- biaobei: https://en.data-baker.com/datasets/freeDatasets/

Extract the downloaded datasets to the following directories: `datasets/aishell3`, `datasets/biaobei`.

For custom datasets, create a directory `datasets/general` with the following structure:

```
datasets/general/
├── SPEAKER_NAME_1/
│ ├── text_1.hanzi (with Chinese text, e.g., 对不起)
│ ├── text_1.wav (corresponding audio file)
│ ...
├── SPEAKER_NAME_2/
│ ├── text_2.hanzi
│ ├── text_2.wav
│ ...
├── ...
```

### Prepare alignment

1. `conda create -n aligner -c conda-forge montreal-forced-aligner`
2. `conda activate aligner`
3. `pip install pinyin_to_ipa` and `python create_dictionary.py`

### Perform alignment

In the following change TEMP_DIR and num_jobs. Make sure that TEMP_DIR is an absolute path or the training might fail.

1. `mfa train datasets/biaobei biaobei_pinyin_dictionary.txt biaobei_pinyin_acoustic.zip --output_directory datasets/biaobei --num_jobs 1 --temporary_directory tmp_dir1 --clean --use_mp --use_threading --single_speaker`.
2. `mfa train datasets/aishell3 aishell3_pinyin_dictionary.txt aishell3_pinyin_acoustic.zip --output_directory datasets/aishell3 --num_jobs 32 --temporary_directory TEMP_DIR --clean --use_mp --use_threading`.

### Post-processing

1. `pip install tgt`
2. `python postprocess.py`