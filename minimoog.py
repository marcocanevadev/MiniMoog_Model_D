from pyo import *
class MiniMoog(PyoObject):
    """
    Emulated Minimoog Model D

    List of control Features:
    
    OSC 1(wf[triangle, sharktooth, sawtooth, square, wide rect, narrow rect], switch, tune, octave, volume)
    OSC 2(wf[triangle, sharktooth, sawtooth, square, wide rect, narrow rect], switch, detune, octave, volume)
    OSC 3(wf[triangle, reverse sawtooth, sawtooth, square, wide rect, narrow rect], switch, detune, octave, volume)
    Noise Generator(type[white, pink], volume)
    Filter(freq, res, contour_amount, attack, decay, sustain)
    LFO modulation(type[square, tri], mul, freq)
    Loudness Contour(attack, decay, sustain)
    Controls(pitch_bend, glide, mod[incomplete], main_volume[incomplete])

    The waveforms of the original instrument have been emulated for each Oscillator


    :Parent: :py:class:`PyoObject`

    :Args:

        empty

    >>> s = Server().boot()
    >>> s.start()
    >>> minimoog = MiniMoog()
    >>> minimoog.ctrl()
    >>> minimoog.out()
    >>> s.gui(locals())
    """

    def __init__(self ):
        super().__init__()

        self._notes = Notein(scale = 1)
        self._notes.keyboard()

        self._glide = Sig(0)
        self._bend = Sig(1)
        ### DISCARDED self._octaves = [0.25,0.5,1,2,3,4]

        self._env = MidiAdsr(self._notes["velocity"])
        self._f_env = self._env

        # ---- OSC 1, 2 and 3 ----

        self._osc1_switch = Sig(0)
        self._osc2_switch = Sig(0)
        self._osc3_switch = Sig(0)

        self._osc1_oct = Sig(0)
        self._osc2_oct = Sig(0)
        self._osc3_oct = Sig(0)

        self._osc1_wf =Sig(0)
        self._osc2_wf =Sig(0)
        self._osc3_wf =Sig(0)

        self._tune = Sig(1)
        self._osc2_det = Sig(1)
        self._osc3_det = Sig(1)

        self._t_1 = LinTable([(0,-0.7),(3272,-0.5),(3280,1),(5320,0.9),(5328,-0.9),(8191,-0.7)])
        self._t_2 = LinTable([(0,-0.7),(3600,-0.5),(3608,1),(4990,0.9),(4998,-0.9),(8191,-0.7)])

        print(type(self._notes['pitch']))
        #self._osc1_freq = VarPort(value=(((self._notes["pitch"]*4)/(2**(5-self._osc1_oct))*self._tune*self._bend)).get(), time = self._glide.get())
        #print(self._osc1_freq.get())
        self._osc1_freq = (self._notes["pitch"]*4)/(2**(5-self._osc1_oct))*self._tune*self._bend
        self._osc2_freq = (self._notes["pitch"]*4)/(2**(5-self._osc2_oct))*self._tune*self._osc2_det*self._bend
        self._osc3_freq = (self._notes["pitch"]*4)/(2**(5-self._osc3_oct))*self._tune*self._osc3_det*self._bend

        self._osc1_freq = Port(self._osc1_freq, risetime=self._glide, falltime=self._glide)
        self._osc2_freq = Port(self._osc2_freq, risetime=self._glide, falltime=self._glide)
        self._osc3_freq = Port(self._osc3_freq, risetime=self._glide, falltime=self._glide)


        self._osc1_mul =  self._env*self._osc1_switch
        self._osc2_mul =  self._env*self._osc2_switch
        self._osc3_mul =  self._env*self._osc3_switch

        self._list_1 = [
            RCOsc(freq=self._osc1_freq,mul = self._osc1_mul, sharp=0),
            Sharktooth(freq= self._osc1_freq,mul = self._osc1_mul),
            LFO(freq=self._osc1_freq,mul = self._osc1_mul, sharp=1,type = 0),
            RCOsc(freq= self._osc1_freq,mul = self._osc1_mul, sharp=1),
            Osc(self._t_1, freq = self._osc1_freq,mul =self._osc1_mul),
            Osc(self._t_2, freq = self._osc1_freq,mul = self._osc1_mul)
        ]
        self._list_2 = [
            RCOsc(self._osc2_freq,mul = self._osc2_mul, sharp=0),
            Sharktooth(self._osc2_freq,mul = self._osc2_mul),
            LFO(self._osc2_freq,mul =self._osc2_mul, sharp=1,type = 0),
            RCOsc(self._osc2_freq,mul = self._osc2_mul, sharp=1),
            Osc(self._t_1, freq = self._osc2_freq,mul = self._osc2_mul),
            Osc(self._t_2, freq = self._osc2_freq,mul = self._osc2_mul)
        ]
        self._list_3 = [
            RCOsc(self._osc3_freq,mul = self._osc3_mul, sharp=0),
            LFO(self._osc3_freq,mul = self._osc3_mul, sharp=1,type = 1),
            LFO(self._osc3_freq,mul =self._osc3_mul, sharp=1,type = 0),
            RCOsc(self._osc3_freq,mul = self._osc3_mul, sharp=1),
            Osc(self._t_1, freq = self._osc3_freq,mul = self._osc3_mul),
            Osc(self._t_2, freq = self._osc3_freq,mul = self._osc3_mul)
        ]


        
        self._osc1 = Selector(self._list_1,self._osc1_wf)
        self._osc2 = Selector(self._list_2,self._osc2_wf)
        self._osc3 = Selector(self._list_3,self._osc3_wf)


        # ---- Noise Generator ----

        self._noise_mul = Sig(0)
        self._noise_select = Sig(0)
        self._pnoise = PinkNoise(mul = self._noise_mul*self._env)
        self._wnoise = Noise(mul = self._noise_mul*self._env)
        self._noise = Selector([self._wnoise, self._pnoise], self._noise_select)


        # ---- Modulating LFO ----

        self._LFO = LFO( type = 3, add = 0.5, sharp=1)

        # ---- Filter and Mix ----

        self._contour = Sig(0)

        self._mix = Mix([self._osc1, self._osc2, self._osc3,self._noise])
        self._LP = MoogLP(self._mix, mul = 1- self._contour)
        self._LP_env = MoogLP(self._mix, freq = self._f_env*3000, mul = self._contour)
        self._LP_mix = Mix([self._LP_env,self._LP])*self._LFO
        self._out= Pan(self._LP_mix)

        #self._spec = Spectrum(self._out)
        self._scope = Scope([self._LP_env])
        self._base_objs = self._out.getBaseObjects()

    def ctrl(self):
        
        self._tune.ctrl([SLMap(1/8,5,'log','value',1,'float')],title='Tune')
        self._osc1_switch.ctrl([SLMap(0,1,'lin','value',0,'int')],title='OSC 1 switch')
        self._osc1.ctrl(title='OSC 1 Volume')
        self._osc1_oct.ctrl([SLMap(0,5,'lin','value',1,'int')],title='OSC 1 octave')
        self._osc1_wf.ctrl([SLMap(0,5,'lin','value',0,'int')],title='OSC 1 waveform [tri, shark, saw, sqr, rect, rect]')

        self._osc2_switch.ctrl([SLMap(0,1,'lin','value',0,'int')],title='OSC 2 switch')
        self._osc2.ctrl(title='OSC 2 Volume')
        self._osc2_det.ctrl([SLMap(1/8,6,'log','value',1,'float')],title='Detune')
        self._osc2_oct.ctrl([SLMap(0,5,'lin','value',1,'int')],title='OSC 2 octave')
        self._osc2_wf.ctrl([SLMap(0,5,'lin','value',0,'int')],title='OSC 2 waveform')

        self._osc3_switch.ctrl([SLMap(0,1,'lin','value',0,'int')],title='OSC 3 switch')
        self._osc3.ctrl(title='OSC 3 Volume')
        self._osc3_det.ctrl([SLMap(1/8,5,'log','value',1,'float')],title='Detune')
        self._osc3_oct.ctrl([SLMap(0,5,'lin','value',1,'int')],title='OSC 3 octave')
        self._osc3_wf.ctrl([SLMap(0,5,'lin','value',0,'int')],title='OSC 3 waveform')

        self._LFO.ctrl([SLMap(2,3,'lin','type',3,'int',dataOnly=True),SLMap(0,0.5,'lin','mul',0,'float'),SLMap(0.001,1000,'log','freq',10,'float')],title='LFO')
        self._LP.ctrl([SLMap(10,32000,'log','freq',1000,'float'),SLMap(0,10,'lin','res',0,'float')],title= 'LP filter')
        self._contour.ctrl(title='Contour Amount')
        self._f_env.ctrl([
            SLMap(0,1,'lin','attack',0.01,'float',dataOnly=True),
            SLMap(0,1,'lin','decay',0.05,'float',dataOnly=True),
            SLMap(0,1,'lin','sustain',0.7,'float',dataOnly=True)     
        ],title= 'Filter Envelope')
        self._noise_select.ctrl([SLMap(0,1,'lin','value',0,'int')], title='Noise Type (White,Pink)')
        self._noise_mul.ctrl([SLMap(0,4,'lin','value',0,'float')], title='Noise Volume')

        self._env.ctrl([
            SLMap(0,1,'lin','attack',0.01,'float',dataOnly=True),
            SLMap(0,1,'lin','decay',0.05,'float',dataOnly=True),
            SLMap(0,1,'lin','sustain',0.7,'float',dataOnly=True)     
        ],title='Loudness Contour')
        self._bend.ctrl([SLMap((2**(-1/12)),(2**(1/12)),'lin','value',1,'float')],title='Pitch Bend')
        self._glide.ctrl([SLMap(0,2,'lin','value',0,"float")])


    def play(self, dur = 0, delay =0):
        self._LP_env.play(dur, delay)
        return super().play(dur, delay)

    def stop(self):
        self._LP_env.stop()
        return super().stop()


    def out(self,chnl=0, inc= 1, dur= 0, delay= 0):
        self._LP_env.play(dur, delay)
        return super().out(chnl,inc,dur,delay)
    

