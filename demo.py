from argparse import ArgumentParser
import json
import streamlit as st
from synthesize import preprocess_vietnamese, synthesize2
import yaml
import os
from utils.model import get_model, get_vocoder
import torch
import numpy as np
import glob

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


st.header("Demo emotional TTS")
text = st.text_input("Enter your text here")
restore_step = 11000#st.slider("Select checkpoint",1000,40000,step=1000)

if st.button("Submit"):
    path_to_config = "config/VLSP-subtask1"
    pitch_control, energy_control, duration_control = 1, 1, 1
    control_values = pitch_control, energy_control, duration_control


    output_path = "demo-output/"    
    os.makedirs(output_path,exist_ok=True)

    for file in glob.glob(output_path + "*.wav"):
        os.remove(file)
    # Read Config
    preprocess_config = yaml.load(
        open(os.path.join(path_to_config,"preprocess.yaml"), "r"), Loader=yaml.FullLoader
    )
    model_config = yaml.load(open(os.path.join(path_to_config,"model.yaml"), "r"), Loader=yaml.FullLoader)
    train_config = yaml.load(open(os.path.join(path_to_config,"train.yaml"), "r"), Loader=yaml.FullLoader)
    configs = (preprocess_config, model_config, train_config)

    # Get model
    parser = ArgumentParser()
    parser.add_argument("--restore_step", type=int, required=True)
    args = parser.parse_args(["--restore_step", str(restore_step)])

    model = get_model(args, configs, device, train=False)

    # Load vocoder
    vocoder = get_vocoder(model_config, device)

    ids = raw_texts = [text]
    speakers = np.array([0])
    
    emotion_map = json.load(open(os.path.join(preprocess_config["path"]["preprocessed_path"],"emotions.json")))

    for k,v in emotion_map.items():
        emotions = np.array([v])
        if preprocess_config["preprocessing"]["text"]["language"] == "vi":
            texts = np.array([preprocess_vietnamese(text, preprocess_config)])
        text_lens = np.array([len(texts[0])])
        batchs = [(ids, raw_texts, speakers,emotions, texts, text_lens, max(text_lens))]

        file_names = synthesize2(model, configs, vocoder, batchs, control_values,output_path)
        st.subheader(k + ":")
        st.audio(file_names[0])
