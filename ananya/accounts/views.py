from django.shortcuts import render,redirect
from django.core.files.storage import default_storage
from django.conf import settings
from .meeting_summarizer import extract_audio, remove_silence, transcribe_audio, summarize_text  # ⬅ your custom functions
import os
# Create your views here.

def index(request):
    return render(request,'accounts/index.html')
def contact(request):
    return render(request, 'accounts/contact.html')
def about(request):
    return render(request, 'accounts/about.html')





def upload_video(request):
    if request.method == "POST" and request.FILES.get("video"):
        file = request.FILES["video"]
        file_path = default_storage.save(file.name, file)

        full_path = os.path.join(settings.MEDIA_ROOT, file_path)
        audio_path = extract_audio(full_path)
        cleaned_audio = remove_silence(audio_path)
        transcript = transcribe_audio(cleaned_audio)
        summary = summarize_text(transcript)

        return render(request, "accounts/summary.html", {
            "summary": summary,
            "transcript": transcript[:3000]
        })

    return render(request, "accounts/upload.html")