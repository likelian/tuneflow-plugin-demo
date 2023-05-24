from run_separate import *
import tempfile
import os
import soundfile as sf
from scipy.io.wavfile import read, write
from io import BytesIO


audio_file_path = "/Users/likelian/Desktop/TF/tuneflow-plugin-demo/Source_Separator/audio/HoldMe2_Preview.wav"
#export_path = "/Users/likelian/Desktop/TF/tuneflow-plugin-demo/Source_Separator/audio/output_audio"


data, samplerate = sf.read(audio_file_path)

empty_bytes = bytes()
byte_io = BytesIO(empty_bytes)
write(byte_io, samplerate, data)
input_audio_bytes = byte_io.read()


fd, temp_input_path = tempfile.mkstemp(suffix = '.wav')
with os.fdopen(fd, 'wb') as tmp:
    tmp.write(input_audio_bytes)


#temp_output_path = tempfile.TemporaryDirectory()
output_dict = run_separate(temp_input_path)


#print(output_dict)

filename = "/Users/likelian/Desktop/TF/tuneflow-plugin-demo/Source_Separator/audio/output_audio/test.wav"
for key in output_dict:
    with open(filename, 'wb') as f:
        f.write(output_dict[key])

#temp_output_path.cleanup()
os.remove(temp_input_path)











