"""
sound_manager.py - Procedural 8-bit chiptune sound generator and music player.
Generates retro sounds and music directly in memory without requiring external audio files.
"""
import io
import math
import wave
import struct
import random
import pygame

class SoundManager:
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        self.current_bgm = None
        self.bgm_channel = None
        self.sfx_volume = 0.7
        self.bgm_volume = 0.5
        
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.bgm_channel = pygame.mixer.Channel(0)
            self.generate_all_sounds()
        except Exception as e:
            print(f"Audio init notice: {e}")
            self.enabled = False

    def _create_wav(self, samples, sample_rate=44100):
        """Converts floating point sample list (-1.0 to 1.0) into a pygame.mixer.Sound object."""
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav_file:
            wav_file.setnchannels(1) # mono
            wav_file.setsampwidth(2) # 16-bit
            wav_file.setframerate(sample_rate)
            
            raw_frames = bytearray()
            for s in samples:
                # Clamp to -1.0 .. 1.0
                val = max(-1.0, min(1.0, s))
                int_val = int(val * 32767.0)
                raw_frames.extend(struct.pack('<h', int_val))
            wav_file.writeframes(raw_frames)
            
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    def _square_wave(self, freq, duration, duty=0.5, sample_rate=44100, volume=0.5):
        num_samples = int(duration * sample_rate)
        samples = []
        period = sample_rate / max(1.0, freq)
        for i in range(num_samples):
            phase = (i % period) / period
            val = volume if phase < duty else -volume
            # Apply smooth linear envelope decay
            env = 1.0 - (i / num_samples) * 0.7
            samples.append(val * env)
        return samples

    def _noise_burst(self, duration, sample_rate=44100, volume=0.5, decay_exp=2.0):
        num_samples = int(duration * sample_rate)
        samples = []
        for i in range(num_samples):
            t = i / num_samples
            env = (1.0 - t) ** decay_exp
            samples.append((random.random() * 2.0 - 1.0) * volume * env)
        return samples

    def _freq_sweep(self, start_f, end_f, duration, sample_rate=44100, volume=0.5, wave_type="square"):
        num_samples = int(duration * sample_rate)
        samples = []
        phase = 0.0
        for i in range(num_samples):
            t = i / num_samples
            freq = start_f + (end_f - start_f) * t
            phase += 2.0 * math.pi * freq / sample_rate
            if wave_type == "square":
                val = volume if (phase % (2.0 * math.pi)) < math.pi else -volume
            elif wave_type == "triangle":
                val = volume * (2.0 / math.pi) * math.asin(math.sin(phase))
            else: # sine
                val = volume * math.sin(phase)
            env = 1.0 - t * 0.8
            samples.append(val * env)
        return samples

    def _create_melody(self, notes_freq_duration, sample_rate=44100, wave_type="square", volume=0.4):
        """Creates a concatenated melody from list of (freq, duration, duty) tuples."""
        samples = []
        for item in notes_freq_duration:
            freq = item[0]
            dur = item[1]
            duty = item[2] if len(item) > 2 else 0.5
            if freq == 0:
                # Rest
                samples.extend([0.0] * int(dur * sample_rate))
            else:
                num_s = int(dur * sample_rate)
                period = sample_rate / max(1.0, freq)
                for i in range(num_s):
                    phase = (i % period) / period
                    if wave_type == "square":
                        val = volume if phase < duty else -volume
                    elif wave_type == "triangle":
                        val = volume * (abs((phase * 4.0) - 2.0) - 1.0)
                    else:
                        val = volume * math.sin(2.0 * math.pi * phase)
                    # Envelope
                    env = max(0.0, 1.0 - (i / num_s) * 0.3)
                    if i < 200:
                        env *= (i / 200) # anti-pop attack
                    samples.append(val * env)
        return samples

    def generate_all_sounds(self):
        if not self.enabled:
            return
        
        SR = 44100
        
        # 1. Menu cursor select
        s = self._square_wave(880, 0.04, duty=0.25, volume=0.3)
        self.sounds["select"] = self._create_wav(s, SR)
        
        # 2. Confirm / Enter
        s = self._melody_samples([(523, 0.05), (659, 0.05), (784, 0.08)], volume=0.35)
        self.sounds["confirm"] = self._create_wav(s, SR)
        
        # 3. Cancel
        s = self._melody_samples([(440, 0.04), (330, 0.08)], volume=0.35)
        self.sounds["cancel"] = self._create_wav(s, SR)
        
        # 4. Tackle / Hit impact
        s = self._noise_burst(0.12, volume=0.6, decay_exp=3.0)
        self.sounds["hit"] = self._create_wav(s, SR)
        
        # 5. Super effective hit
        s = self._freq_sweep(300, 120, 0.25, volume=0.7, wave_type="square")
        s2 = self._noise_burst(0.25, volume=0.5, decay_exp=2.0)
        combined = [s[i] + s2[i] for i in range(min(len(s), len(s2)))]
        self.sounds["super_hit"] = self._create_wav(combined, SR)
        
        # 6. Fire move (Ember / Flamethrower)
        s = self._noise_burst(0.3, volume=0.5, decay_exp=1.2)
        self.sounds["fire"] = self._create_wav(s, SR)
        
        # 7. Water move (Bubble / Water Gun)
        s = self._freq_sweep(400, 900, 0.18, volume=0.4, wave_type="triangle")
        self.sounds["water"] = self._create_wav(s, SR)
        
        # 8. Electric move (Thunder Shock)
        s = []
        for i in range(int(0.22 * SR)):
            t = i / SR
            f = 440 + 200 * math.sin(2.0 * math.pi * 35 * t)
            val = 0.4 if (i % (SR / f)) < (SR / f * 0.5) else -0.4
            noise = (random.random() * 2 - 1) * 0.2
            s.append((val + noise) * (1.0 - t / 0.22))
        self.sounds["electric"] = self._create_wav(s, SR)
        
        # 9. Grass move (Vine Whip / Razor Leaf)
        s = self._freq_sweep(900, 300, 0.15, volume=0.4, wave_type="triangle")
        self.sounds["grass"] = self._create_wav(s, SR)
        
        # 10. Pokeball throw
        s = self._freq_sweep(300, 800, 0.16, volume=0.35, wave_type="sine")
        self.sounds["throw"] = self._create_wav(s, SR)
        
        # 11. Pokeball shake
        s = self._melody_samples([(600, 0.06), (500, 0.06)], volume=0.35)
        self.sounds["ball_shake"] = self._create_wav(s, SR)
        
        # 12. Catch success chime
        s = self._melody_samples([(523, 0.1), (659, 0.1), (784, 0.1), (1046, 0.3)], volume=0.4)
        self.sounds["catch_success"] = self._create_wav(s, SR)
        
        # 13. Level Up Fanfare
        s = self._melody_samples([
            (523, 0.08), (523, 0.08), (523, 0.08), (659, 0.12), (784, 0.12), (1046, 0.35)
        ], volume=0.45)
        self.sounds["level_up"] = self._create_wav(s, SR)
        
        # 14. Pokemon Faint
        s = self._freq_sweep(400, 100, 0.4, volume=0.4, wave_type="triangle")
        self.sounds["faint"] = self._create_wav(s, SR)
        
        # 15. Heal Chime
        s = self._melody_samples([
            (659, 0.12), (784, 0.12), (987, 0.12), (1318, 0.25)
        ], volume=0.4)
        self.sounds["heal"] = self._create_wav(s, SR)
        
        # 16. Wild Encounter intro
        s = self._freq_sweep(200, 1200, 0.35, volume=0.5, wave_type="square")
        self.sounds["wild_encounter"] = self._create_wav(s, SR)
        
        # 17. Grass rustle step
        s = self._noise_burst(0.06, volume=0.25, decay_exp=4.0)
        self.sounds["rustle"] = self._create_wav(s, SR)
        
        # Generate BGM tracks
        self._generate_bgm_tracks(SR)

    def _melody_samples(self, note_list, volume=0.4, SR=44100):
        notes = []
        for n in note_list:
            freq = n[0]
            dur = n[1]
            notes.append((freq, dur, 0.5))
        return self._create_melody(notes, SR, wave_type="square", volume=volume)

    def _generate_bgm_tracks(self, SR):
        # 1. Peaceful Town Theme Loop
        town_notes = [
            # C major peaceful melody
            (523.25, 0.3), (659.25, 0.3), (783.99, 0.3), (659.25, 0.3),
            (587.33, 0.3), (698.46, 0.3), (880.00, 0.3), (698.46, 0.3),
            (659.25, 0.3), (783.99, 0.3), (987.77, 0.3), (783.99, 0.3),
            (1046.50, 0.6), (783.99, 0.3), (523.25, 0.3),
            # Phrase 2
            (880.00, 0.3), (987.77, 0.3), (1046.50, 0.3), (880.00, 0.3),
            (783.99, 0.3), (659.25, 0.3), (587.33, 0.6),
            (523.25, 0.6), (0, 0.2)
        ]
        s_lead = self._melody_samples(town_notes, volume=0.22, SR=SR)
        self.sounds["bgm_town"] = self._create_wav(s_lead, SR)
        
        # 2. Battle Theme Loop (Fast energetic chiptune arpeggios & bass)
        battle_notes = [
            # Driving rhythm in D minor / A
            (293.66, 0.1), (349.23, 0.1), (440.00, 0.1), (587.33, 0.1),
            (293.66, 0.1), (349.23, 0.1), (440.00, 0.1), (587.33, 0.1),
            (261.63, 0.1), (329.63, 0.1), (392.00, 0.1), (523.25, 0.1),
            (261.63, 0.1), (329.63, 0.1), (392.00, 0.1), (523.25, 0.1),
            # Melody peak
            (440.00, 0.15), (587.33, 0.15), (659.25, 0.15), (698.46, 0.15),
            (880.00, 0.2), (783.99, 0.1), (698.46, 0.1), (659.25, 0.2),
            (587.33, 0.3), (440.00, 0.1), (0, 0.1)
        ]
        s_battle = self._melody_samples(battle_notes, volume=0.25, SR=SR)
        self.sounds["bgm_battle"] = self._create_wav(s_battle, SR)
        
        # 3. Victory Theme
        victory_notes = [
            (523.25, 0.12), (659.25, 0.12), (783.99, 0.12), (1046.5, 0.24),
            (880.00, 0.12), (1046.5, 0.36),
            (783.99, 0.12), (659.25, 0.12), (783.99, 0.4)
        ]
        s_victory = self._melody_samples(victory_notes, volume=0.3, SR=SR)
        self.sounds["bgm_victory"] = self._create_wav(s_victory, SR)

    def play_sfx(self, sound_name):
        if not self.enabled or sound_name not in self.sounds:
            return
        try:
            snd = self.sounds[sound_name]
            snd.set_volume(self.sfx_volume)
            snd.play()
        except Exception:
            pass

    def play_bgm(self, bgm_name, loop=True):
        if not self.enabled or not self.bgm_channel:
            return
        sound_key = f"bgm_{bgm_name}"
        if sound_key not in self.sounds:
            return
        if self.current_bgm == bgm_name and self.bgm_channel.get_busy():
            return
        
        try:
            self.current_bgm = bgm_name
            snd = self.sounds[sound_key]
            snd.set_volume(self.bgm_volume)
            self.bgm_channel.play(snd, loops=-1 if loop else 0)
        except Exception:
            pass

    def stop_bgm(self):
        if self.enabled and self.bgm_channel:
            self.bgm_channel.stop()
            self.current_bgm = None

# Global Singleton Sound Manager
sound_mgr = SoundManager()
