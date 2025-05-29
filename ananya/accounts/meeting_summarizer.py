# utils.py
import os, wave, json
from pydub import AudioSegment, silence
from vosk import Model, KaldiRecognizer
import google.generativeai as genai

genai.configure(api_key="AIzaSyA6nui_hYu0gEoc9RWheIcKffXqaRdVlEs")
model = genai.GenerativeModel("models/gemini-1.5-flash")

def extract_audio(input_path, output_path="extracted_audio.wav"):
    import ffmpeg
    ffmpeg.input(input_path).output(output_path, ar=16000, ac=1).run(overwrite_output=True)
    return output_path

def remove_silence(audio_path, cleaned_path="cleaned_audio.wav"):
    audio = AudioSegment.from_wav(audio_path)
    chunks = silence.split_on_silence(audio, min_silence_len=500, silence_thresh=audio.dBFS - 14, keep_silence=250)
    cleaned_audio = AudioSegment.empty()
    for chunk in chunks:
        cleaned_audio += chunk
    cleaned_audio.export(cleaned_path, format="wav")
    return cleaned_path

def transcribe_audio(audio_path):
    try:
        model_path = os.path.join(os.path.dirname(__file__), "vosk-model-small-en-us-0.15")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Vosk model not found at: {model_path}")
        
        model = Model(model_path)
        wf = wave.open(audio_path, "rb")
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)

        transcript = ""
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                transcript += result.get("text", "") + " "
        final_result = json.loads(rec.FinalResult())
        transcript += final_result.get("text", "")
        return transcript.strip()
    except Exception as e:
        print(f"Transcription failed: {str(e)}")
        return ""

def summarize_text(transcript):
    chunks = [transcript[i:i + 3000] for i in range(0, len(transcript), 3000)]
    summaries = []
    for chunk in chunks:
        prompt = f"Summarize this meeting transcript into bullet points:\n{chunk}"
        response = model.generate_content(prompt)
        summaries.append(response.text.strip())
        

    final_prompt = "Combine these points into a concise summary:\n" + "\n".join(summaries)
    final_response = model.generate_content(final_prompt)
    return final_response.text.strip()
