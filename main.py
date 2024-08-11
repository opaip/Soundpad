
import customtkinter as ctk
import os, threading
import sys,libs.func,libs.recorder
from tkinter import messagebox
from pynput import keyboard

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")  # This sets the theme to blue

MAX_AUDIO = 9
MICNAME = 'mymic (2- High Definition Audio' 
VBNAME = "vb-speaker (VB-Audio Virtual Ca"



class VoicePadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Voice Pad App")
        self.root.geometry("700x600")
        self.root.configure(bg='#001f3f')  # Dark blue background

        self.buttons = []
        self.sounds = []

        files = os.listdir('./audio')
        if len(files) > MAX_AUDIO:
            index = len(files) - 1
            for i in range(len(files) - MAX_AUDIO):
                files.pop(index)
                index -= 1

        for i in range(len(files)):
            row = i // 3
            col = i % 3
            button = ctk.CTkButton(self.root, text=f"{files[i]}({i+1})", command=lambda i=i: self.play_audio(i+1), 
                                   fg_color="#004080", hover_color="#003366", width=100, height=100)
            button.grid(row=row, column=col, padx=10, pady=10)
            self.buttons.append(button)

        # Settings button
        self.settings_button = ctk.CTkButton(self.root, text="Settings", command=self.open_settings, 
                                             fg_color="#004080", hover_color="#003366", width=100, height=40)
        self.settings_button.grid(row=3, column=1, padx=10, pady=10)

        self.instruction_lable = ctk.CTkLabel(self.root,text = 'press p to activate or deactivate',fg_color=None,text_color="white")
        self.instruction_lable.grid(row=4,column=0,columnspan=3,pady=10)
        self.instruction_lable2 = ctk.CTkLabel(self.root,text = 'press l to rercord audio',fg_color=None,text_color="white")
        self.instruction_lable2.grid(row=4,column=0,columnspan=3,pady=6)
        self.instruction_lable3 = ctk.CTkLabel(self.root,text = 'press l to rercord audio',fg_color=None,text_color="white")
        self.instruction_lable3.grid(row=4,column=0,columnspan=3,pady=2)

        self.recordb = ctk.CTkButton(self.root,text='record',fg_color="red",hover_color="#ff6666",state="disabled",width=100,height=40,corner_radius=20)
        self.recordb.grid(row=5,column=1,padx=10,pady=10)

    def play_audio(self, idx):
        threading.Thread(target=aud.Play, args=(idx,)).start()

    def open_settings(self):
        # Add your settings code here
        messagebox.showinfo("Settings", "Settings dialog coming soon!")

    def quit_app(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            aud.stop()
            sys.exit()

    def enable_rb(self):
        self.recordb.configure(state="normal")
    def disable_rb(self):
        self.recordb.configure(state='disabled')
    

class listener(keyboard.Listener):
    def __init__(self, player,app,recorder):
        super().__init__(on_press=self.on_press,on_release = self.on_release)
        self.player = player
        self.app = app
        self.recorder = recorder

    def on_press(self, key):
        try:

            if isinstance(key, keyboard.KeyCode):  # alphanumeric key event
                if key.char == 'p':  # press p to activate
                    def show_status_message():
                        if self.player.active:
                            self.player.active = False
                            messagebox.showinfo("Voice Pad App", "App Deactivated")
                        else:
                            self.player.active = True
                            messagebox.showinfo("Voice Pad App", "App Activated")
                    # Run the messagebox in a separate thread to avoid blocking
                    threading.Thread(target=show_status_message).start()

                elif key.char =="l" or key.char == "L":
                    if self.player.active == True:
                        if self.app.recordb.cget("state") == "disabled":
                            self.app.enable_rb()
                            self.recorder.start()
                
                elif key.char =='t' or key.char == "T":
                    if self.player.active:
                        try:
                            self.player.stream.stop()
                        except :
                            pass
                        
            # Check if key is a number (0-9)
            if key.char.isnumeric():
                if self.player.active == True:
                    number = int(key.char)
                    if number == 0:
                        self.player.Play(0) #play the reorded audio
                    if number !=0:
                        self.player.Play(number)
            
                
        except Exception as e:
            print(e)


    def on_release(self,key):
        try:

            if isinstance(key, keyboard.KeyCode):
                if self.player.active == True:
                    if key.char == 'l' or key.char == 'L':
                        self.app.disable_rb()
                        self.recorder.stop()
                        print('play the recorded audio with 0')

        except Exception as e:
            print(e)



# Main function
if __name__ == "__main__":
    aud = libs.func.AudioInjector()
    mic = libs.func.Mic(VBNAME,MICNAME)
    threading.Thread(target = mic.start).start()
    Recorder = libs.recorder.recorder('./recorded.wav')
    root = ctk.CTk()
    app = VoicePadApp(root)

    l = listener(aud,app,Recorder)
    l.start()
    threading.Thread(target=l.join).start()

    root.mainloop()