class Sharktooth(PyoObject):

    """
    Generates Sharktooth waves.
    Sum of a tri and a saw wave with precise phase and amplitude.
    Divided by a factor of 6 to lower level.

    :Parent: :py:class:`PyoObject`

    :Args:

        freq : float or PyoObject, optional
            Oscillator frequency in cycles per second.
            Defaults to 1000.
        mul : float or PyoObject, optional
            Multiplies the value of the signal.
            Defaults to 1
        


    >>> s = Server().boot()
    >>> s.start()
    >>> shark = Sharktooth()
    >>> shark.ctrl()
    >>> shark.out()
    >>> s.gui(locals())

    """

    def __init__(self, freq = 1000, mul=1):
        super().__init__()
        self._amp = 0.5
        self._freq = freq
        self._phase = 0.738
        self._mul = mul/6

        self._phasor = Phasor(freq=self._freq, phase = self._phase, mul = 0.3)
        self._saw_waveform = 1 - 2 * self._phasor

        self._saw_waveform = Sig(self._saw_waveform, mul=self._amp*self._mul)
        self._tri = LFO(self._freq,type=3,mul=self._mul)
        self._mix = Mix([self._tri ,self._saw_waveform])
        self._pan = Pan(self._mix)
    
        self._base_objs = self._pan.getBaseObjects()



    def ctrl(self):
        self._phasor.ctrl()
        self._saw_waveform.ctrl()

    def play(self, dur = 0, delay =0):
        return super().play(dur, delay)

    def stop(self):
        return super().stop()


    def out(self,chnl=0, inc= 1, dur= 0, delay= 0):
        return super().out(chnl,inc,dur,delay)
    

if __name__ == "__main__":
    s = Server().boot()
    #s.setAmp(0.2)
   
    my = MiniMoog()
    my.out()
    my.ctrl()

    """
    note = Notein(scale = 1)
    note.keyboard()
    env = MidiAdsr(note['velocity'])
    aa = Sharktooth(note['pitch'], env)
    aa.ctrl()
    aa.out()
    sc = Scope(aa)
     """
    s.gui(locals())
