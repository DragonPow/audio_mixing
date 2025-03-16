import os
import json
import wave
import argparse
import pandas as pd

def get_vivo_dataset_annotation(audio_dir: str, annotation_file_name: str):
    annotations = []
    # Get all speakers directory
    speakers = os.listdir(audio_dir)

    # Mapping all script to dictionary[file_name] = prompt
    with open(annotation_file_name, 'r', encoding='utf-8') as f:
        scripts = f.readlines()

    # Annotation file format: file_name prompt
    # Example: 0001 Xin chào các bạn
    # Need to split file_name and prompt by space add .wav extension to file_name
    script_dict = {}
    for script in scripts:
        file_name = script[:script.index(" ")].strip()
        prompt = script[len(file_name) + 1:].strip()
        script_dict[file_name+".wav"] = prompt

    # Loop through all speakers directory
    for i, speaker in enumerate(speakers):
        speaker_dir = os.path.join(audio_dir, speaker)
        if not os.path.isdir(speaker_dir):
            print("Skip non-directory file: ", speaker)
            continue

        # Loop through all audio files in speaker directory
        for file_name in os.listdir(speaker_dir):
            if not file_name.endswith('.wav'):
                print("Skip non-wav file: ", file_name)
                continue

            # Get audio file metadata
            with wave.open(os.path.join(speaker_dir, file_name), 'r') as wav_file:
                frames = wav_file.getnframes()
                rate = wav_file.getframerate()
                duration = frames / float(rate)
                annotations.append({
                    'speaker': speaker,
                    'file_path': os.path.join(speaker, file_name),
                    'file_name': file_name,
                    'duration': duration,
                    'rate': rate,
                    'script': script_dict.get(file_name, '')
                })

        print(f"Processing: {i+1}/{len(speakers)} - {speaker}")
    
    return annotations

def generate_annotation(dataset_type:str, audio_dir: str, annotation_file_name: str, output_file_name: str):
    if dataset_type == 'vivos':
        annotations = get_vivo_dataset_annotation(audio_dir, annotation_file_name)
    else:
        raise ValueError("Dataset type not supported: ", dataset_type)

    print("Annotation generated: ", len(annotations))

    # Save annotation to output file
    if output_file_name.endswith('.json'):
        with open(output_file_name, 'w', encoding='utf-8') as f:
            json.dump(annotations, f, ensure_ascii=False, indent=4)
    elif output_file_name.endswith('.csv'):
        # dumpt to csv file using | separator
        df = pd.DataFrame(annotations)
        df.to_csv(output_file_name, index=False, sep='|', encoding='utf-8')
    else:
        raise ValueError("Output file format not supported: ", output_file_name)
    
    print("Annotation file saved as ", output_file_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset_type", type=str, choices=['vivos'], default='vivos')
    parser.add_argument("--dataset_dir", type=str, default='./data/vivos/train/waves')
    parser.add_argument("--annotation_file_name", type=str, default='./data/vivos/train/prompts.txt')
    parser.add_argument("--output_file_name", type=str, default='./data/processed/metadata.csv')
    args = parser.parse_args()

    generate_annotation(
        args.dataset_type,
        args.dataset_dir, 
        args.annotation_file_name, 
        args.output_file_name
    )