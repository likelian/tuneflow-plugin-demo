from separate import SeperateMDX
import pickle
from typing import List
import json
from gui_data.constants import *
import os
import hashlib


def load_data() -> dict:
    """
    Loads saved pkl file and returns the stored data

    Returns(dict):
        Dictionary containing all the saved data
    """
    try:
        """
        with open('settings.json', 'rb') as data_file:  # Open data file
            data = json.load(data_file)
        """
        with open('data.pkl', 'rb') as data_file:  # Open data file
            data = pickle.load(data_file)
        

        return data
    except (ValueError, FileNotFoundError):
        # Data File is corrupted or not found so recreate it

        save_data(data=DEFAULT_DATA)

        return load_data()


def load_model_hash_data(dictionary):
    '''Get the model hash dictionary'''

    with open(dictionary) as d:
        data = d.read()

    return json.loads(data)

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
model_hash_table = {}
MDX_MIXER_PATH = os.path.join(BASE_PATH, 'lib_v5', 'mixer.ckpt')
MODELS_DIR = os.path.join(BASE_PATH, 'models')
MDX_MODELS_DIR = os.path.join(MODELS_DIR, 'MDX_Net_Models')
MDX_HASH_DIR = os.path.join(MDX_MODELS_DIR, 'model_data')
MDX_HASH_JSON = os.path.join(MDX_MODELS_DIR, 'model_data', 'model_data.json')
mdx_hash_MAPPER = load_model_hash_data(MDX_HASH_JSON)
data = load_data()


