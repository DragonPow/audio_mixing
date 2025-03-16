import torchaudio
import torch
import torch.nn.functional as F


def compute_power(waveform):
    """Tính công suất trung bình của tín hiệu."""
    return waveform.pow(2).mean()

def adjust_gain(reference, target_snr_db, interferer):
    """
    Điều chỉnh cường độ của tín hiệu interferer sao cho SNR giữa reference và interferer đạt target_snr_db.
    
    Công thức: desired_noise_power = reference_power / (10^(SNR/10))
    Scaling factor = sqrt(desired_noise_power / interferer_power)
    """
    ref_power = compute_power(reference)
    interferer_power = compute_power(interferer)
    desired_noise_power = ref_power / (10 ** (target_snr_db / 10))
    scaling_factor = torch.sqrt(desired_noise_power / interferer_power)
    return interferer * scaling_factor

def mix_signals(signal1, signal2, offset):
    """
    Trộn hai tín hiệu với một khoảng offset cho signal2.
    
    signal1, signal2: tensor có shape [channels, samples]
    offset: số mẫu để dịch signal2 so với signal1.
    """
    len1 = signal1.shape[1]
    len2 = signal2.shape[1]
    total_length = max(len1, offset + len2)
    mixture = torch.zeros(signal1.shape[0], total_length)
    mixture[:, :len1] += signal1
    mixture[:, offset:offset+len2] += signal2
    return mixture

def preprocess_audio(waveform, target_length):
    """
    Nếu tín hiệu ngắn hơn target_length thì padding, nếu dài hơn thì cắt.
    Giả sử waveform có shape [channels, samples].
    """
    current_length = waveform.shape[1]
    if current_length < target_length:
        pad_amount = target_length - current_length
        waveform = F.pad(waveform, (0, pad_amount))
    else:
        waveform = waveform[:, :target_length]
    return waveform

def mixing_2_file(file1: str, file2: str, target_duration_sec: float, target_snr_db: float, overlap: float, output_file: str):
    
    # Load file âm thanh sử dụng torchaudio
    waveform1, sr1 = torchaudio.load(file1)  # waveform1: [channels, samples]
    waveform2, sr2 = torchaudio.load(file2)
    
    # Đảm bảo sample rate giống nhau; nếu không, resample file thứ hai về sr1
    if sr1 != sr2:
        # resampler = torchaudio.transforms.Resample(orig_freq=sr2, new_freq=sr1)
        # waveform2 = resampler(waveform2)
        # Raise error
        raise ValueError("Sample rates do not match, %d vs %d" % (sr1, sr2))
    sr = sr1  # sử dụng sample rate chung
    
    # Nếu tín hiệu có nhiều hơn 1 kênh, chuyển về mono (lấy trung bình các channel)
    if waveform1.shape[0] > 1:
        waveform1 = waveform1.mean(dim=0, keepdim=True)
    if waveform2.shape[0] > 1:
        waveform2 = waveform2.mean(dim=0, keepdim=True)
    
    # Định nghĩa độ dài đoạn mong muốn, ví dụ 4 giây
    target_length = sr * target_duration_sec
    
    waveform1 = preprocess_audio(waveform1, target_length)
    waveform2 = preprocess_audio(waveform2, target_length)
    
    # Điều chỉnh SNR: đặt mục tiêu SNR (dB) cho nguồn interferer so với reference
    waveform2_adjusted = adjust_gain(waveform1, target_snr_db, waveform2)
    
    # Trộn hai tín hiệu: định nghĩa offset (ví dụ, 50% overlap => offset = 50% độ dài đoạn)
    offset = target_length * overlap
    mixture = mix_signals(waveform1, waveform2_adjusted, offset)
    
    # (Tùy chọn) Chuẩn hóa lại tín hiệu trộn để tránh clipping
    # max_val = mixture.abs().max()
    # if max_val > 1.0:
    #     mixture = mixture / max_val
    
    # Lưu file mixture ra định dạng WAV
    torchaudio.save(output_file, mixture, sr)
    print("Mixture saved as mixture.wav")