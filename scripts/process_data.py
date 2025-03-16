import torch
import torchaudio.transforms as T
import torchaudio

def load_audio(file_path: str, sample_rate: int) -> torch.Tensor:
    """
    Get file audio in file_path and downrate to sample_rate
    """
    waveform, orig_sr = torchaudio.load(file_path)
    if orig_sr != sample_rate:
        waveform = T.Resample(orig_freq=orig_sr, new_freq=sample_rate)(waveform)
    return waveform.squeeze(0)

def apply_overlap(wave1: torch.Tensor, wave2: torch.Tensor, overlap_ratio: float):
    """
    Overlap wave2 into waves1 with overlap_ratio.
    - If overlap_ratio = 0, wave2 will be appended to wave1.
    - If overlap_ratio = 1, wave2 will be fully overlapped with wave1.
    """

    start_pos = int(wave1.shape[0] * (1 - overlap_ratio))
    combined_length = max(start_pos + wave2.shape[0], wave1.shape[0])

    wave1 = torch.cat([wave1, torch.zeros(combined_length - len(wave1))])
    wave2 = torch.cat([torch.zeros(start_pos), wave2, torch.zeros(combined_length - (start_pos + len(wave2)))])
    mixed_wave = wave1 + wave2
    return mixed_wave, start_pos

def adjust_snr(wave1: torch.Tensor, wave2: torch.Tensor, snr_db: float):
    """Adjust SNR of wave2 to match SNR_db."""
    power_wave1 = torch.mean(wave1**2)
    power_wave2 = torch.mean(wave2**2)

    snr_linear = 10 ** (snr_db / 10)
    scale_factor = torch.sqrt(power_wave1 / (power_wave2 * snr_linear))

    wave2 = wave2 * scale_factor
    return wave2