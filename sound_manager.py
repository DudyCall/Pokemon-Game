"""
sound_manager.py - Procedural warm acoustic chiptune sound generator and music player.
Generates warm, authentic retro sounds and multi-voice polyphonic music directly in memory
with low-pass filtering, gentle attack/decay envelopes, and balanced volumes to eliminate harshness.
"""
import io
import math
import wave
import struct
import random
import pygame

# Musical Note Frequencies (Hz)
NOTES = {
    "Bb1": 58.27, "C2": 65.41, "D2": 73.42, "E2": 82.41, "F2": 87.31, "G2": 98.00, "A2": 110.00, "Bb2": 116.54, "B2": 123.47,
    "C3": 130.81, "D3": 146.83, "Eb3": 155.56, "E3": 164.81, "F3": 174.61, "G3": 196.00, "A3": 220.00, "Bb3": 233.08, "B3": 246.94,
    "C4": 261.63, "D4": 293.66, "Eb4": 311.13, "E4": 329.63, "F4": 349.23, "F#4": 369.99, "G4": 392.00, "Ab4": 415.30, "A4": 440.00, "Bb4": 466.16, "B4": 493.88,
    "C5": 523.25, "D5": 587.33, "Eb5": 622.25, "E5": 659.25, "F5": 698.46, "F#5": 739.99, "G5": 783.99, "Ab5": 830.61, "A5": 880.00, "Bb5": 932.33, "B5": 987.77,
    "C6": 1046.50, "D6": 1174.66, "E6": 1318.51, "G6": 1567.98
}


