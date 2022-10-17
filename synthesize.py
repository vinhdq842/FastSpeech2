import os
import re
import argparse
from string import punctuation
import time

import torch
import yaml
import numpy as np
from torch.utils.data import DataLoader

from utils.model import get_model, get_vocoder, vocoder_infer
from utils.tools import to_device, synth_samples
from dataset import TextDataset
from text import text_to_sequence
from unidecode import unidecode
from scipy.io import wavfile

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def read_lexicon(lex_path):
    lexicon = {}
    with open(lex_path) as f:
        for line in f:
            temp = re.split(r"\s+", line.strip("\n"))
            word = temp[0]
            phones = temp[1:]
            if word.lower() not in lexicon:
                lexicon[word.lower()] = phones
    return lexicon


def preprocess_vietnamese(text, preprocess_config):
    text = text.rstrip(punctuation)
    lexicon = read_lexicon(preprocess_config["path"]["lexicon_path"])

    phones = []
    words = list(filter(lambda x : len(x.strip()) > 0,re.split(r"([,;.\-\?\!\s+])", text)))
    comb = ["ch","gh","gi","kh","ng","ngh","nh","th","tr","qu"]

    for w in words:
        w = w.lower()
        if w in lexicon:
            phones += lexicon[w]
        else:
            can:bool = True

            for c in w:
                can = can and c in lexicon
            
            if not can:
                continue
            
            if unidecode(w[0]) in ["u","e","o","a","i"]:
                phones += lexicon[w[0]]
                w = w[len(w[0]):]
            else:
                while len(w) > 0:
                    for cb in comb:
                        if w.startswith(cb):
                            phones += lexicon[cb][0]
                            w = w[len(cb):]
                            break
                    else:
                        if unidecode(w[0]) in ["u","e","o","a","i"]:
                            phones += lexicon[w[0]][1:]
                        else:
                            phones += lexicon[w[0]][0]
                        w = w[len(w[0]):]


    phones = "{" + "}{".join(phones) + "}"
    phones = re.sub(r"\{[^\w\s]?\}", "{sp}", phones)
    phones = phones.replace("}{", " ")

    print("Raw Text Sequence: {}".format(text))
    print("Phoneme Sequence: {}".format(phones))
    sequence = np.array(
        text_to_sequence(
            phones, preprocess_config["preprocessing"]["text"]["text_cleaners"]
        )
    )

    return np.array(sequence)

def synthesize2(model,configs,vocoder,batchs,control_values,path):
    preprocess_config, model_config, train_config = configs
    pitch_control, energy_control, duration_control = control_values
    results = []

    for batch in batchs:
        batch = to_device(batch, device)
        with torch.no_grad():
            # Forward
            output = model(
                *(batch[2:]),
                p_control=pitch_control,
                e_control=energy_control,
                d_control=duration_control
            )
            
        mel_predictions = output[1].transpose(1, 2)
        lengths = output[9] * preprocess_config["preprocessing"]["stft"]["hop_length"]
        wav_predictions = vocoder_infer(
            mel_predictions, vocoder, model_config, preprocess_config, lengths=lengths
        )

        sampling_rate = preprocess_config["preprocessing"]["audio"]["sampling_rate"]

        for wav in wav_predictions:
            name = os.path.join(path,str(time.time()*1000).split('.')[0] + ".wav")
            results.append(name)
            wavfile.write(name, sampling_rate, wav)

    return results

def synthesize(model, step, configs, vocoder, batchs, control_values):
    preprocess_config, model_config, train_config = configs
    pitch_control, energy_control, duration_control = control_values

    for batch in batchs:
        batch = to_device(batch, device)
        with torch.no_grad():
            # Forward
            output = model(
                *(batch[2:]),
                p_control=pitch_control,
                e_control=energy_control,
                d_control=duration_control
            )
            synth_samples(
                batch,
                output,
                vocoder,
                model_config,
                preprocess_config,
                train_config["path"]["result_path"],
            )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--restore_step", type=int, required=True)
    parser.add_argument(
        "--mode",
        type=str,
        choices=["batch", "single"],
        required=True,
        help="Synthesize a whole dataset or a single sentence",
    )
    parser.add_argument(
        "--source",
        type=str,
        default=None,
        help="path to a source file with format like train.txt and val.txt, for batch mode only",
    )
    parser.add_argument(
        "--text",
        type=str,
        default=None,
        help="raw text to synthesize, for single-sentence mode only",
    )
    parser.add_argument(
        "--speaker_id",
        type=int,
        default=0,
        help="speaker ID for multi-speaker synthesis, for single-sentence mode only",
    )
    parser.add_argument(
        "--emotion_id",
        type=int,
        default=0,
        help="emotion ID for multi-emotion synthesis, for single-sentence mode only",
    )
    parser.add_argument(
        "-p",
        "--preprocess_config",
        type=str,
        required=True,
        help="path to preprocess.yaml",
    )
    parser.add_argument(
        "-m", "--model_config", type=str, required=True, help="path to model.yaml"
    )
    parser.add_argument(
        "-t", "--train_config", type=str, required=True, help="path to train.yaml"
    )
    parser.add_argument(
        "--pitch_control",
        type=float,
        default=1.0,
        help="control the pitch of the whole utterance, larger value for higher pitch",
    )
    parser.add_argument(
        "--energy_control",
        type=float,
        default=1.0,
        help="control the energy of the whole utterance, larger value for larger volume",
    )
    parser.add_argument(
        "--duration_control",
        type=float,
        default=1.0,
        help="control the speed of the whole utterance, larger value for slower speaking rate",
    )
    args = parser.parse_args()

    # Check source texts
    if args.mode == "batch":
        assert args.source is not None and args.text is None
    if args.mode == "single":
        assert args.source is None and args.text is not None

    # Read Config
    preprocess_config = yaml.load(
        open(args.preprocess_config, "r"), Loader=yaml.FullLoader
    )
    model_config = yaml.load(open(args.model_config, "r"), Loader=yaml.FullLoader)
    train_config = yaml.load(open(args.train_config, "r"), Loader=yaml.FullLoader)
    configs = (preprocess_config, model_config, train_config)

    # Get model
    model = get_model(args, configs, device, train=False)

    # Load vocoder
    vocoder = get_vocoder(model_config, device)

    # Preprocess texts
    if args.mode == "batch":
        # Get dataset
        dataset = TextDataset(args.source, preprocess_config)
        batchs = DataLoader(
            dataset,
            batch_size=8,
            collate_fn=dataset.collate_fn,
        )
    if args.mode == "single":
        ids = raw_texts = [args.text]
        speakers = np.array([args.speaker_id])
        emotions = np.array([args.emotion_id])
        if preprocess_config["preprocessing"]["text"]["language"] == "vi":
            texts = np.array([preprocess_vietnamese(args.text, preprocess_config)])
        text_lens = np.array([len(texts[0])])
        batchs = [(ids, raw_texts, speakers,emotions, texts, text_lens, max(text_lens))]

    control_values = args.pitch_control, args.energy_control, args.duration_control

    synthesize(model, args.restore_step, configs, vocoder, batchs, control_values)
