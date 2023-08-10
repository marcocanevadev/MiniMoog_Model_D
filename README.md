# MiniMoog_Model_D

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
 
