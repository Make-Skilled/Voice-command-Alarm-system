import tkinter as tk
from tkinter import ttk, messagebox
import speech_recognition as sr
import pyttsx3
import datetime
import threading
import time
import re
import pygame

class VoiceAlarmClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Voice Alarm Clock")
        self.root.geometry("600x500")
        self.root.configure(bg='#2c3e50')
        
        # Initialize speech components
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
        # Initialize pygame for alarm sound
        pygame.mixer.init()
        
        # Alarm storage
        self.alarms = []
        self.listening = False
        self.alarm_thread_running = False
        
        # Setup GUI
        self.setup_gui()
        
        # Start alarm monitoring thread
        self.start_alarm_monitor()
        
        # Adjust microphone for ambient noise
        self.calibrate_microphone()
    
    def setup_tts(self):
        """Configure text-to-speech settings"""
        voices = self.tts_engine.getProperty('voices')
        if voices:
            self.tts_engine.setProperty('voice', voices[0].id)
        self.tts_engine.setProperty('rate', 150)
        self.tts_engine.setProperty('volume', 0.8)
    
    def setup_gui(self):
        """Create the graphical user interface"""
        # Title
        title_label = tk.Label(
            self.root, 
            text="🔊 Smart Voice Alarm Clock", 
            font=("Arial", 20, "bold"),
            bg='#2c3e50', 
            fg='#ecf0f1'
        )
        title_label.pack(pady=20)
        
        # Current time display
        self.time_label = tk.Label(
            self.root, 
            text="", 
            font=("Digital-7", 24, "bold"),
            bg='#2c3e50', 
            fg='#e74c3c'
        )
        self.time_label.pack(pady=10)
        self.update_time_display()
        
        # Voice control frame
        voice_frame = tk.Frame(self.root, bg='#2c3e50')
        voice_frame.pack(pady=20)
        
        self.listen_button = tk.Button(
            voice_frame,
            text="🎤 Start Listening",
            command=self.toggle_listening,
            font=("Arial", 12, "bold"),
            bg='#27ae60',
            fg='white',
            padx=20,
            pady=10
        )
        self.listen_button.pack(side=tk.LEFT, padx=10)
        
        self.status_label = tk.Label(
            voice_frame,
            text="Click 'Start Listening' to use voice commands",
            font=("Arial", 10),
            bg='#2c3e50',
            fg='#bdc3c7'
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Manual alarm setting frame
        manual_frame = tk.LabelFrame(
            self.root, 
            text="Manual Alarm Setting", 
            font=("Arial", 12, "bold"),
            bg='#34495e', 
            fg='#ecf0f1'
        )
        manual_frame.pack(pady=20, padx=20, fill='x')
        
        time_frame = tk.Frame(manual_frame, bg='#34495e')
        time_frame.pack(pady=10)
        
        tk.Label(time_frame, text="Hour:", bg='#34495e', fg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        self.hour_var = tk.StringVar(value="12")
        hour_spin = tk.Spinbox(time_frame, from_=1, to=12, textvariable=self.hour_var, width=5)
        hour_spin.pack(side=tk.LEFT, padx=5)
        
        tk.Label(time_frame, text="Minute:", bg='#34495e', fg='#ecf0f1').pack(side=tk.LEFT, padx=5)
        self.minute_var = tk.StringVar(value="00")
        minute_spin = tk.Spinbox(time_frame, from_=0, to=59, textvariable=self.minute_var, width=5, format="%02.0f")
        minute_spin.pack(side=tk.LEFT, padx=5)
        
        self.ampm_var = tk.StringVar(value="AM")
        ampm_combo = ttk.Combobox(time_frame, textvariable=self.ampm_var, values=["AM", "PM"], width=5)
        ampm_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Label(manual_frame, text="Label:", bg='#34495e', fg='#ecf0f1').pack(pady=5)
        self.label_var = tk.StringVar()
        label_entry = tk.Entry(manual_frame, textvariable=self.label_var, width=30)
        label_entry.pack(pady=5)
        
        set_button = tk.Button(
            manual_frame,
            text="Set Alarm",
            command=self.set_manual_alarm,
            bg='#e67e22',
            fg='white',
            font=("Arial", 10, "bold")
        )
        set_button.pack(pady=10)
        
        # Alarms list
        alarms_frame = tk.LabelFrame(
            self.root, 
            text="Active Alarms", 
            font=("Arial", 12, "bold"),
            bg='#34495e', 
            fg='#ecf0f1'
        )
        alarms_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.alarms_listbox = tk.Listbox(
            alarms_frame, 
            bg='#2c3e50', 
            fg='#ecf0f1',
            selectbackground='#e74c3c'
        )
        self.alarms_listbox.pack(fill='both', expand=True, pady=10, padx=10)
        
        delete_button = tk.Button(
            alarms_frame,
            text="Delete Selected Alarm",
            command=self.delete_alarm,
            bg='#e74c3c',
            fg='white',
            font=("Arial", 10, "bold")
        )
        delete_button.pack(pady=5)
        
        # Voice commands help
        help_text = """
Voice Commands:
• "Set alarm for [time]" - e.g., "Set alarm for 7:30 AM"
• "Set alarm for [time] [label]" - e.g., "Set alarm for 8 AM wake up"
• "What time is it?" or "What's the time?"
• "Show my alarms" or "My alarms"
• "Delete all alarms"
        """
        
        help_label = tk.Label(
            self.root,
            text=help_text,
            font=("Arial", 8),
            bg='#2c3e50',
            fg='#95a5a6',
            justify=tk.LEFT
        )
        help_label.pack(pady=10)
    
    def calibrate_microphone(self):
        """Calibrate microphone for ambient noise"""
        def calibrate():
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
            except:
                pass
        
        threading.Thread(target=calibrate, daemon=True).start()
    
    def update_time_display(self):
        """Update the current time display"""
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time_display)
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"TTS: {text}")  # Debug print
        def speak_thread():
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                print("TTS completed")  # Debug print
            except Exception as e:
                print(f"TTS Error: {e}")  # Debug print
        
        threading.Thread(target=speak_thread, daemon=True).start()
    
    def toggle_listening(self):
        """Toggle voice listening on/off"""
        if not self.listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        """Start listening for voice commands"""
        self.listening = True
        self.listen_button.config(text="🔴 Stop Listening", bg='#e74c3c')
        self.status_label.config(text="Listening... Speak your command")
        
        def listen_thread():
            while self.listening:
                try:
                    with self.microphone as source:
                        # Adjust for ambient noise on first run
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        # Listen for audio with longer timeout
                        audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    
                    # Recognize speech
                    command = self.recognizer.recognize_google(audio).lower()
                    print(f"Recognized command: {command}")  # Debug print
                    self.root.after(0, lambda cmd=command: self.process_command(cmd))
                    
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    self.root.after(0, lambda: self.status_label.config(text="Could not understand audio"))
                    continue
                except sr.RequestError as e:
                    self.root.after(0, lambda err=str(e): self.status_label.config(text=f"Speech recognition error: {err}"))
                    break
                except Exception as e:
                    self.root.after(0, lambda err=str(e): self.status_label.config(text=f"Error: {err}"))
                    break
        
        threading.Thread(target=listen_thread, daemon=True).start()
    
    def stop_listening(self):
        """Stop listening for voice commands"""
        self.listening = False
        self.listen_button.config(text="🎤 Start Listening", bg='#27ae60')
        self.status_label.config(text="Click 'Start Listening' to use voice commands")
    
    def process_command(self, command):
        """Process voice commands"""
        print(f"Processing command: {command}")  # Debug print
        self.status_label.config(text=f"Command: {command}")
        
        # More flexible command matching
        if "set alarm" in command or "alarm for" in command:
            self.process_alarm_command(command)
        elif any(phrase in command for phrase in ["what time", "time is it", "what's the time", "the time now"]):
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}")
            print(f"Speaking: The current time is {current_time}")  # Debug print
        elif any(phrase in command for phrase in ["show", "my alarm", "list alarm"]):
            if self.alarms:
                alarm_list = ", ".join([f"{alarm['time']} {alarm['label']}" for alarm in self.alarms])
                self.speak(f"Your alarms are: {alarm_list}")
            else:
                self.speak("You have no active alarms")
        elif "delete all alarm" in command:
            self.alarms.clear()
            self.update_alarms_display()
            self.speak("All alarms deleted")
        else:
            self.speak("Sorry, I didn't understand that command")
    
    def process_alarm_command(self, command):
        """Process alarm setting commands with improved regex patterns"""
        print(f"Processing alarm command: {command}")  # Debug print
        
        # More comprehensive time patterns
        time_patterns = [
            # Matches: "4:24 p.m." or "4:24 PM"
            r'(\d{1,2}):(\d{2})\s*([ap]\.?m\.?)',
            # Matches: "4 p.m." or "4 PM"
            r'(\d{1,2})\s*([ap]\.?m\.?)',
            # Matches: "4:24" (24-hour format)
            r'(\d{1,2}):(\d{2})(?!\s*[ap]\.?m\.?)',
            # Matches standalone numbers that might be hours
            r'(\d{1,2})(?!\s*:)(?!\s*[ap]\.?m\.?)'
        ]
        
        time_match = None
        pattern_used = None
        
        for i, pattern in enumerate(time_patterns):
            time_match = re.search(pattern, command, re.IGNORECASE)
            if time_match:
                pattern_used = i
                print(f"Matched pattern {i}: {time_match.groups()}")  # Debug print
                break
        
        if not time_match:
            self.speak("I couldn't understand the time. Please try again with a format like '4:30 PM' or '4 PM'.")
            return
        
        try:
            groups = time_match.groups()
            
            if pattern_used == 0:  # Hour:Minute AM/PM
                hour, minute, ampm = groups
                hour, minute = int(hour), int(minute)
                ampm = self.normalize_ampm(ampm)
            elif pattern_used == 1:  # Hour AM/PM
                hour, ampm = groups
                hour, minute = int(hour), 0
                ampm = self.normalize_ampm(ampm)
            elif pattern_used == 2:  # Hour:Minute (24-hour)
                hour, minute = groups
                hour, minute = int(hour), int(minute)
                # Convert 24-hour to 12-hour
                if hour == 0:
                    hour, ampm = 12, "AM"
                elif hour < 12:
                    ampm = "AM"
                elif hour == 12:
                    ampm = "PM"
                else:
                    hour -= 12
                    ampm = "PM"
            else:  # pattern_used == 3, just hour
                hour = int(groups[0])
                minute = 0
                # Guess AM/PM based on current time and context
                current_hour = datetime.datetime.now().hour
                if hour <= 12 and current_hour < 12:
                    ampm = "AM"
                else:
                    ampm = "PM"
            
            # Validate hour and minute
            if hour < 1 or hour > 12 or minute < 0 or minute > 59:
                raise ValueError("Invalid time")
            
            # Extract label from command
            label = self.extract_label(command, time_match.group())
            
            # Create alarm
            alarm_time = f"{hour:02d}:{minute:02d} {ampm}"
            self.add_alarm(alarm_time, label)
            self.speak(f"Alarm set for {alarm_time}")
            if label != "Alarm":
                self.speak(f"with label {label}")
            
        except ValueError as e:
            print(f"ValueError in alarm processing: {e}")  # Debug print
            self.speak("Invalid time format. Please try again.")
        except Exception as e:
            print(f"Error in alarm processing: {e}")  # Debug print
            self.speak("Sorry, there was an error setting the alarm.")
    
    def normalize_ampm(self, ampm_str):
        """Normalize AM/PM string"""
        ampm_clean = ampm_str.replace('.', '').upper()
        return "AM" if ampm_clean.startswith('A') else "PM"
    
    def extract_label(self, command, time_str):
        """Extract label from alarm command"""
        # Remove the time part and common alarm phrases
        label_text = command.replace(time_str.lower(), "")
        label_text = re.sub(r'\b(set|alarm|for)\b', '', label_text, flags=re.IGNORECASE)
        label_text = label_text.strip()
        
        # If there's remaining text, use it as label
        if label_text:
            return label_text.title()
        else:
            return "Alarm"
    
    def set_manual_alarm(self):
        """Set alarm manually from GUI inputs"""
        try:
            hour = int(self.hour_var.get())
            minute = int(self.minute_var.get())
            ampm = self.ampm_var.get()
            label = self.label_var.get() or "Manual Alarm"
            
            alarm_time = f"{hour:02d}:{minute:02d} {ampm}"
            self.add_alarm(alarm_time, label)
            
            # Clear inputs
            self.label_var.set("")
            
        except ValueError:
            messagebox.showerror("Error", "Invalid time format")
    
    def add_alarm(self, time_str, label):
        """Add alarm to the list"""
        alarm = {
            'time': time_str,
            'label': label,
            'active': True
        }
        self.alarms.append(alarm)
        self.update_alarms_display()
        print(f"Added alarm: {alarm}")  # Debug print
    
    def update_alarms_display(self):
        """Update the alarms listbox"""
        self.alarms_listbox.delete(0, tk.END)
        for i, alarm in enumerate(self.alarms):
            status = "✓" if alarm['active'] else "✗"
            self.alarms_listbox.insert(tk.END, f"{status} {alarm['time']} - {alarm['label']}")
    
    def delete_alarm(self):
        """Delete selected alarm"""
        selection = self.alarms_listbox.curselection()
        if selection:
            index = selection[0]
            del self.alarms[index]
            self.update_alarms_display()
    
    def start_alarm_monitor(self):
        """Start monitoring for alarm times"""
        def monitor():
            while True:
                current_time = datetime.datetime.now()
                current_time_str = current_time.strftime("%I:%M %p")
                
                for alarm in self.alarms[:]:  # Copy list to avoid modification during iteration
                    if alarm['active'] and alarm['time'] == current_time_str:
                        alarm['active'] = False
                        self.root.after(0, lambda a=alarm: self.trigger_alarm(a))
                
                time.sleep(30)  # Check every 30 seconds
        
        threading.Thread(target=monitor, daemon=True).start()
    
    def trigger_alarm(self, alarm):
        """Trigger an alarm"""
        self.update_alarms_display()
        
        # Play alarm sound and speak
        self.speak(f"Alarm! {alarm['label']}. Time is {alarm['time']}")
        
        # Show alarm popup
        result = messagebox.askquestion(
            "Alarm!", 
            f"🔔 ALARM! 🔔\n\nTime: {alarm['time']}\nLabel: {alarm['label']}\n\nSnooze for 5 minutes?",
            icon='warning'
        )
        
        if result == 'yes':
            # Snooze for 5 minutes
            current = datetime.datetime.now()
            snooze_time = current + datetime.timedelta(minutes=5)
            snooze_time_str = snooze_time.strftime("%I:%M %p")
            
            snooze_alarm = {
                'time': snooze_time_str,
                'label': f"{alarm['label']} (Snoozed)",
                'active': True
            }
            self.alarms.append(snooze_alarm)
            self.update_alarms_display()

def main():
    # Create main window
    root = tk.Tk()
    
    # Create alarm clock app
    app = VoiceAlarmClock(root)
    
    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()