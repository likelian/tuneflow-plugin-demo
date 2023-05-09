from typing import Any, Dict
from tuneflow_py import TuneflowPlugin, Song, ParamDescriptor, WidgetType, InjectSource, TrackType

"""
read more about tuneflow_py classes at 
https://github.com/tuneflow/tuneflow-py/blob/main/src/tuneflow_py/descriptors/param.py
"""



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


        """
        gather the audio clip data
        """
        print("params.keys(): ", params.keys(), "\n")

        selected_clip_infos = params["selectedClipInfos"] #dict
        print("selected_clip_infos: ", selected_clip_infos, "\n")

        clipAudioData = params["clipAudioData"] #list
        print("clipAudioData[0].keys(): ", clipAudioData[0].keys(), "\n") #dict

        print("clipAudioData[0][\"clipInfo\"]: ", clipAudioData[0]["clipInfo"], "\n")
        trackId = clipAudioData[0]["clipInfo"]['trackId']
        clipId = clipAudioData[0]["clipInfo"]['clipId']

        print("clipAudioData[0][\"audioData\"].keys(); ", clipAudioData[0]["audioData"].keys(), "\n")
        audio_format = clipAudioData[0]["audioData"]["format"]

        print("audio_format: ", audio_format, "\n")
        audio_bytes = clipAudioData[0]["audioData"]["data"]
        #print(audio_bytes)

        """
        gather the track and clip info
        """
        track = song.get_track_by_id(trackId)
        if track is None:
            raise Exception("Cannot find track")
        print("track: ", track, "\n")

        track_index = song.get_track_index(track_id=trackId)
        print("track_index: ", track_index, "\n")

        audio_clip = track.get_clip_by_id(clipId)        
        print("audio_clip: ", audio_clip, "\n")


        """
        source separation
        """



        """
        create new track
        """
       
        new_track = song.create_track(type=TrackType.AUDIO_TRACK, index=track_index+1)
        
        
        new_track.create_audio_clip(
            clip_start_tick=audio_clip.get_clip_start_tick(),
            clip_end_tick=audio_clip.get_clip_end_tick(),
            audio_clip_data={"audio_data": {"format": "wav", "data": audio_bytes},
                             "duration": audio_clip.get_duration(),
                             "start_tick": audio_clip.get_clip_start_tick()
                            }
                        )
        