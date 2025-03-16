import json
import random
import torchaudio
import os
import time
from datetime import datetime
from pandas import read_csv, DataFrame
from process_data import load_audio, adjust_snr, apply_overlap

# Load from config.yaml
CONFIG_PATH = "./configs/config.json"

DEFAULT_NUM_MIXTURES = 1000
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_SNR_DB_RANGE = [-5, 5]
DEFAULT_OVERLAP_RATIO_RANGE = [0.3, 0.3]

def load_json(file_path: str):
    """Get metadata from JSON file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
def load_csv(file_path: str):
    """Get metadata from CSV file."""
    with open(file_path, "r", encoding="utf-8") as f:
        df = read_csv(f, sep="|", encoding="utf-8")
        return df.to_dict(orient="records")
    

def mix_audio_files(file1:str, file2:str, snr_db:float, overlap_ratio:float, target_sample_rate:int):
    """Mix 2 file audio with SNR and overlap ratio."""
    target_sample_rate = target_sample_rate if target_sample_rate else DEFAULT_SAMPLE_RATE
    wave1 = load_audio(file1, target_sample_rate)
    wave2 = load_audio(file2, target_sample_rate)

    wave2 = adjust_snr(wave1, wave2, snr_db) # Adjust SNR
    mixed_wave, start_pos = apply_overlap(wave1, wave2, overlap_ratio) # Apply overlap

    return mixed_wave, start_pos

def create_mixture_dataset(
        metadata:dict, audio_dir:str, output_dir:str,
        num_mixtures:int=DEFAULT_NUM_MIXTURES, 
        snr_db_range:list=DEFAULT_SNR_DB_RANGE, 
        overlap_ratio_range:list=DEFAULT_OVERLAP_RATIO_RANGE, 
        downsample_rate:int=None
    ):
    """Create mixture dataset from metadata."""
    # Create output directory
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(output_dir, date_str)
    os.makedirs(output_dir, exist_ok=True)

    # Create data directory
    data_dir = os.path.join(output_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    
    output_metadata = []
    total_duration = 0

    start_time = time.time()
    print(f"🚀 Start mixing {num_mixtures} audio files...")
    for i in range(num_mixtures):
        # Print progress every 10%
        if num_mixtures > 10 and i % (num_mixtures // 10) == 0:
            time_processed = time.time() - start_time
            print(f"Processing {i}/{num_mixtures}, num files: {i}/{num_mixtures}, time elapsed: {time_processed:.4f} seconds")

        # Get random 2 file from metadata
        spk1, spk2 = random.sample(metadata, 2)
        # If speaker 1 and speaker 2 are the same, skip this iteration
        if spk1["speaker"] == spk2["speaker"]:
            continue

        file1_name = spk1["file_path"].split("/")[-1]
        file2_name = spk2["file_path"].split("/")[-1]
        # print(f"Mixing {file1_name} and {file2_name}")

        # Choose random SNR and overlap ratio
        snr_db = random.uniform(*snr_db_range)
        overlap_ratio = random.uniform(*overlap_ratio_range)

        # Mix audio files and get start position of speaker 2
        file1  = os.path.join(audio_dir, spk1["file_path"])
        file2 = os.path.join(audio_dir, spk2["file_path"])
        mixture, start_pos = mix_audio_files(file1, file2, snr_db, overlap_ratio, target_sample_rate=downsample_rate)

        # Save mixture audio file
        mixture_filename = f"mixture_{i:05d}.wav"
        mixture_path = os.path.join(data_dir, mixture_filename) # mixture_path = output_dir/data/mixture_{i}.wav
        output_sample_rate = downsample_rate if downsample_rate else DEFAULT_SAMPLE_RATE
        torchaudio.save(mixture_path, mixture.unsqueeze(0), output_sample_rate)

        total_duration += mixture.shape[0] / output_sample_rate

        # Save metadata
        output_metadata.append({
            "mixture": mixture_path,
            "source1": spk1["file_path"],
            "source2": spk2["file_path"],
            "speaker1": spk1["speaker"],
            "speaker2": spk2["speaker"],
            "transcript1": spk1["script"],
            "transcript2": spk2["script"],
            "rate": output_sample_rate,
            "snr_db": snr_db,
            "overlap_ratio": overlap_ratio,
            "duration": mixture.shape[0] / output_sample_rate,
            "start_time_speaker_1": 0,
            "start_time_speaker_2": start_pos / output_sample_rate  # Convert from sample rate to seconds
        })

    print(f"✅ Created {num_mixtures} mixture audio files in {output_dir}")
    return output_dir, output_metadata, total_duration
    
if __name__ == "__main__":
    config = load_json(CONFIG_PATH)
    metadata = load_csv(config["metadata_path"])

    # Print config
    print("CONFIG", config)

    # Create mixture dataset
    output_dir, output_metadata, total_duration = create_mixture_dataset(
        metadata, 
        config["audio_dir"],
        config["output_dir"], 
        config["num_mixtures"],
        snr_db_range=config["snr_db_range"],
        overlap_ratio_range=config["overlap_ratio_range"],
        downsample_rate=config["downsample_rate"]
    )

    # Save metadata to JSON file
    metadata_path = os.path.join(output_dir, "annotation.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(output_metadata, f, indent=4, ensure_ascii=False)

    # Save metadata to CSV file
    metadata_csv_path = os.path.join(output_dir, "annotation.csv")
    with open(metadata_csv_path, "w", encoding="utf-8") as f:
        # Convert dict to DataFrame
        df = DataFrame(output_metadata)
        # Write to CSV file
        df.to_csv(f, index=False, sep="|", encoding="utf-8")

    # Save config to JSON file
    config_path = os.path.join(output_dir, "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        config["total_duration"] = total_duration # Load total duration to config
        json.dump(config, f, indent=4, ensure_ascii=False)

    print(f"✅ Saved filed annotation success")