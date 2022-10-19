from argparse import ArgumentParser
import json
from synthesize import preprocess_vietnamese, synthesize_api
import yaml
import os
from utils.model import get_model, get_vocoder
import torch
import numpy as np
import glob


device = "cpu" # change device here and model/modules as well


text = "Thay lời muốn nói"
restore_step = 11000
emotion = 0 # {"neutral": 0, "sad": 1, "angry": 2, "happy": 3}
path_to_config = "config/VLSP-subtask1"
pitch_control, energy_control, duration_control = 1, 1, 1
output_path = "api-output/"    





control_values = pitch_control, energy_control, duration_control
os.makedirs(output_path,exist_ok=True)

# remove old files
for file in glob.glob(output_path + "*.wav"):
    os.remove(file)

# Read Config
preprocess_config = yaml.load(
    open(os.path.join(path_to_config,"preprocess.yaml"), "r"), Loader=yaml.FullLoader
)
model_config = yaml.load(open(os.path.join(path_to_config,"model.yaml"), "r"), Loader=yaml.FullLoader)
train_config = yaml.load(open(os.path.join(path_to_config,"train.yaml"), "r"), Loader=yaml.FullLoader)
configs = (preprocess_config, model_config, train_config)

parser = ArgumentParser()
parser.add_argument("--restore_step", type=int, required=True)
args = parser.parse_args(["--restore_step", str(restore_step)])
model = get_model(args, configs, device, train=False)
vocoder = get_vocoder(model_config, device)

ids = raw_texts = [text]
speakers = np.array([0]) # random values should also work
emotion_map = json.load(open(os.path.join(preprocess_config["path"]["preprocessed_path"],"emotions.json")))

for k,v in emotion_map.items():
    emotions = np.array([v])
    if preprocess_config["preprocessing"]["text"]["language"] == "vi":
        texts = np.array([preprocess_vietnamese(text, preprocess_config)])
    text_lens = np.array([len(texts[0])])
    batchs = [(ids, raw_texts, speakers,emotions, texts, text_lens, max(text_lens))]
    synthesize_api(device,model, configs, vocoder, batchs, control_values,os.path.join(output_path,k+".wav"))