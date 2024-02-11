from winsound import PlaySound, SND_FILENAME
from time import sleep as wait, time
from threading import Thread

from info import Modifiers
# time: a string representing a time in mm:ss.ss format
# returns the time in seconds w/ decimals
def to_seconds(time:str) -> float:
    time:list[str] = time.split(":")
    return (int(time[0]) * 60) + float(time[1])

class Song:
    # File name includes the path to the file
    def __init__(self, song_name:str, file_name:str, seconds_duration:int = None):
        self.file_name:str = file_name
        if file_name[len(file_name) - 4:] != ".wav": # Just in case
            self.file_name += ".wav"
        
        self.song_name:str = song_name

        self.duration:int = seconds_duration
        self.curr_duration:int = None
        if seconds_duration: # Initialize before playing if duration is available, so the ui won't show "None" when the song first starts to play
            self.curr_duration = 0
        self.start_time = None
        self.timer_thread:Thread = None

        # KEYS IN attributes MUST MATCH KEYS IN enabled_colors IN spotify.list_actions
        self.attributes:dict[str, any] = {"playing" : False, # This attribute is updated from the play function, not from Spotify
                                        "queued" : False,
                                        "sequenced" : False,
                                        "modifiers" : set()}

        # Each item in lyrics is a dictionary representing a line in the form of {"time" : start time of this line, "text" : the line's text}
        # lyrics will be None if no lyrics text file 
        self.lyrics:list[dict[str, any]] = None
        try:
            lines = open(f"lyrics/{self.song_name}.txt", "r").readlines() # Will error if no lyrics file with the same name as the song is found

            for line in lines:
                line = {"time" : to_seconds(line[:line.index(" ")]), "text" : line[line.index(" ") + 1:]}
                # Add in the quarter note symbols
                line["text"] = line["text"].replace("/u2669", "\u2669")

                if not self.lyrics:
                    self.lyrics = []
                self.lyrics.append(line) # Newline characters will be included at the end of each line's text
        except:
            self.lyrics = None # If something is wrong with the lyrics' formatting and only some of the lyrics were added
            pass


    def __str__(self) -> str:
        return self.song_name

    def set_player(self, parent_player): # Call before playing the song
        self.player = parent_player

    def play(self):
        # Update the parent player's list of songs that are on cooldown
        self.player.curr_song = self
        if Modifiers.hot not in self.attributes["modifiers"]:
            self.player.songs_on_cooldown.append(self.song_name)

        self.attributes["playing"] = True

        self.timer_thread = Thread(target = self.start_timer, daemon = True)
        self.timer_thread.start()
        PlaySound(self.file_name, SND_FILENAME) # Don't make async

        self.attributes["playing"] = False

    # Call in a separate thread/process
    def start_timer(self) -> None:
        if self.duration: # self.duration will be None if no duration has been passed into the constructor
            self.curr_duration = 0
            self.start_time = time()

            while self.curr_duration < self.duration:
                while time() - self.start_time <= self.curr_duration:
                    wait(0.1)

                self.curr_duration += 1