"""
read more about tuneflow_py classes at
https://github.com/tuneflow/tuneflow-py/blob/main/src/tuneflow_py/descriptors/param.py
"""
from tuneflow_py import TuneflowPlugin, Song, ParamDescriptor, WidgetType, InjectSource, TrackType
from typing import Any, Dict
from scipy.io.wavfile import read, write
import soundfile as sf
from io import BytesIO
from run_separate import *
import numpy as np
import tempfile
import os


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
        write audio clip bytes to a temp file
        """
        fd, temp_input_path = tempfile.mkstemp(suffix = '.wav')
        with os.fdopen(fd, 'wb') as tmp:
            tmp.write(audio_bytes)

        """
        source separation
        """
        output_bytes_dict = run_separate(temp_input_path)
        os.remove(temp_input_path)

        if output_bytes_dict is None:
            return None

        """
        add separated audio bytes to new tracks
        """
        def add_stem(stem_bytes, track_index):
            new_track = song.create_track(type=TrackType.AUDIO_TRACK, index=track_index+1)
            track_index += 1
            
            new_track.create_audio_clip(
                clip_start_tick=audio_clip.get_clip_start_tick(),
                clip_end_tick=audio_clip.get_clip_end_tick(),
                audio_clip_data={"audio_data": {"format": "wav", "data": stem_bytes},
                                    "duration": audio_clip.get_duration(),
                                    "start_tick": audio_clip.get_clip_start_tick()
                                }
                            )
            return None
           
        for key in output_bytes_dict:
            add_stem(output_bytes_dict[key], track_index)

        

        