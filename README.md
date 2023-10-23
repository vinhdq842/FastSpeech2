# VLSP 2022 TTS: Emotional speech synthesis - training guide for sub-task 1
### Dependencies

You need to first install [Montreal Forced Aligner](https://montreal-forced-aligner.readthedocs.io/en/latest/installation.html), then install the Python dependencies with
```
pip install -r requirements.txt
```

### Preprocessing
Before you go on, make sure the `corpus_path` in `config/VLSP-subtask1/preprocess.yaml` points to your corresponding local path to the training data.

First, run 
```
python prepare_align.py config/VLSP-subtask1/preprocess.yaml
```
for some preparations.
After that, use MFA to validate and obtain the alignments between the utterances and the phoneme sequences.
```
mfa validate raw_data/VLSP-subtask1/ lexicon/vietnamese-hcm-lexicon.txt vietnamese_mfa
mfa align raw_data/VLSP-subtask1/ lexicon/vietnamese-hcm-lexicon.txt vietnamese_mfa preprocessed_data/VLSP-subtask1
```
(assumed that you have downloaded `vietnamese_mfa` acoustic model using `mfa model download acoustic vietnamese_mfa`).

Finally, run the preprocessing script
```
python preprocess.py config/VLSP-subtask1/preprocess.yaml
```
to further extract acoustic features served for training.

### Start training
Train the model with
```
python train.py -p config/VLSP-subtask1/preprocess.yaml -m config/VLSP-subtask1/model.yaml -t config/VLSP-subtask1/train.yaml
```

### Inference
Run
```
python synthesize.py --mode single -p config/VLSP-subtask1/preprocess.yaml -m config/VLSP-subtask1/model.yaml -t config/VLSP-subtask1/train.yaml --text "cuộc sống này quá bon chen" --restore_step 40000 --emotion_id 1
```
and generated utterances will be put in `.output/result/VLSP-subtask1`.