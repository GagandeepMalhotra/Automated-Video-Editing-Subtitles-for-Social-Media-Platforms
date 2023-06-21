import tkinter as tk
from tkinter import filedialog
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import time
# Import the Speech-to-Text client library
from google.cloud import speech
import datetime
import srt
import os

# Instantiates a client
client = speech.SpeechClient.from_service_account_file('key.json')


def transcribe_speech(audio_file):
    audio = speech.RecognitionAudio(content=audio_file)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code="en-US",
        model="phone_call",
        audio_channel_count=2,
        use_enhanced=True,
        enable_word_time_offsets=True,
        profanity_filter=True
    )

    # Detects speech in the audio file
    operation = client.long_running_recognize(config=config, audio=audio)

    print("Converting audio to text. Waiting for operation to complete...")
    response = operation.result(timeout=90)

    return response


def subtitle_generation(response, bin_size=1):
    """bin_size = interval of text grouping"""
    transcriptions = []
    index = 0

    for result in response.results:
        try:
            if result.alternatives[0].words[0].start_time.seconds:
                # bin start -> for first word of result
                start_sec = result.alternatives[0].words[0].start_time.seconds
                start_microsec = result.alternatives[0].words[0].start_time.microseconds
            else:
                # bin start -> For First word of response
                start_sec = 0
                start_microsec = 0
            end_sec = start_sec + bin_size  # bin end sec

            # for last word of result
            last_word_end_sec = result.alternatives[0].words[-1].end_time.seconds
            last_word_end_microsec = result.alternatives[0].words[-1].end_time.microseconds

            # bin transcript
            transcript = result.alternatives[0].words[0].word

            index += 1  # subtitle index

            for i in range(len(result.alternatives[0].words) - 1):
                try:
                    word = result.alternatives[0].words[i + 1].word
                    word_start_sec = result.alternatives[0].words[i + 1].start_time.seconds
                    word_start_microsec = result.alternatives[0].words[
                        i + 1].start_time.microseconds  # 0.001 to convert nana -> micro
                    word_end_sec = result.alternatives[0].words[i + 1].end_time.seconds
                    word_end_microsec = result.alternatives[0].words[i + 1].end_time.microseconds

                    if word_end_sec < end_sec:
                        transcript = transcript + " " + word
                    else:
                        previous_word_end_sec = result.alternatives[0].words[i].end_time.seconds
                        previous_word_end_microsec = result.alternatives[0].words[i].end_time.microseconds

                        # append bin transcript
                        transcriptions.append(srt.Subtitle(index, datetime.timedelta(0, start_sec, start_microsec),
                                                           datetime.timedelta(0, previous_word_end_sec,
                                                                              previous_word_end_microsec), transcript))

                        # reset bin parameters
                        start_sec = word_start_sec
                        start_microsec = word_start_microsec
                        end_sec = start_sec + bin_size
                        transcript = result.alternatives[0].words[i + 1].word

                        index += 1
                except IndexError:
                    pass
            # append transcript of last transcript in bin
            transcriptions.append(srt.Subtitle(index, datetime.timedelta(0, start_sec, start_microsec),
                                               datetime.timedelta(0, last_word_end_sec, last_word_end_microsec),
                                               transcript))
            index += 1
        except IndexError:
            pass

    # turn transcription list into subtitles
    subtitles = srt.compose(transcriptions)

    return subtitles


def upload_file():
    # start_time = time.time()
    clear_text()
    # print(TextClip.list('font'))

    file_path = filedialog.askopenfilename(filetypes=(("MP4 files", "*.mp4"), ("All files", "*.*")),
                                           defaultextension=".mp4")
    if not file_path.endswith(".mp4"):
        error_text.config(text="ERROR: Not an MP4 file")
        return

    video = VideoFileClip(file_path)
    video_length = video.duration

    if video_length <= 60:
        status_text.config(text="File Chosen: " + file_path)

        # Specify the region to keep
        audio = video.audio
        filename = get_input(file_name_entry)

        if not os.path.exists(filename + " files"):
            os.makedirs(filename + " files")
            os.chdir(filename + " files")

        audio.write_audiofile(filename + ".wav")

        with open(filename + ".wav", 'rb') as f:
            audio_data = f.read()

        if len(audio_data) < 10485760:

            response = transcribe_speech(audio_data)
            subtitles = subtitle_generation(response)

            with open(filename + ".srt", "w") as f:
                f.write(subtitles)

            final_video = attempt(video, filename)

            save_video(final_video)
            os.getcwd()
            os.path.normpath(os.getcwd() + os.sep + os.pardir)

        else:
            error_text.config(text="ERROR: Audio File is too large " + str(
                len(audio_data)) + " bytes is greater than 10485760 bytes. Please select a smaller file." + file_path)
    else:
        error_text.config(text="ERROR: File is too long. Please select a file under 60 seconds" + file_path)

    # end_time = time.time()
    # print("Time taken:", end_time - start_time, "seconds")


def attempt(video, filename):
    generator = lambda txt: TextClip(txt, font='Impact', fontsize=50, color='yellow', stroke_color='black',
                                     stroke_width=2, size=video.size, method='caption')

    subtitles_clip = SubtitlesClip(filename + ".srt", generator)

    final_video = CompositeVideoClip([video, subtitles_clip.set_pos(('center', 'center'))])

    return final_video


def get_input(entry_box):
    user_input = entry_box.get()
    if user_input == "":
        error_text.config(text="ERROR: No file name entered")
        return
    return user_input


def save_video(video):
    new_file_name = get_input(file_name_entry)
    if new_file_name:
        video.write_videofile(new_file_name + ".mp4", preset="ultrafast", threads=4)
        success_text.config(text="File saved as '" + new_file_name + "'")
    return


def clear_text():
    status_text.config(text="")
    success_text.config(text="")
    error_text.config(text="")


root = tk.Tk()
root.geometry("800x600")
root.title("Youtube Shorts Creator")

frame = tk.Frame(root)
frame.pack(side="top", fill="both", expand=True)

# Load and resize the YouTube icon image to 100x100 pixels
youtube_icon = tk.PhotoImage(file="youtube_icon.png")
youtube_icon_resized = youtube_icon.subsample(7)  # Adjust the subsample factor to resize the image
youtube_label = tk.Label(frame, image=youtube_icon_resized)
youtube_label.pack(pady=0)

bottom_frame = tk.Frame(root)
bottom_frame.pack(side="top", fill="both", expand=True)

instruct_message = tk.Label(bottom_frame, text="Enter New Filename:")
instruct_message.pack()

file_name_entry = tk.Entry(bottom_frame, width=40)
file_name_entry.pack(pady=10, ipady=5)

button = tk.Button(
    bottom_frame,
    text="Upload File",
    command=upload_file,
    bg="#111111",
    fg="white",
    relief="flat",
    padx=10,
    pady=5
)
button.pack(pady=10)

error_text = tk.Label(bottom_frame, text="", fg="darkred")
error_text.pack(pady=10)

status_text = tk.Label(bottom_frame, text="")
status_text.pack(pady=10)

success_text = tk.Label(bottom_frame, text="", fg="darkgreen")
success_text.pack(pady=10)

root.update_idletasks()

# Calculate the centered position
x = (root.winfo_screenwidth() - root.winfo_reqwidth()) // 2
y = (root.winfo_screenheight() - root.winfo_reqheight()) // 2

# Set the window position
root.geometry("+%d+%d" % (x, y))

root.mainloop()