import string
import csv
from pydub import AudioSegment
import os
import whisper_timestamped as whisper
class Audio:
    def mute_audio(audio_file_path, output_path = "uploads/beep_audio.mp3"):
        file_name, file_extension = os.path.splitext(audio_file_path)
        
        print(audio_file_path)

        audio = whisper.load_audio(audio_file_path)

        model = whisper.load_model("small")

        result = whisper.transcribe(model, audio)

        # Check if 'result' is a dictionary
        if isinstance(result, dict):
            result = [result]

        # Assuming 'result' is a list of dictionaries
        words_data = [word for segment in result[0]['segments'] for word in segment['words']]

        # Get the keys (column names) from the first dictionary in the list
        keys = words_data[0].keys()

        # Write the data to a CSV file
        with open('Foul/utils/wordstamps.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(words_data)

        badwords = []
        with open("Foul/utils/DirtyWords.csv", 'r', encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) > 2:
                    badwords.append(row[1])

        file_path = "Foul/utils/wordstamps.csv"

        # Read the data from the CSV file
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            data = list(reader)

        audio = AudioSegment.from_file(audio_file_path, format=file_extension[1:])

        found_occurrences = []
        for item in data:
            if item['text'].translate(str.maketrans('', '', string.punctuation)).lower() in badwords:
                start = float(item['start'])
                end = float(item['end'])
                found_occurrences.append((item['text'], start, end))

        # Mute the audio during the time intervals of the foul words
        for occurrence in found_occurrences:
            print(occurrence)
            word, start, end = occurrence
            audio = audio[:int(start * 1000)] + AudioSegment.silent(duration=int((end - start) * 1000)) + audio[int(end * 1000):]

        # Export the modified audio as a new file
        audio.export(output_path, format="mp3")

        print("Audio with foul words replaced by beep has been saved.")
        return output_path


if __name__ == "__main__":
    audio_file_path = "Foul/utils/pure-blur-intro.mp3"
    output_file_path = Audio.mute_audio(audio_file_path=audio_file_path)
    print(output_file_path)