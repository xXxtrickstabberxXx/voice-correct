from pydub import AudioSegment
import ctypes
import numpy as np
class RNNoise(object):
	def __init__(self):
		self.channels=1
		self.sample_rate=48000
		self.sample_width=2
		self.path_to_lib='libs/librnnoise.so.0.4.1'
		self.frame_duration_ms=10
		self.rnnoise_lib = ctypes.cdll.LoadLibrary(self.path_to_lib)
		self.rnnoise_lib.rnnoise_process_frame.argtypes = [ctypes.c_void_p,ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float)]
		self.rnnoise_lib.rnnoise_process_frame.restype = ctypes.c_float
		self.rnnoise_lib.rnnoise_create.restype = ctypes.c_void_p
		self.rnnoise_lib.rnnoise_destroy.argtypes = [ctypes.c_void_p]
		self.rnnoise_obj = self.rnnoise_lib.rnnoise_create(None)
	
	def __get_frames(self,audio):
		audio_bytes=audio.raw_data
		frame_width=int(self.sample_rate*(self.frame_duration_ms/1000.0)*2)
		if len(audio_bytes)%frame_width !=0:
			silence_duration=frame_width - len(audio_bytes) % frame_width
			audio_bytes +=b'\x00'*silence_duration
		
		offset = 0
		frames=[]
		while offset + frame_width<= len(audio_bytes):
			frames.append(audio_bytes[offset:offset + frame_width])
			offset += frame_width
		return frames
	
	def __filter_frames(self,frames,voice_prob_treshold=0.0):
		denoised_frames_with_probability = [self.filter_frame(frame) for frame in frames]
		denoised_frames = [frame_with_prob[1] for frame_with_prob in denoised_frames_with_probability if frame_with_prob[0] >= voice_prob_treshold]
		denoised_audio_bytes = b''.join(denoised_frames)
		denoised_audio = AudioSegment(data=denoised_audio_bytes, sample_width=self.sample_width, frame_rate=self.sample_rate, channels=self.channels)
		return denoised_audio
		
	def filter_frame(self,frame):
		frame_buf = np.ndarray((480,),'h', frame).astype(ctypes.c_float)
		frame_buf_ptr = frame_buf.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
		vad_probability = self.rnnoise_lib.rnnoise_process_frame(self.rnnoise_obj, frame_buf_ptr, frame_buf_ptr)
		return vad_probability, frame_buf.astype(ctypes.c_short).tobytes()
	def filter(self,audio, voice_prob_treshold=0.0):
		frames=self.__get_frames(audio)
		denoised_audio=self.__filter_frames(frames, voice_prob_treshold)
		return(denoised_audio)
