import sounddevice as sd
import soundfile as sf
import os, sys
import threading
from tkinter import messagebox
from pydub import AudioSegment
VBNAME = "vb-speaker (VB-Audio Virtual Ca"

class AudioInjector:
    def __init__(self):
        if os.path.exists('./audio'):
            self.path = os.listdir('./audio')
            self.clean()
        else:
            os.mkdir('./audio')
            self.path = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.file = None
        self.data = None
        self.samplerate = None
        self.stream = None
        self.data_index = 0
        self.playing = False
        self.play_thread = None
        self.active = False
        self.vbidx = None
        self.idx()

    def clean(self):
        try:
            if len(self.path) > 9:
                diff = len(self.path) - 9
                for i in range(diff):
                    self.path.pop( (len(self.path) - i) - 1)
            for i, file in enumerate(self.path):
                if file.endswith('.mp3'):
                    newfile = AudioSegment.from_mp3('./audio/' + file)
                    wav_filename = file.replace('.mp3', '.wav')
                    newfile.export(f'./audio/{wav_filename}', format='wav')
                    self.path[i] = wav_filename
                    os.remove(f'./audio/{file}')
        except Exception as e:
            print(e)
            
            

    def load_wav(self):
        try:
            self.data, self.samplerate = sf.read(self.file)
        except Exception as e:
            print(f"Error loading WAV file: {e}")
            return False
        return True

    def callback(self, outdata, frames, time, status):
        try:
            if status:
                print(f"Status: {status}")
            if self.data_index + frames < len(self.data):
                outdata[:, :] = self.data[self.data_index:self.data_index + frames, :]
                self.data_index += frames
            else:
                outdata[:len(self.data) - self.data_index, :] = self.data[self.data_index:len(self.data), :]
                outdata[len(self.data) - self.data_index:, :] = 0
                self.data_index = 0
                self.playing = False  # Mark as finished
        except Exception as e:
            print(e)
            outdata =None
            self.data_index=None
            frames=None
            messagebox.showinfo("VoicePad app","App Activated , enter p to Activate the app")
            self.__init__()


    def idx(self):
        try:
            devices = sd.query_devices()
            for idx, device in enumerate(devices):
                if VBNAME == device['name']:
                    self.vbidx = idx
                    self.vb_channels_out = device['max_output_channels']
    
            if self.vbidx is None :
                raise ValueError("Could not find the specified devices.")
            
            print(f"VB-Cable Device Index: {self.vbidx}, Channels: {self.vb_channels_out}")
            return True
        except Exception as e:
            print(e)
            return False

    def Play(self, num):
        if self.active:
            if self.playing:
                try:
                    self.stream.stop()
                except:
                    pass
                self.play_thread = None
                self.playing = True
                self.play_thread = threading.Thread(target=self.play_audio, args=(num,))
                self.play_thread.start()
            elif not self.playing:
                self.playing = True
                self.play_thread = threading.Thread(target=self.play_audio, args=(num,))
                self.play_thread.start()

    def play_audio(self, num):
        try:
            if num == 0:
                self.file = './recorded.wav'
            else:
                self.file = './audio/' + str(self.path[num - 1])

            if not self.load_wav():
                return

            # Ensure samplerate and channels are integers
            self.samplerate = int(self.samplerate)
            channels = int(self.data.shape[1])
    
            with sd.OutputStream(callback=self.callback, channels=channels, samplerate=self.samplerate, device=self.vbidx) as st:
                self.stream = st
                print(f'Playing {self.file} into microphone. Press Ctrl+C to stop.')
                sd.sleep(int(self.data.shape[0] / self.samplerate * 1000))  # Ensure enough time for playback in milliseconds
        
        except ValueError as ve:
            print(f"ValueError during audio streaming: {ve}")
            self.playing = False
        except TypeError as te:
            print(f"TypeError during audio streaming: {te}")
            self.playing = False
        except KeyboardInterrupt:
            print('\nStopped by user.')
        except Exception as e:
            print(f"Error during audio streaming: {e}")
            self.playing = False

    def stop(self):
        if self.play_thread is not None:
            self.play_thread = None
        if self.stream is not None:
            self.stream.abort()



class Mic():
    def __init__(self, vbname, micname):
        self.vbname = vbname
        self.micname = micname
        self.vbidx = None
        self.micidx = None
        self.running = False
        self.streamobj = None

    def idx(self):
        try:
            devices = sd.query_devices()
            for idx, device in enumerate(devices):
                if self.vbname == device['name']:
                    self.vbidx = idx
                    self.vb_channels_out = device['max_output_channels']
                if self.micname == device['name']:
                    self.micidx = idx
                    self.mic_channels_in = device['max_input_channels']

            if self.vbidx is None or self.micidx is None:
                raise ValueError("Could not find the specified devices.")
            
            print(f"VB-Cable Device Index: {self.vbidx}, Channels: {self.vb_channels_out}")
            print(f"Microphone Device Index: {self.micidx}, Channels: {self.mic_channels_in}")
            return True
        except Exception as e:
            print(f"Error in device indexing: {e}")
            return False

    def audio_callback(self, indata, outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        # Ensure the output matches the number of channels expected
        if indata.shape[1] != outdata.shape[1]:
            print(f"Channel mismatch: indata has {indata.shape[1]} channels, outdata has {outdata.shape[1]} channels")
            return
        outdata[:] = indata

    def start(self):
        if self.idx():
            self.running = True
            try:
                with sd.Stream(device=(int(self.micidx), int(self.vbidx)),
                               channels=min(self.mic_channels_in, self.vb_channels_out),
                               callback=self.audio_callback) as stream:
                    self.streamobj = stream
                    stream.start()

                    print("Audio routing started. Press Ctrl+C to stop.")
                    try:
                        while self.running:
                            sd.sleep(1000)
                    except KeyboardInterrupt:
                        print("Interrupted by user.")
            except Exception as e:
                print(f"Error starting stream: {e}")
        else:
            print("Failed to initialize devices. Please check device names and try again.")

    def stop(self):
        self.running = False
        if self.streamobj:
            self.streamobj.stop()
            self.streamobj.close()
        
        

     

        
        

     
