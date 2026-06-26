import numpy as np
import io

import streamlit as st


@st.cache_resource(show_spinner=False)
def load_voice_encoder():
    """
    Load the Resemblyzer VoiceEncoder. Returns None if the model is
    unavailable (e.g. torch/resemblyzer not installed or model download failed).
    The caller must check for None before using the encoder.
    """
    try:
        from resemblyzer import VoiceEncoder
        return VoiceEncoder()
    except Exception as exc:
        st.warning(
            f"⚠️ Voice recognition model unavailable: {exc}\n\n"
            "Voice attendance will not work until the model is available."
        )
        return None


def get_voice_embedding(audio_bytes):
    try:
        import librosa
        from resemblyzer import preprocess_wav

        encoder = load_voice_encoder()
        if encoder is None:
            return None

        audio_data, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        wav = preprocess_wav(audio_data, sr)

        embedding = encoder.embed_utterance(wav)
        return embedding.tolist()
    except Exception as e:
        st.error(f"Error processing audio: {e}")
        return None


# Identify the enrolled voice with the highest similarity score.
def identify_speaker(new_embedding, candidates_dict, threshold=0.65):
    if new_embedding is None or not candidates_dict:
        return None, 0.0

    best_sid = None
    best_score = -1.0

    for sid, stored_embedding in candidates_dict.items():
        if stored_embedding:
            similarity = np.dot(new_embedding, stored_embedding)
            if similarity > best_score:
                best_score = similarity
                best_sid = sid

    if best_sid is None or best_score < threshold:
        return None, 0.0

    return best_sid, best_score


def process_bulk_audio(audio_bytes, candidates_dict, threshold=0.65):
    try:
        import librosa
        from resemblyzer import preprocess_wav

        encoder = load_voice_encoder()
        if encoder is None:
            st.error("Voice encoder is not available. Cannot process audio.")
            return {}

        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        segments = librosa.effects.split(audio, top_db=30)

        identified_result = {}

        for start, end in segments:
            if (end - start) < sr * 0.5:
                continue
            segment_audio = audio[start:end]
            wav = preprocess_wav(segment_audio, sr)
            embedding = encoder.embed_utterance(wav)

            sid, score = identify_speaker(embedding, candidates_dict, threshold)

            if sid:
                if sid not in identified_result or score > identified_result[sid]:
                    identified_result[sid] = score

        return identified_result
    except Exception as e:
        st.error(f"Bulk audio processing error: {e}")
        return {}
