"""
read more about tuneflow_py classes at
https://github.com/tuneflow/tuneflow-py/blob/main/src/tuneflow_py/descriptors/param.py
"""
from tuneflow_py import TuneflowPlugin, Song, ParamDescriptor, WidgetType, InjectSource, TrackType
from typing import Any, Dict
from scipy.io.wavfile import read, write
from io import BytesIO
import numpy as np



class MDX(TuneflowPlugin):
    @staticmethod
    def provider_id():
        return "likelian"

    @staticmethod
    def plugin_id():
        return "MDX"

    @staticmethod
    def params(song: Song) -> Dict[str, ParamDescriptor]:

        paramDict = {
            "selectedClipInfos": {
                "defaultValue": None,
                "widget": {
                    "type": WidgetType.NoWidget.value,
                },
                #"hidden": False,
                "injectFrom": {
                    "type": InjectSource.SelectedClipInfos.value
                }
            },
            "clipAudioData": {
                "defaultValue": None,
                "widget": {
                    "type": WidgetType.NoWidget.value,
                },
                "injectFrom": {
                    "type": InjectSource.ClipAudioData.value,
                    "options": {
                        "clips": "selectedAudioClips",
                        "convert": {
                            "toFormat": "wav"
                        }
                    }
                }
            },
        }

        return paramDict


    @staticmethod
    def run(song: Song, params: Dict[str, Any]):

        print("plugin running...")
        print("========================================")

        """
        gather the audio clip data
        """
        selected_clip_infos = params["selectedClipInfos"] #dict
        clipAudioData = params["clipAudioData"] #list
        trackId = clipAudioData[0]["clipInfo"]['trackId']
        clipId = clipAudioData[0]["clipInfo"]['clipId']
        audio_format = clipAudioData[0]["audioData"]["format"]
        audio_bytes = clipAudioData[0]["audioData"]["data"]

        """
        gather the track and clip info
        """
        track = song.get_track_by_id(trackId)
        if track is None:
            raise Exception("Cannot find track")
        track_index = song.get_track_index(track_id=trackId)
        audio_clip = track.get_clip_by_id(clipId)        



        """
        Reverse the audio clip
        """
        #convert WAV bytes into numpy array
        input_samplerate, input_audio = read(BytesIO(audio_bytes))

        #reverse
        reversed_audio = input_audio[::-1]

        #convert numpy array into WAV bytes
        empty_bytes = bytes()
        byte_io = BytesIO(empty_bytes)
        write(byte_io, input_samplerate, reversed_audio)
        reversed_audio_bytes = byte_io.read()


        """
        create new track
        """
        new_track = song.create_track(type=TrackType.AUDIO_TRACK, index=track_index+1)
        
        
        new_track.create_audio_clip(
            clip_start_tick=audio_clip.get_clip_start_tick(),
            clip_end_tick=audio_clip.get_clip_end_tick(),
            audio_clip_data={"audio_data": {"format": "wav", "data": reversed_audio_bytes},
                             "duration": audio_clip.get_duration(),
                             "start_tick": audio_clip.get_clip_start_tick()
                            }
                        )
        