from pyo import *
class MiniMoog(PyoObject):
    """
    qui ci va il docc
    mponofonico anni 70 caratteristiche standard
    3 oscillatori quasi uguali con forme donda (tri, dente, rampa, square, 1/2 square, 1/4 square)
    1 generatore di rumore
    1 eventuale segnale esterno (?) self filtering (brute factor) (???)
    1 passabasso risonante 24 dB per oct
    1 LFO modulante 

    """

    def __init__(self ):
        super().__init__()

        self._notes = Notein(scale = 1)
        self._notes.keyboard()
        self._glide = Sig(0)
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

        self._tune = Sig(0)
        self._osc2_det = Sig(0)
        self._osc3_det = Sig(0)

        self._t_1 = LinTable([(0,-0.5),(3372,-0.3),(3380,1),(4096,1),(5220,1),(5228,-0.7),(8191,-0.5)])
        self._t_2 = LinTable([(0,-0.5),(3600,-0.3),(3608,1),(4096,1),(4990,1),(4998,-0.7),(8191,-0.5)])

        self._list_1 = [
            RCOsc((self._notes["pitch"]*4)/(2**(5-self._osc1_oct))+self._tune,mul = self._env*self._osc1_switch, sharp=0),
            Sharktooth((self._notes["pitch"]*4)/(2**(5-self._osc1_oct))+self._tune,mul = self._env*self._osc1_switch),
            LFO((self._notes["pitch"]*4)/(2**(5-self._osc1_oct))+self._tune,mul = self._env*self._osc1_switch, sharp=1,type = 0),
            RCOsc((self._notes["pitch"]*4)/(2**(5-self._osc1_oct))+self._tune,mul = self._env*self._osc1_switch, sharp=1),
            Osc(self._t_1, freq = (self._notes["pitch"]*4)/(2**(5-self._osc1_oct))+self._tune,mul = self._env*self._osc1_switch),
            Osc(self._t_2, freq = (self._notes["pitch"]*4)/(2**(5-self._osc1_oct))+self._tune,mul = self._env*self._osc1_switch)
        ]
        self._list_2 = [
            RCOsc((self._notes["pitch"]*4)/(2**(5-self._osc2_oct))+self._osc2_det+self._tune,mul = self._env*self._osc2_switch, sharp=0),
            Sharktooth((self._notes["pitch"]*4)/(2**(5-self._osc2_oct))+self._osc2_det+self._tune,mul = self._env*self._osc2_switch),
            LFO((self._notes["pitch"]*4)/(2**(5-self._osc2_oct))+self._osc2_det+self._tune,mul = self._env*self._osc2_switch, sharp=1,type = 0),
            RCOsc((self._notes["pitch"]*4)/(2**(5-self._osc2_oct))+self._osc2_det+self._tune,mul = self._env*self._osc2_switch, sharp=1),
            Osc(self._t_1, freq = (self._notes["pitch"]*4)/(2**(5-self._osc2_oct))+self._osc2_det+self._tune,mul = self._env*self._osc2_switch),
            Osc(self._t_2, freq = (self._notes["pitch"]*4)/(2**(5-self._osc2_oct))+self._osc2_det+self._tune,mul = self._env*self._osc2_switch)
        ]
        self._list_3 = [
            RCOsc((self._notes["pitch"]*4)/(2**(5-self._osc3_oct))+self._osc3_det+self._tune,mul = self._env*self._osc3_switch, sharp=0),
            LFO((self._notes["pitch"]*4)/(2**(5-self._osc3_oct))+self._osc3_det+self._tune,mul = self._env*self._osc3_switch, sharp=1,type = 1),
            LFO((self._notes["pitch"]*4)/(2**(5-self._osc3_oct))+self._osc3_det+self._tune,mul = self._env*self._osc3_switch, sharp=1,type = 0),
            RCOsc((self._notes["pitch"]*4)/(2**(5-self._osc3_oct))+self._osc3_det+self._tune,mul = self._env*self._osc3_switch, sharp=1),
            Osc(self._t_1, freq = (self._notes["pitch"]*4)/(2**(5-self._osc3_oct))+self._osc3_det+self._tune,mul = self._env*self._osc3_switch),
            Osc(self._t_2, freq = (self._notes["pitch"]*4)/(2**(5-self._osc3_oct))+self._osc3_det+self._tune,mul = self._env*self._osc3_switch)
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
        self._scope = Scope([self._out])
        self._base_objs = self._out.getBaseObjects()

    def ctrl(self):
        
        self._tune.ctrl([SLMap(-5,5,'lin','value',0,'float')],title='Tune')
        self._osc1_switch.ctrl([SLMap(0,1,'lin','value',0,'int')],title='OSC 1 switch')
        self._osc1.ctrl(title='OSC 1 Volume')
        self._osc1_oct.ctrl([SLMap(0,5,'lin','value',1,'int')],title='OSC 1 octave')
        self._osc1_wf.ctrl([SLMap(0,5,'lin','value',0,'int')],title='OSC 1 waveform')

        self._osc2_switch.ctrl([SLMap(0,1,'lin','value',0,'int')],title='OSC 2 switch')
        self._osc2.ctrl(title='OSC 2 Volume')
        self._osc2_det.ctrl([SLMap(-5,5,'lin','value',0,'float')],title='Detune')
        self._osc2_oct.ctrl([SLMap(0,5,'lin','value',1,'int')],title='OSC 2 octave')
        self._osc2_wf.ctrl([SLMap(0,5,'lin','value',0,'int')],title='OSC 2 waveform')

        self._osc3_switch.ctrl([SLMap(0,1,'lin','value',0,'int')],title='OSC 3 switch')
        self._osc3.ctrl(title='OSC 3 Volume')
        self._osc3_det.ctrl([SLMap(-5,5,'lin','value',0,'float')],title='Detune')
        self._osc3_oct.ctrl([SLMap(0,5,'lin','value',1,'int')],title='OSC 3 octave')
        self._osc3_wf.ctrl([SLMap(0,5,'lin','value',0,'int')],title='OSC 3 waveform')

        self._LFO.ctrl([SLMap(2,3,'lin','type',3,'int',dataOnly=True),SLMap(0,0.5,'lin','mul',0,'float'),SLMap(0.001,1000,'log','freq',10,'float')],title='LFO')
        self._LP.ctrl(title= 'LP filter')
        self._contour.ctrl(title='Contour Amount')
        self._f_env.ctrl(title= 'Filter Envelope')
        self._noise_select.ctrl([SLMap(0,1,'lin','value',0,'int')], title='Noise Type (White,Pink)')
        self._noise_mul.ctrl([SLMap(0,4,'lin','value',0,'float')], title='Noise Mul')

        self._env.ctrl(title='Loudness Contour')
        #self._glide.ctrl([SLMap(0,100,'lin','value',0,"float")])


    def play(self, dur = 0, delay =0):
        return super().play(dur, delay)

    def stop(self):
        return super().stop()


    def out(self,chnl=0, inc= 1, dur= 0, delay= 0):
        return super().out(chnl,inc,dur,delay)
    

class Sharktooth(PyoObject):

    def __init__(self, freq, mul):
        super().__init__()
        self._amp = 0.5
        self._freq = freq
        self._phase = 0.750
        self._mul = mul/6

        self._phasor = Phasor(freq=self._freq, phase = self._phase, mul = 0.292)
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