class ModelData():
    def __init__(self, model_name: str, 
                 selected_process_method=MDX_ARCH_TYPE, 
                 new_model_name="",
                 is_secondary_model=False, 
                 primary_model_primary_stem=None, 
                 is_primary_model_primary_stem_only=False, 
                 is_primary_model_secondary_stem_only=False, 
                 is_pre_proc_model=False,
                 is_dry_check=False):

        self.new_model_name = new_model_name
        self.is_gpu_conversion = 0 #if root.is_gpu_conversion_var.get() else -1
        self.is_normalization = False #root.is_normalization_var.get()
        self.is_primary_stem_only = True #root.is_primary_stem_only_var.get()
        self.is_secondary_stem_only = False #root.is_secondary_stem_only_var.get()
        self.is_denoise = False #root.is_denoise_var.get()
        self.mdx_batch_size = 1 #if root.mdx_batch_size_var.get() == DEF_OPT else int(root.mdx_batch_size_var.get())
        self.is_mdx_ckpt = False
        self.wav_type_set = "PCM_16" #root.wav_type_set
        self.mp3_bit_set = "320k" #root.mp3_bit_set_var.get()
        self.save_format = "WAV" #root.save_format_var.get()
        self.is_invert_spec = False #root.is_invert_spec_var.get()
        self.is_mixer_mode = False #root.is_mixer_mode_var.get()
        self.demucs_stems = "All Stems" #root.demucs_stems_var.get()
        self.demucs_source_list = []
        self.demucs_stem_count = 0
        self.mixer_path = BASE_PATH + "/models/MDX_Net_Models" #MDX_MIXER_PATH
        self.model_name = model_name
        self.process_method = selected_process_method
        self.model_status = False if self.model_name == CHOOSE_MODEL or self.model_name == NO_MODEL else True
        self.primary_stem = None
        self.secondary_stem = None
        self.is_ensemble_mode = False
        self.ensemble_primary_stem = None
        self.ensemble_secondary_stem = None
        self.primary_model_primary_stem = primary_model_primary_stem
        self.is_secondary_model = is_secondary_model
        self.secondary_model = None
        self.secondary_model_scale = None
        self.demucs_4_stem_added_count = 0
        self.is_demucs_4_stem_secondaries = False
        self.is_4_stem_ensemble = False
        self.pre_proc_model = None
        self.pre_proc_model_activated = False
        self.is_pre_proc_model = is_pre_proc_model
        self.is_dry_check = is_dry_check
        self.model_samplerate = 44100
        self.model_capacity = 32, 128
        self.is_vr_51_model = False
        self.is_demucs_pre_proc_model_inst_mix = False
        self.manual_download_Button = None
        self.secondary_model_4_stem = []
        self.secondary_model_4_stem_scale = []
        self.secondary_model_4_stem_names = []
        self.secondary_model_4_stem_model_names_list = []
        self.all_models = []
        self.secondary_model_other = None
        self.secondary_model_scale_other = None
        self.secondary_model_bass = None
        self.secondary_model_scale_bass = None
        self.secondary_model_drums = None
        self.secondary_model_scale_drums = None
        self.compensate = 1.035 #maded-up  
        #self.n_fft = 6144
        if self.new_model_name == "UVR-MDX-NET-Inst_HQ_1.onnx":
            self.mdx_dim_f_set = 2048
        elif self.new_model_name == "Kim_Vocal_1.onnx":
            self.mdx_dim_f_set = 3072
        self.mdx_dim_t_set = 8 #maded-up
        self.mdx_n_fft_scale_set = 6144



        if selected_process_method == ENSEMBLE_MODE:
            partitioned_name = model_name.partition(ENSEMBLE_PARTITION)
            self.process_method = partitioned_name[0]
            self.model_name = partitioned_name[2]
            self.model_and_process_tag = model_name
            self.ensemble_primary_stem, self.ensemble_secondary_stem = root.return_ensemble_stems()
            self.is_ensemble_mode = True if not is_secondary_model and not is_pre_proc_model else False
            self.is_4_stem_ensemble = True if root.ensemble_main_stem_var.get() == FOUR_STEM_ENSEMBLE and self.is_ensemble_mode else False
            self.pre_proc_model_activated = root.is_demucs_pre_proc_model_activate_var.get() if not self.ensemble_primary_stem == VOCAL_STEM else False

        if self.process_method == VR_ARCH_TYPE:
            self.is_secondary_model_activated = root.vr_is_secondary_model_activate_var.get() if not self.is_secondary_model else False
            self.aggression_setting = float(int(root.aggression_setting_var.get())/100)
            self.is_tta = root.is_tta_var.get()
            self.is_post_process = root.is_post_process_var.get()
            self.window_size = int(root.window_size_var.get())
            self.batch_size = 1 if root.batch_size_var.get() == DEF_OPT else int(root.batch_size_var.get())
            self.crop_size = int(root.crop_size_var.get())
            self.is_high_end_process = 'mirroring' if root.is_high_end_process_var.get() else 'None'
            self.post_process_threshold = float(root.post_process_threshold_var.get())
            self.model_capacity = 32, 128
            self.model_path = os.path.join(VR_MODELS_DIR, f"{self.model_name}.pth")
            self.get_model_hash()
            if self.model_hash:
                self.model_data = self.get_model_data(VR_HASH_DIR, root.vr_hash_MAPPER) if not self.model_hash == WOOD_INST_MODEL_HASH else WOOD_INST_PARAMS
                if self.model_data:
                    vr_model_param = os.path.join(VR_PARAM_DIR, "{}.json".format(self.model_data["vr_model_param"]))
                    self.primary_stem = self.model_data["primary_stem"]
                    self.secondary_stem = STEM_PAIR_MAPPER[self.primary_stem]
                    self.vr_model_param = ModelParameters(vr_model_param)
                    self.model_samplerate = self.vr_model_param.param['sr']
                    if "nout" in self.model_data.keys() and "nout_lstm" in self.model_data.keys():
                        self.model_capacity = self.model_data["nout"], self.model_data["nout_lstm"]
                        self.is_vr_51_model = True
                else:
                    self.model_status = False
                
        if self.process_method == MDX_ARCH_TYPE:
            self.is_secondary_model_activated = data['mdx_is_secondary_model_activate'] #root.mdx_is_secondary_model_activate_var.get() if not is_secondary_model else False
            self.margin = 44100 #int(root.margin_var.get())
            self.chunks = 0
            #self.chunks = root.determine_auto_chunks(root.chunks_var.get(), self.is_gpu_conversion) if root.is_chunk_mdxnet_var.get() else 0
            self.get_mdx_model_path()
            self.get_model_hash()
            if self.model_hash:
                self.model_data = self.get_model_data(MDX_HASH_DIR, mdx_hash_MAPPER)
                if self.model_data:
                    self.compensate = self.model_data["compensate"]# if root.compensate_var.get() == AUTO_SELECT else float(root.compensate_var.get())
                    self.mdx_dim_f_set = self.model_data["mdx_dim_f_set"]
                    self.mdx_dim_t_set = self.model_data["mdx_dim_t_set"]
                    self.mdx_n_fft_scale_set = self.model_data["mdx_n_fft_scale_set"]
                    self.primary_stem = self.model_data["primary_stem"]
                    self.secondary_stem = STEM_PAIR_MAPPER[self.primary_stem]
                else:
                    self.model_status = False


        self.model_basename = os.path.splitext(os.path.basename(self.model_path))[0] if self.model_status else None
        self.pre_proc_model_activated = self.pre_proc_model_activated if not self.is_secondary_model else False
        
        self.is_primary_model_primary_stem_only = is_primary_model_primary_stem_only
        self.is_primary_model_secondary_stem_only = is_primary_model_secondary_stem_only

        if self.is_secondary_model_activated and self.model_status:
            if (not self.is_ensemble_mode and root.demucs_stems_var.get() == ALL_STEMS and self.process_method == DEMUCS_ARCH_TYPE) or self.is_4_stem_ensemble:
                for key in DEMUCS_4_SOURCE_LIST:
                    self.secondary_model_data(key)
                    self.secondary_model_4_stem.append(self.secondary_model)
                    self.secondary_model_4_stem_scale.append(self.secondary_model_scale)
                    self.secondary_model_4_stem_names.append(key)
                self.demucs_4_stem_added_count = sum(i is not None for i in self.secondary_model_4_stem)
                self.is_secondary_model_activated = False if all(i is None for i in self.secondary_model_4_stem) else True
                self.demucs_4_stem_added_count = self.demucs_4_stem_added_count - 1 if self.is_secondary_model_activated else self.demucs_4_stem_added_count
                if self.is_secondary_model_activated:
                    self.secondary_model_4_stem_model_names_list = [None if i is None else i.model_basename for i in self.secondary_model_4_stem]
                    self.is_demucs_4_stem_secondaries = True 
            else:
                primary_stem = self.ensemble_primary_stem if self.is_ensemble_mode and self.process_method == DEMUCS_ARCH_TYPE else self.primary_stem
                self.secondary_model_data(primary_stem)
                
        if self.process_method == DEMUCS_ARCH_TYPE and not is_secondary_model:
            if self.demucs_stem_count >= 3 and self.pre_proc_model_activated:
                self.pre_proc_model_activated = True
                self.pre_proc_model = root.process_determine_demucs_pre_proc_model(self.primary_stem)
                self.is_demucs_pre_proc_model_inst_mix = root.is_demucs_pre_proc_model_inst_mix_var.get() if self.pre_proc_model else False

    def secondary_model_data(self, primary_stem):
        secondary_model_data = root.process_determine_secondary_model(self.process_method, primary_stem, self.is_primary_stem_only, self.is_secondary_stem_only)
        self.secondary_model = secondary_model_data[0]
        self.secondary_model_scale = secondary_model_data[1]
        self.is_secondary_model_activated = False if not self.secondary_model else True
        if self.secondary_model:
            self.is_secondary_model_activated = False if self.secondary_model.model_basename == self.model_basename else True
              
    def get_mdx_model_path(self):
        
        if self.model_name.endswith(CKPT):
            # self.chunks = 0
            # self.is_mdx_batch_mode = True
            self.is_mdx_ckpt = True
            
        ext = '' if self.is_mdx_ckpt else ONNX


        mdx_model_name_mapper_path = BASE_PATH + "/models/MDX_Net_Models/model_data/model_name_mapper.json"
        mdx_name_select_MAPPER = json.load(open(mdx_model_name_mapper_path))

        MDX_MODELS_DIR = BASE_PATH + "/models/MDX_Net_Models/"

        #for file_name, chosen_mdx_model in root.mdx_name_select_MAPPER.items():
        for file_name, chosen_mdx_model in mdx_name_select_MAPPER.items():
            if self.model_name in chosen_mdx_model:
                self.model_path = os.path.join(MDX_MODELS_DIR, f"{file_name}{ext}")
                break
        else:
            self.model_path = os.path.join(MDX_MODELS_DIR, f"{self.model_name}{ext}")
            
        self.mixer_path = os.path.join(MDX_MODELS_DIR, f"mixer_val.ckpt")

        self.model_path = MDX_MODELS_DIR + self.new_model_name
        
    
    def get_demucs_model_path(self):
        
        demucs_newer = [True for x in DEMUCS_NEWER_TAGS if x in self.model_name]
        demucs_model_dir = DEMUCS_NEWER_REPO_DIR if demucs_newer else DEMUCS_MODELS_DIR
        
        for file_name, chosen_model in root.demucs_name_select_MAPPER.items():
            if self.model_name in chosen_model:
                self.model_path = os.path.join(demucs_model_dir, file_name)
                break
        else:
            self.model_path = os.path.join(DEMUCS_NEWER_REPO_DIR, f'{self.model_name}.yaml')

    def get_demucs_model_data(self):

        self.demucs_version = DEMUCS_V4

        for key, value in DEMUCS_VERSION_MAPPER.items():
            if value in self.model_name:
                self.demucs_version = key

        self.demucs_source_list = DEMUCS_2_SOURCE if DEMUCS_UVR_MODEL in self.model_name else DEMUCS_4_SOURCE
        self.demucs_source_map = DEMUCS_2_SOURCE_MAPPER if DEMUCS_UVR_MODEL in self.model_name else DEMUCS_4_SOURCE_MAPPER
        self.demucs_stem_count = 2 if DEMUCS_UVR_MODEL in self.model_name else 4
        
        if not self.is_ensemble_mode:
            self.primary_stem = PRIMARY_STEM if self.demucs_stems == ALL_STEMS else self.demucs_stems
            self.secondary_stem = STEM_PAIR_MAPPER[self.primary_stem]

    def get_model_data(self, model_hash_dir, hash_mapper):

        model_settings_json = os.path.join(model_hash_dir, "{}.json".format(self.model_hash))

        if os.path.isfile(model_settings_json):
            return json.load(open(model_settings_json))
        else:
            for hash, settings in hash_mapper.items():
                if self.model_hash in hash:
                    return settings
            else:
                return self.get_model_data_from_popup()

    def get_model_data_from_popup(self):
        return None
        if not self.is_dry_check:
            confirm = tk.messagebox.askyesno(title=UNRECOGNIZED_MODEL[0],
                                             message=f"\"{self.model_name}\"{UNRECOGNIZED_MODEL[1]}",
                                             parent=root)
                                            
            if confirm:
                if self.process_method == VR_ARCH_TYPE:
                    root.pop_up_vr_param(self.model_hash)
                    return root.vr_model_params
                if self.process_method == MDX_ARCH_TYPE:
                    root.pop_up_mdx_model(self.model_hash, self.model_path)
                    return root.mdx_model_params
            else:
                return None
        else:
            return None

    def get_model_hash(self):
        self.model_hash = None
        
        if not os.path.isfile(self.model_path):
            self.model_status = False
            self.model_hash is None
        else:
            if model_hash_table:
                for (key, value) in model_hash_table.items():
                    if self.model_path == key:
                        self.model_hash = value
                        break
                    
            if not self.model_hash:
                try:
                    with open(self.model_path, 'rb') as f:
                        f.seek(- 10000 * 1024, 2)
                        self.model_hash = hashlib.md5(f.read()).hexdigest()
                except:
                    self.model_hash = hashlib.md5(open(self.model_path,'rb').read()).hexdigest()
                    
                table_entry = {self.model_path: self.model_hash}
                model_hash_table.update(table_entry)




