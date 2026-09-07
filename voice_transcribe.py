"""Local speech-to-text, CPU-only, no cloud dependency -- same
faster-whisper "tiny" model bayhouse's own voice_monitor.py already
uses on similarly constrained hardware (no AVX2 there; here it's RAM,
414MB + 1GB swap, that's the limiting resource instead).

Deliberately does the transcription itself and returns plain text --
nothing about "here's an audio file, go listen to it" is ever handed
to a spawned Claude session. Per Paul's own instruction: this is
message PROCESSING, done in Python before a message ever reaches the
agent, not a tool call the agent makes itself.

Model loads once, lazily, and is kept in memory for the life of the
process (webhook / email monitor) -- reloading per call would be both
slow and needlessly hard on a box this memory-constrained.
"""
from pathlib import Path

from faster_whisper import WhisperModel

from safehouse_logging import get_logger

log = get_logger(Path(__file__).stem)

_MODEL: WhisperModel | None = None


def _get_model() -> WhisperModel:
    global _MODEL
    if _MODEL is None:
        log.info("loading faster-whisper 'tiny' model (int8, cpu) -- first call only")
        _MODEL = WhisperModel("tiny", device="cpu", compute_type="int8")
    return _MODEL


def transcribe(audio_path: str) -> str:
    """Transcribes an audio file (any format ffmpeg can decode -- mp3,
    wav, amr, m4a, etc.) to plain text. Raises on failure; callers
    decide how to degrade (bayhouse's own voice pipeline treats an
    empty/garbled result as ordinary STT variance, not an error -- same
    posture here)."""
    model = _get_model()
    segments, _info = model.transcribe(audio_path, beam_size=1)
    text = " ".join(seg.text.strip() for seg in segments).strip()
    log.info(f"transcribed {audio_path} -> {len(text)} chars")
    return text
