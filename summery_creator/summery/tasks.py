import os
from mimetypes import guess_type

import magic
import requests
from celery import shared_task
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.io.VideoFileClip import VideoFileClip
from requests_toolbelt import MultipartEncoder

from summery_creator.summery.models import GlossaryEntry, Lesson
from summery_creator.summery.services import (
    extract_file_text,
    extract_term_and_definition,
    send_message,
)

ML_HOST = "http://192.168.62.95:8000/"
LOCAL = False
mime = magic.Magic(mime=True)


@shared_task
def send_file_to_ml(lesson_id):
    lesson = Lesson.objects.get(id=lesson_id)
    send_file = True if lesson.file else False
    text = None
    new_file_path = None

    try:
        if send_file:
            file_path = lesson.file.path
            mime_type, encoding = guess_type(file_path)
            top_level_type = mime_type.split("/")[0] if mime_type else None
            output_path = file_path.rsplit(".", 1)[0]

            if top_level_type == "audio":
                if mime_type != "audio/mpeg":
                    # Extract MP3 from any audio file
                    audio = AudioFileClip(file_path)
                    new_file_path = f"{output_path}.mp3"
                    audio.write_audiofile(new_file_path)
                else:
                    new_file_path = None
            elif top_level_type == "video":
                # Extract MP4 from any video file
                video = VideoFileClip(file_path)
                new_file_path = f"{output_path}.mp3"
                video.audio.write_audiofile(new_file_path)
            else:
                text = extract_file_text(lesson.file.path)
    except Exception as e:
        print(e)
        return lesson_id  # Return the ID in case of failure

    if send_file:
        if not LOCAL:
            if text:
                r = requests.post(
                    ML_HOST + "summary",
                    json={"query": text, "uuid": str(lesson_id)},
                    headers={"Content-Type": "application/json"},
                )
                print(r.status_code)
                send_message(lesson_id, text)
            elif new_file_path:
                mp_encoder = MultipartEncoder(
                    fields={
                        "uuid": str(lesson_id),
                        "file": (
                            lesson.file.path.split("/")[-1],
                            open(
                                new_file_path if new_file_path else lesson.file.path,
                                "rb",
                            ),
                            "audio/mpeg",
                        ),
                    }
                )
                r = requests.post(
                    ML_HOST + "upload_audio",
                    data=mp_encoder,
                    headers={"Content-Type": mp_encoder.content_type},
                )
                print(r.status_code)
        else:
            # TODO: add local file send
            ...
    else:
        r = requests.post(
            ML_HOST + "summary",
            json={"query": lesson.audio_text, "uuid": str(lesson_id)},
            headers={"Content-Type": "application/json"},
        )
        print(r.status_code)
    if new_file_path and os.path.exists(new_file_path):
        os.remove(new_file_path)
    return lesson_id


lessons = {}


@shared_task
def handle_ml_callback(type: str, data, uuid: str):
    global lessons
    if uuid not in lessons:
        lessons[uuid] = Lesson.objects.get(id=uuid)
    lesson = lessons[uuid]
    if type == "trans":
        if lesson.audio_text is None:
            lesson.audio_text = ""
        lesson.audio_text += data
        lesson.save(update_fields=["audio_text"])
    elif type == "terms":
        term, definition = extract_term_and_definition(data)
        GlossaryEntry.objects.create(
            lesson=lesson, sentence=term, description=definition
        )