class SoundManager:
    def __init__(self):
        self.enabled = True
        self.sounds = {}
        self.current_bgm = None
        self.bgm_channel = None
        # Calibrated default volumes (non-fatiguing, comfortable listening levels)
        self.sfx_volume = 0.28
        self.bgm_volume = 0.18
        
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.bgm_channel = pygame.mixer.Channel(0)
            self.generate_all_sounds()
        except Exception as e:
            print(f"Audio init notice: {e}")
            self.enabled = False

    def set_sfx_volume(self, volume):
        """Sets master SFX volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, float(volume)))

    def set_bgm_volume(self, volume):
        """Sets master BGM volume (0.0 to 1.0) and adjusts active channel."""
        self.bgm_volume = max(0.0, min(1.0, float(volume)))
        if self.bgm_channel:
            self.bgm_channel.set_volume(self.bgm_volume)

    def _create_wav(self, samples, sample_rate=44100):
        """Converts floating point sample list (-1.0 to 1.0) into a pygame.mixer.Sound object."""
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav_file:
            wav_file.setnchannels(1) # mono
            wav_file.setsampwidth(2) # 16-bit
            wav_file.setframerate(sample_rate)
            
            raw_frames = bytearray()
            for s in samples:
                val = max(-1.0, min(1.0, s))
                int_val = int(val * 32767.0)
                raw_frames.extend(struct.pack('<h', int_val))
            wav_file.writeframes(raw_frames)
            
        buf.seek(0)
        return pygame.mixer.Sound(buf)

    def _low_pass_filter(self, samples, cutoff_freq=3200, sample_rate=44100):
        """
        1-pole IIR low-pass filter to eliminate harsh digital treble and buzzing.
        Transforms raw square/pulse waveforms into warm, smooth analog/GBA tones.
        """
        if not samples:
            return []
        rc = 1.0 / (2.0 * math.pi * cutoff_freq)
        dt = 1.0 / sample_rate
        alpha = dt / (rc + dt)
        out = [0.0] * len(samples)
        val = 0.0
        for i in range(len(samples)):
            val += alpha * (samples[i] - val)
            out[i] = val
        return out

    def _mix_tracks(self, *tracks):
        """Mixes multiple float sample lists together with automatic normalization preventing clipping."""
        max_len = max(len(t) for t in tracks)
        mixed = [0.0] * max_len
        for track in tracks:
            for i, val in enumerate(track):
                mixed[i] += val
        peak = max((abs(x) for x in mixed), default=1.0)
        if peak > 0.35:
            scale = 0.32 / peak
            mixed = [x * scale for x in mixed]
        return mixed

    def _flute_tone(self, freq, duration, volume=0.20, sample_rate=44100, cutoff=3600):
        """Smooth, warm flute/bell tone (sine fundamental + 2nd harmonic) with gentle ADSR envelope."""
        if freq <= 0:
            return [0.0] * int(duration * sample_rate)
        num_samples = int(duration * sample_rate)
        samples = []
        att = int(min(0.015, duration * 0.15) * sample_rate)
        rel = int(min(0.035, duration * 0.25) * sample_rate)
        for i in range(num_samples):
            t = i / sample_rate
            v = (math.sin(2.0 * math.pi * freq * t) * 0.78 +
                 math.sin(4.0 * math.pi * freq * t) * 0.16 +
                 math.sin(6.0 * math.pi * freq * t) * 0.06) * volume
            if i < att:
                env = i / max(1, att)
            elif i > num_samples - rel:
                env = (num_samples - i) / max(1, rel)
            else:
                env = 1.0 - (i / num_samples) * 0.12
            samples.append(v * env)
        return self._low_pass_filter(samples, cutoff_freq=cutoff, sample_rate=sample_rate)

    def _bass_tone(self, freq, duration, volume=0.18, sample_rate=44100, cutoff=850):
        """Warm, rounded deep bass tone (triangle + sub-sine blend) with low cutoff filter."""
        if freq <= 0:
            return [0.0] * int(duration * sample_rate)
        num_samples = int(duration * sample_rate)
        samples = []
        att = int(min(0.012, duration * 0.15) * sample_rate)
        rel = int(min(0.030, duration * 0.25) * sample_rate)
        period = sample_rate / max(1.0, freq)
        for i in range(num_samples):
            t = i / sample_rate
            phase = (i % period) / period
            tri = abs(phase * 4.0 - 2.0) - 1.0
            sine = math.sin(2.0 * math.pi * freq * t)
            v = (tri * 0.55 + sine * 0.45) * volume
            if i < att:
                env = i / max(1, att)
            elif i > num_samples - rel:
                env = (num_samples - i) / max(1, rel)
            else:
                env = 1.0 - (i / num_samples) * 0.18
            samples.append(v * env)
        return self._low_pass_filter(samples, cutoff_freq=cutoff, sample_rate=sample_rate)

    def _pulse_tone(self, freq, duration, duty=0.35, volume=0.18, sample_rate=44100, cutoff=2600):
        """Smooth, filtered pulse wave for authentic retro chiptune without harshness."""
        if freq <= 0:
            return [0.0] * int(duration * sample_rate)
        num_samples = int(duration * sample_rate)
        samples = []
        att = int(min(0.008, duration * 0.1) * sample_rate)
        rel = int(min(0.025, duration * 0.2) * sample_rate)
        period = sample_rate / max(1.0, freq)
        for i in range(num_samples):
            phase = (i % period) / period
            v = volume if phase < duty else -volume
            if i < att:
                env = i / max(1, att)
            elif i > num_samples - rel:
                env = (num_samples - i) / max(1, rel)
            else:
                env = 1.0 - (i / num_samples) * 0.15
            samples.append(v * env)
        return self._low_pass_filter(samples, cutoff_freq=cutoff, sample_rate=sample_rate)

    def _soft_click(self, freq=480, duration=0.024, volume=0.14, sample_rate=44100):
        """Soft, subtle wooden click for pleasant, non-annoying menu cursor navigation."""
        num_samples = int(duration * sample_rate)
        samples = []
        for i in range(num_samples):
            t = i / sample_rate
            env = math.exp(-t * 90.0)
            v = math.sin(2.0 * math.pi * freq * t) * volume * env
            samples.append(v)
        return self._low_pass_filter(samples, cutoff_freq=2400, sample_rate=sample_rate)

    def _soft_noise(self, duration, volume=0.07, decay_exp=3.5, sample_rate=44100, cutoff=2800):
        """Soft, filtered noise burst for gentle, organic footsteps and prop rustling."""
        num_samples = int(duration * sample_rate)
        samples = []
        for i in range(num_samples):
            t = i / num_samples
            env = (1.0 - t) ** decay_exp
            samples.append((random.random() * 2.0 - 1.0) * volume * env)
        return self._low_pass_filter(samples, cutoff_freq=cutoff, sample_rate=sample_rate)

    def _freq_sweep(self, start_f, end_f, duration, volume=0.20, wave_type="sine", sample_rate=44100, cutoff=3200):
        """Smooth frequency sweep for whooshes, impacts, and sound effects."""
        num_samples = int(duration * sample_rate)
        samples = []
        phase = 0.0
        for i in range(num_samples):
            t = i / num_samples
            freq = start_f + (end_f - start_f) * t
            phase += 2.0 * math.pi * freq / sample_rate
            if wave_type == "sine":
                v = math.sin(phase) * volume
            elif wave_type == "triangle":
                v = volume * (2.0 / math.pi) * math.asin(math.sin(phase))
            else:
                v = volume if (phase % (2.0 * math.pi)) < math.pi else -volume
            env = 1.0 - t * 0.7
            samples.append(v * env)
        return self._low_pass_filter(samples, cutoff_freq=cutoff, sample_rate=sample_rate)

    def _build_melody(self, notes, tone_fn, volume=0.20, SR=44100):
        """Builds a continuous audio track from a list of (freq, duration) tuples."""
        res = []
        for freq, dur in notes:
            res.extend(tone_fn(freq, dur, volume=volume, sample_rate=SR))
        return res

    # Backward compatibility helpers
    def _square_wave(self, freq, duration, duty=0.5, sample_rate=44100, volume=0.20):
        return self._pulse_tone(freq, duration, duty=duty, volume=volume, sample_rate=sample_rate)

    def _noise_burst(self, duration, sample_rate=44100, volume=0.15, decay_exp=2.0):
        return self._soft_noise(duration, volume=volume, decay_exp=decay_exp, sample_rate=sample_rate)

    def _create_melody(self, notes_freq_duration, sample_rate=44100, wave_type="square", volume=0.20):
        notes = [(n[0], n[1]) for n in notes_freq_duration]
        return self._build_melody(notes, self._pulse_tone if wave_type == "square" else self._flute_tone, volume=volume, SR=sample_rate)

    def _warm_lead_tone(self, freq, duration, volume=0.10, sample_rate=44100, cutoff=1500):
        """Warm, mellow synth lead with rounded harmonics, low cutoff, and smooth envelope."""
        if freq <= 0:
            return [0.0] * int(duration * sample_rate)
        num_samples = int(duration * sample_rate)
        samples = []
        att = int(min(0.018, duration * 0.15) * sample_rate)
        rel = int(min(0.035, duration * 0.25) * sample_rate)
        period = sample_rate / max(1.0, freq)
        for i in range(num_samples):
            t = i / sample_rate
            phase = (i % period) / period
            tri = abs(phase * 4.0 - 2.0) - 1.0
            sine = math.sin(2.0 * math.pi * freq * t)
            sine2 = math.sin(4.0 * math.pi * freq * t)
            v = (tri * 0.40 + sine * 0.50 + sine2 * 0.10) * volume
            if i < att:
                env = i / max(1, att)
            elif i > num_samples - rel:
                env = (num_samples - i) / max(1, rel)
            else:
                env = 1.0 - (i / num_samples) * 0.15
            samples.append(v * env)
        return self._low_pass_filter(samples, cutoff_freq=cutoff, sample_rate=sample_rate)

    def _soft_bass_tone(self, freq, duration, volume=0.08, sample_rate=44100, cutoff=550):
        """Deep, rounded warm bass filtered low at 550Hz so it never booms or buzzes."""
        if freq <= 0:
            return [0.0] * int(duration * sample_rate)
        num_samples = int(duration * sample_rate)
        samples = []
        att = int(min(0.015, duration * 0.15) * sample_rate)
        rel = int(min(0.030, duration * 0.25) * sample_rate)
        for i in range(num_samples):
            t = i / sample_rate
            v = math.sin(2.0 * math.pi * freq * t) * volume
            if i < att:
                env = i / max(1, att)
            elif i > num_samples - rel:
                env = (num_samples - i) / max(1, rel)
            else:
                env = 1.0 - (i / num_samples) * 0.12
            samples.append(v * env)
        return self._low_pass_filter(samples, cutoff_freq=cutoff, sample_rate=sample_rate)

    def generate_all_sounds(self):
        """Generates all procedural game sound effects and polyphonic BGM tracks directly into memory."""
        if not self.enabled:
            return
        
        SR = 44100
        
        # 1. Menu cursor select (Quiet, pleasant wooden tap - never annoying)
        self.sounds["select"] = self._create_wav(self._soft_click(480, 0.024, volume=0.14, sample_rate=SR), SR)
        
        # 2. Confirm / Enter (Gentle harmonic bell chime: C5 -> G5)
        m_conf = self._build_melody([(NOTES["C5"], 0.05), (NOTES["G5"], 0.08)], self._flute_tone, volume=0.18, SR=SR)
        self.sounds["confirm"] = self._create_wav(m_conf, SR)
        
        # 3. Cancel (Soft mellow downward dip: E4 -> C4)
        m_canc = self._build_melody([(NOTES["E4"], 0.04), (NOTES["C4"], 0.07)], self._flute_tone, volume=0.16, SR=SR)
        self.sounds["cancel"] = self._create_wav(m_canc, SR)
        
        # 4. Tackle / Hit impact (Punchy, bass-weighted thump instead of harsh static)
        thump = self._freq_sweep(160, 45, 0.10, volume=0.25, wave_type="triangle", sample_rate=SR, cutoff=800)
        noise_h = self._soft_noise(0.10, volume=0.14, decay_exp=4.0, sample_rate=SR, cutoff=1200)
        self.sounds["hit"] = self._create_wav(self._mix_tracks(thump, noise_h), SR)
        
        # 5. Super effective hit (Resonant low impact with deep bass punch)
        thump_s = self._freq_sweep(240, 35, 0.22, volume=0.30, wave_type="triangle", sample_rate=SR, cutoff=900)
        noise_s = self._soft_noise(0.22, volume=0.18, decay_exp=2.8, sample_rate=SR, cutoff=1400)
        self.sounds["super_hit"] = self._create_wav(self._mix_tracks(thump_s, noise_s), SR)
        
        # 6. Fire move (Warm roaring flame whoosh)
        s_fire = self._soft_noise(0.28, volume=0.18, decay_exp=1.5, sample_rate=SR, cutoff=1600)
        self.sounds["fire"] = self._create_wav(s_fire, SR)
        
        # 7. Water move (Gentle bubbly water splash)
        s_water = self._freq_sweep(280, 680, 0.16, volume=0.18, wave_type="triangle", sample_rate=SR, cutoff=2400)
        self.sounds["water"] = self._create_wav(s_water, SR)
        
        # 8. Electric move (Crisp modulated static zap, low-pass filtered)
        s_elec = []
        for i in range(int(0.20 * SR)):
            t = i / SR
            f = 420 + 180 * math.sin(2.0 * math.pi * 32 * t)
            v = (0.16 if (i % (SR / f)) < (SR / f * 0.4) else -0.16) + (random.random() * 2 - 1) * 0.06
            s_elec.append(v * (1.0 - t / 0.20))
        self.sounds["electric"] = self._create_wav(self._low_pass_filter(s_elec, 2400, SR), SR)
        
        # 9. Grass move (Whistling razor leaf whoosh)
        s_grass = self._freq_sweep(650, 240, 0.14, volume=0.18, wave_type="triangle", sample_rate=SR, cutoff=2200)
        self.sounds["grass"] = self._create_wav(s_grass, SR)
        
        # 10. Pokeball throw (Smooth aerodynamic whoosh)
        self.sounds["throw"] = self._create_wav(self._freq_sweep(260, 600, 0.15, volume=0.16, wave_type="sine", sample_rate=SR), SR)
        
        # 11. Pokeball shake (Gentle wooden wobble)
        self.sounds["ball_shake"] = self._create_wav(self._build_melody([(460, 0.04), (390, 0.05)], self._flute_tone, volume=0.18, SR=SR), SR)
        
        # 12. Catch success chime (Harmonic 4-note bell chime)
        m_catch = self._build_melody([(NOTES["C5"], 0.08), (NOTES["E5"], 0.08), (NOTES["G5"], 0.08), (NOTES["C6"], 0.28)], self._flute_tone, volume=0.22, SR=SR)
        self.sounds["catch_success"] = self._create_wav(m_catch, SR)
        
        # 13. Level Up Fanfare (Celebratory 6-note fanfare)
        m_lvl = self._build_melody([
            (NOTES["C5"], 0.07), (NOTES["D5"], 0.07), (NOTES["E5"], 0.07),
            (NOTES["G5"], 0.10), (NOTES["A5"], 0.10), (NOTES["C6"], 0.30)
        ], self._flute_tone, volume=0.22, SR=SR)
        self.sounds["level_up"] = self._create_wav(m_lvl, SR)
        
        # 14. Pokemon Faint (Gentle downward sigh sweep)
        self.sounds["faint"] = self._create_wav(self._freq_sweep(360, 90, 0.35, volume=0.18, wave_type="triangle", sample_rate=SR, cutoff=1400), SR)
        
        # 15. Heal Chime (Classic Pokémon Center 4-note warm chime)
        m_heal = self._build_melody([(NOTES["E5"], 0.10), (NOTES["G5"], 0.10), (NOTES["B5"], 0.10), (NOTES["E6"], 0.24)], self._flute_tone, volume=0.22, SR=SR)
        self.sounds["heal"] = self._create_wav(m_heal, SR)
        
        # 16. Wild Encounter intro (Dramatic encounter chords instead of harsh siren)
        m_enc_lead = self._build_melody([(NOTES["G5"], 0.05), (NOTES["F5"], 0.05), (NOTES["G5"], 0.05), (NOTES["Ab5"], 0.05), (NOTES["G5"], 0.12)], self._warm_lead_tone, volume=0.12, SR=SR)
        m_enc_bass = self._build_melody([(NOTES["C3"], 0.15), (NOTES["G2"], 0.17)], self._soft_bass_tone, volume=0.10, SR=SR)
        self.sounds["wild_encounter"] = self._create_wav(self._mix_tracks(m_enc_lead, m_enc_bass), SR)
        
        # Footstep SFX (Extremely gentle, quiet, atmospheric - no annoying static bursts!)
        self.sounds["rustle"] = self._create_wav(self._soft_noise(0.045, volume=0.06, decay_exp=4.0, sample_rate=SR, cutoff=2200), SR)
        s_chime = self._build_melody([(NOTES["G5"], 0.02), (NOTES["C6"], 0.03)], self._flute_tone, volume=0.05, SR=SR)
        self.sounds["flower_step"] = self._create_wav(self._mix_tracks(self._soft_noise(0.04, volume=0.04, sample_rate=SR), s_chime), SR)
        self.sounds["leaves_step"] = self._create_wav(self._soft_noise(0.05, volume=0.07, decay_exp=3.2, sample_rate=SR, cutoff=2400), SR)
        s_gravel = self._mix_tracks(self._soft_noise(0.05, volume=0.07, decay_exp=3.5, sample_rate=SR, cutoff=1600),
                                    self._freq_sweep(140, 50, 0.05, volume=0.08, wave_type="triangle", sample_rate=SR, cutoff=700))
        self.sounds["rubble_step"] = self._create_wav(s_gravel, SR)
        self.sounds["snow_step"] = self._create_wav(self._soft_noise(0.06, volume=0.05, decay_exp=4.5, sample_rate=SR, cutoff=1400), SR)
        self.sounds["mist_step"] = self._create_wav(self._freq_sweep(520, 360, 0.08, volume=0.06, wave_type="sine", sample_rate=SR, cutoff=1800), SR)
        self.sounds["ash_step"] = self._create_wav(self._soft_noise(0.05, volume=0.06, decay_exp=3.5, sample_rate=SR, cutoff=2000), SR)
        self.sounds["mud_step"] = self._create_wav(self._mix_tracks(self._freq_sweep(160, 420, 0.06, volume=0.08, wave_type="triangle", sample_rate=SR),
                                                                    self._soft_noise(0.05, volume=0.05, sample_rate=SR)), SR)
        s_spark = self._low_pass_filter([(0.07 if (i % 80 < 35) else -0.07) + (random.random() * 2 - 1) * 0.04 for i in range(int(0.04 * SR))], 2200, SR)
        self.sounds["spark_step"] = self._create_wav(s_spark, SR)

        # Generate Polyphonic BGM tracks
        self._generate_bgm_tracks(SR)

    def _generate_bgm_tracks(self, SR=44100):
        """Generates rich 3-voice polyphonic background music tracks with warm flute leads, harmony chords, and bass."""
        # -------------------------------------------------------------
        # 1. Peaceful Town Theme ("Pallet Town / Littleroot" inspired)
        # -------------------------------------------------------------
        lead_town = [
            (NOTES["E5"], 0.5), (NOTES["G5"], 0.25), (NOTES["A5"], 0.25),
            (NOTES["G5"], 0.5), (NOTES["E5"], 0.25), (NOTES["D5"], 0.25),
            (NOTES["C5"], 0.5), (NOTES["D5"], 0.25), (NOTES["E5"], 0.25),
            (NOTES["D5"], 0.75), (0, 0.25),
            (NOTES["E5"], 0.5), (NOTES["G5"], 0.25), (NOTES["C6"], 0.25),
            (NOTES["B5"], 0.5), (NOTES["A5"], 0.25), (NOTES["G5"], 0.25),
            (NOTES["A5"], 0.25), (NOTES["G5"], 0.25), (NOTES["F5"], 0.25), (NOTES["E5"], 0.25),
            (NOTES["D5"], 0.5), (NOTES["C5"], 0.5)
        ]
        chords_town = [
            (NOTES["C4"], 0.25), (NOTES["E4"], 0.25), (NOTES["G4"], 0.25), (NOTES["E4"], 0.25),
            (NOTES["B3"], 0.25), (NOTES["E4"], 0.25), (NOTES["G4"], 0.25), (NOTES["E4"], 0.25),
            (NOTES["A3"], 0.25), (NOTES["C4"], 0.25), (NOTES["F4"], 0.25), (NOTES["C4"], 0.25),
            (NOTES["B3"], 0.25), (NOTES["D4"], 0.25), (NOTES["G4"], 0.25), (NOTES["D4"], 0.25),
            (NOTES["A3"], 0.25), (NOTES["C4"], 0.25), (NOTES["E4"], 0.25), (NOTES["C4"], 0.25),
            (NOTES["G3"], 0.25), (NOTES["B3"], 0.25), (NOTES["E4"], 0.25), (NOTES["B3"], 0.25),
            (NOTES["F3"], 0.25), (NOTES["A3"], 0.25), (NOTES["C4"], 0.25), (NOTES["A3"], 0.25),
            (NOTES["G3"], 0.25), (NOTES["B3"], 0.25), (NOTES["D4"], 0.25), (NOTES["G3"], 0.25)
        ]
        bass_town = [
            (NOTES["C2"], 0.5), (NOTES["G2"], 0.5),
            (NOTES["E2"], 0.5), (NOTES["B2"], 0.5),
            (NOTES["F2"], 0.5), (NOTES["C3"], 0.5),
            (NOTES["G2"], 0.5), (NOTES["D3"], 0.5),
            (NOTES["A2"], 0.5), (NOTES["E3"], 0.5),
            (NOTES["E2"], 0.5), (NOTES["B2"], 0.5),
            (NOTES["F2"], 0.5), (NOTES["C3"], 0.5),
            (NOTES["G2"], 0.5), (NOTES["G2"], 0.5)
        ]
        t1 = self._build_melody(lead_town, self._flute_tone, volume=0.18, SR=SR)
        t2 = self._build_melody(chords_town, self._flute_tone, volume=0.08, SR=SR)
        t3 = self._build_melody(bass_town, self._bass_tone, volume=0.15, SR=SR)
        self.sounds["bgm_town"] = self._create_wav(self._mix_tracks(t1, t2, t3), SR)

        # -------------------------------------------------------------
        # 2. Warm, Melodic Battle Theme (Extended 16-Bar Progression in D Minor)
        # -------------------------------------------------------------
        B = 0.22  # 8th note duration
        Q = 0.44  # Quarter note duration
        H = 0.88  # Half note duration

        lead_battle = [
            # Phrase 1: Opening motif
            (NOTES["D4"], B), (NOTES["F4"], B), (NOTES["G4"], B), (NOTES["A4"], B),
            (NOTES["D5"], Q), (NOTES["C5"], B), (NOTES["A4"], B),
            (NOTES["F4"], B), (NOTES["G4"], B), (NOTES["A4"], Q),
            (NOTES["G4"], B), (NOTES["F4"], B), (NOTES["E4"], Q),
            # Phrase 2: Melodic ascent
            (NOTES["D4"], B), (NOTES["F4"], B), (NOTES["A4"], B), (NOTES["D5"], B),
            (NOTES["F5"], Q), (NOTES["E5"], B), (NOTES["D5"], B),
            (NOTES["C5"], B), (NOTES["D5"], B), (NOTES["E5"], Q),
            (NOTES["C5"], Q), (NOTES["A4"], Q),
            # Phrase 3: Tense counter-cadence (Bb - C - Dm)
            (NOTES["Bb4"], B), (NOTES["C5"], B), (NOTES["D5"], Q),
            (NOTES["C5"], B), (NOTES["Bb4"], B), (NOTES["A4"], Q),
            (NOTES["G4"], B), (NOTES["A4"], B), (NOTES["Bb4"], Q),
            (NOTES["A4"], B), (NOTES["G4"], B), (NOTES["F4"], Q),
            # Phrase 4: Climactic resolution to Dm
            (NOTES["E4"], B), (NOTES["F4"], B), (NOTES["G4"], B), (NOTES["A4"], B),
            (NOTES["D5"], Q), (NOTES["A4"], Q),
            (NOTES["F4"], B), (NOTES["E4"], B), (NOTES["D4"], Q),
            (NOTES["D4"], H)
        ]

        bass_battle = [
            # Phrase 1 (Dm - C - Dm - A)
            (NOTES["D2"], B), (NOTES["D2"], B), (NOTES["F2"], B), (NOTES["A2"], B),
            (NOTES["C2"], B), (NOTES["C2"], B), (NOTES["E2"], B), (NOTES["G2"], B),
            (NOTES["D2"], B), (NOTES["D2"], B), (NOTES["F2"], B), (NOTES["A2"], B),
            (NOTES["A2"], B), (NOTES["A2"], B), (NOTES["C3"], B), (NOTES["E3"], B),
            # Phrase 2 (Dm - Bb - C - Am)
            (NOTES["D2"], B), (NOTES["D2"], B), (NOTES["F2"], B), (NOTES["A2"], B),
            (NOTES["Bb2"], B), (NOTES["Bb2"], B), (NOTES["D3"], B), (NOTES["F3"], B),
            (NOTES["C2"], B), (NOTES["C2"], B), (NOTES["E2"], B), (NOTES["G2"], B),
            (NOTES["A2"], B), (NOTES["A2"], B), (NOTES["C3"], B), (NOTES["E3"], B),
            # Phrase 3 (Bb - C - Dm - G)
            (NOTES["Bb2"], B), (NOTES["Bb2"], B), (NOTES["D3"], B), (NOTES["F3"], B),
            (NOTES["C2"], B), (NOTES["C2"], B), (NOTES["E2"], B), (NOTES["G2"], B),
            (NOTES["D2"], B), (NOTES["D2"], B), (NOTES["F2"], B), (NOTES["A2"], B),
            (NOTES["G2"], B), (NOTES["G2"], B), (NOTES["Bb2"], B), (NOTES["D3"], B),
            # Phrase 4 (Gm - A - Dm - Dm)
            (NOTES["G2"], B), (NOTES["G2"], B), (NOTES["Bb2"], B), (NOTES["D3"], B),
            (NOTES["A2"], B), (NOTES["A2"], B), (NOTES["C3"], B), (NOTES["E3"], B),
            (NOTES["D2"], B), (NOTES["D2"], B), (NOTES["F2"], B), (NOTES["A2"], B),
            (NOTES["D2"], H)
        ]

        chords_battle = [
            # Phrase 1
            (NOTES["D3"], Q), (NOTES["F3"], Q),
            (NOTES["C3"], Q), (NOTES["E3"], Q),
            (NOTES["D3"], Q), (NOTES["F3"], Q),
            (NOTES["A3"], Q), (NOTES["C4"], Q),
            # Phrase 2
            (NOTES["D3"], Q), (NOTES["F3"], Q),
            (NOTES["Bb3"], Q), (NOTES["D4"], Q),
            (NOTES["C3"], Q), (NOTES["E3"], Q),
            (NOTES["A3"], Q), (NOTES["C4"], Q),
            # Phrase 3
            (NOTES["Bb3"], Q), (NOTES["D4"], Q),
            (NOTES["C3"], Q), (NOTES["E3"], Q),
            (NOTES["D3"], Q), (NOTES["F3"], Q),
            (NOTES["G3"], Q), (NOTES["Bb3"], Q),
            # Phrase 4
            (NOTES["G3"], Q), (NOTES["Bb3"], Q),
            (NOTES["A3"], Q), (NOTES["E4"], Q),
            (NOTES["D3"], Q), (NOTES["F3"], Q),
            (NOTES["D3"], H)
        ]

        b1 = self._build_melody(lead_battle, self._warm_lead_tone, volume=0.10, SR=SR)
        b2 = self._build_melody(bass_battle, self._soft_bass_tone, volume=0.08, SR=SR)
        b3 = self._build_melody(chords_battle, self._flute_tone, volume=0.04, SR=SR)
        self.sounds["bgm_battle"] = self._create_wav(self._mix_tracks(b1, b2, b3), SR)

        # -------------------------------------------------------------
        # 3. Victory Theme
        # -------------------------------------------------------------
        lead_vic = [
            (NOTES["C5"], 0.12), (NOTES["E5"], 0.12), (NOTES["G5"], 0.12), (NOTES["C6"], 0.28),
            (NOTES["A5"], 0.14), (NOTES["C6"], 0.42),
            (NOTES["B5"], 0.14), (NOTES["G5"], 0.14), (NOTES["C6"], 0.50)
        ]
        bass_vic = [
            (NOTES["C3"], 0.36), (NOTES["E3"], 0.28),
            (NOTES["F3"], 0.14), (NOTES["A3"], 0.42),
            (NOTES["G3"], 0.28), (NOTES["C3"], 0.50)
        ]
        v1 = self._build_melody(lead_vic, self._flute_tone, volume=0.16, SR=SR)
        v2 = self._build_melody(bass_vic, self._bass_tone, volume=0.12, SR=SR)
        self.sounds["bgm_victory"] = self._create_wav(self._mix_tracks(v1, v2), SR)

    def play_sfx(self, sound_name):
        """Plays a sound effect with calibrated volume."""
        if not self.enabled or sound_name not in self.sounds:
            return
        try:
            snd = self.sounds[sound_name]
            snd.set_volume(self.sfx_volume)
            snd.play()
        except Exception:
            pass

    def play_bgm(self, bgm_name, loop=True):
        """Plays a background music track, looping smoothly."""
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
            # Balanced playback volume (battle theme plays gently so SFX remain clear)
            vol = self.bgm_volume * 0.80 if bgm_name == "battle" else self.bgm_volume
            snd.set_volume(vol)
            self.bgm_channel.play(snd, loops=-1 if loop else 0)
        except Exception:
            pass

    def stop_bgm(self):
        """Stops active background music playback."""
        if self.enabled and self.bgm_channel:
            self.bgm_channel.stop()
            self.current_bgm = None


# Global Singleton Sound Manager
sound_mgr = SoundManager()
