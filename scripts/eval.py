import os
import json
import numpy as np
import torchaudio
import torch
import matplotlib.pyplot as plt
from pypesq import pesq

def compute_si_snr(target, estimate):
    target_energy = torch.sum(target**2)
    projection = (torch.sum(target * estimate) / target_energy) * target
    noise = estimate - projection
    return 10 * torch.log10(torch.sum(projection**2) / torch.sum(noise**2))

def compute_sdr(target, estimate):
    noise = estimate - target
    return 10 * torch.log10(torch.sum(target**2) / torch.sum(noise**2))

def compute_pesq(target, estimate, sample_rate=16000):
    target_np = target.numpy()  # Chuyển tensor thành numpy array
    estimate_np = estimate.numpy()
    return pesq(sample_rate, target_np, estimate_np, 'wb')  # Wideband PESQ

def plot_waveform(original, mixed, sample_rate=16000):
    plt.figure(figsize=(12, 4))
    
    plt.subplot(2, 1, 1)
    plt.plot(np.arange(len(original)) / sample_rate, original.numpy(), label="Original")
    plt.title("Waveform - Original")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.legend()
    
    plt.subplot(2, 1, 2)
    plt.plot(np.arange(len(mixed)) / sample_rate, mixed.numpy(), label="Mixed", color='r')
    plt.title("Waveform - Mixed")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.legend()
    
    plt.tight_layout()
    plt.show()

def evaluate_dataset(metadata_path, num_samples=5):
    """Evaluate data with metrics SI-SNR, SDR and PESQ."""
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    results = []
    for entry in metadata[:num_samples]:  # Chỉ đánh giá một số mẫu
        wave_mix, _ = torchaudio.load(entry["mixture"])
        wave_src, _ = torchaudio.load(entry["source1"])  # Dùng source1 để đánh giá

        si_snr = compute_si_snr(wave_src.squeeze(), wave_mix.squeeze())
        sdr = compute_sdr(wave_src.squeeze(), wave_mix.squeeze())
        pesq_score = compute_pesq(wave_src.squeeze(), wave_mix.squeeze())

        results.append({
            "file": entry["mixture"],
            "SI-SNR (dB)": round(si_snr.item(), 2),
            "SDR (dB)": round(sdr.item(), 2),
            "PESQ": round(pesq_score, 2)
        })

        print(f"{entry['mixture']} - SI-SNR: {si_snr:.2f} dB | SDR: {sdr:.2f} dB | PESQ: {pesq_score:.2f}")

    return results

if __name__ == "__main__":
    metadata_path = "output/mixture_metadata.json"
    results = evaluate_dataset(metadata_path)

    output_file = "output/evaluation_results.json"
    # Dump results to file csv
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
    
    print("\n✅ Finishned, the output drop in file `{output_file}`")
