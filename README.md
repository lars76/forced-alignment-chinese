# Forced Alignment for AISHELL-3

This repository shows how the AISHELL-3 dataset can be aligned using *Montreal Forced Aligner* 3.1.

![Alt text](praat.jpg?raw=true)

## What is Forced Alignment?

Forced Alignment takes as input an audio file and a transcript of what has been said in the audio file. The start and end time of a sentence, word, phoneme or paragraph is then determined. For example, in the case of an audio book and the corresponding text, forced alignment could align the sentence with the audio.

## Montreal Forced Aligner

[Montreal Forced Aligner](https://montreal-forced-aligner.readthedocs.io/en/latest/) (MFA) is a popular library for creating such alignments. MFA was notably used in [FastSpeech-2](https://arxiv.org/pdf/2006.04558).

The library takes as input the text (English text, pinyin transcription, Chinese characters, ...) and the audio. The inputs are ".lab" files containing the text and ".wav" audio files. The outputs are ".TextGrid" files containing the start and end time of each word and phoneme.

Currently, there is only an acoustic model for the alignment of Chinese characters and no pinyin model. However, a pinyin model would be much better. AISHELL-3 provides more accurate information with pinyin, which we could use.

## Generated TextGrid files

Instead of following the instruction below, you can also download the files from the releases.

## Instruction

### Download dataset

1. Download data_aishell3.tgz from https://www.openslr.org/93/
2. Extract the archive to the chosen path: tar xzf data_aishell3.tgz -C PATH

Change the PATH variable to your output path (e.g. /home/SSD).

### Perform alignment

1. python preprocess.py (change PATH in the script)
2. conda create -n aligner -c conda-forge montreal-forced-aligner
3. conda activate aligner
4. mfa model download acoustic mandarin_mfa
5. mfa model download dictionary mandarin_china_mfa
6. mfa align PATH mandarin_china_mfa mandarin_mfa PATH
7. python postprocess.py