##############################################



def run_separate(audio_file, export_path, is_Vocal=True, is_Instrumental=True):
    """
    return:
        export_path {
            "vocal" : vocal_stem_abs_path,
            "instrumental" : instrumental_stem_abs_path
        }
    """

    if not (is_Vocal or is_Instrumental):
        print("invalid selection, not vocal nor instrumental")
        return None

    SeperateMDX.is_mdx_ckpt = False
    SeperateMDX.run_type = ['CPUExecutionProvider'] #['CUDAExecutionProvider']

    model = data['mdx_net_model']
    MDX_ARCH_TYPE = "MDX-Net"
    audio_file_base = ""
    export_path = BASE_PATH.rpartition('/')[0] + "/audio/" + "output_audio/" #absolute path
    model_data = None

    process_data = {
            'model_data': None, 
            'export_path': export_path,
            'audio_file_base': audio_file_base, #file path before filename
            'audio_file': audio_file,
            'set_progress_bar': None, #set_progress_bar,
            'write_to_console': None,
            'process_iteration': None,
            'cached_source_callback': None,
            'cached_model_source_holder': None,
            'list_all_models': None,
            'is_ensemble_master': False,
            'is_4_stem_ensemble': False
            }

    export_path_dict = {}

    if is_Vocal:
        model_data = ModelData(model, MDX_ARCH_TYPE, new_model_name="Kim_Vocal_1.onnx")
        process_data['model_data'] = model_data
        seperator = SeperateMDX(model_data, process_data)
        seperator.seperate()
        export_path_dict["vocal"] = export_path + "_(Vocals).wav"
    
    if is_Instrumental:
        model_data = ModelData(model, MDX_ARCH_TYPE, new_model_name="UVR-MDX-NET-Inst_HQ_1.onnx")
        process_data['model_data'] = model_data
        seperator = SeperateMDX(model_data, process_data)
        seperator.seperate()
        export_path_dict["instrumental"] = export_path + "_(Instrumental).wav"
    
    return export_path_dict




