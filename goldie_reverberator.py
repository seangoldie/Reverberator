'''Basic Schroeder Reverberator 
Author: Sean Goldie, smg8196@nyu.edu
Written for Advanced Musical Acoustics Summer 2021, NYU

Call the class SchroederReverberator() to process audio signals as numpy arrays.
'''

import numpy as np
from IPython.display import Audio
import soundfile as sf
import scipy.signal as sp


class CombFilter():

    ''' A simple comb filter that processes a mono signal.
    '''

    def __init__(self, delay_in_ms, sample_rate):

        '''Constructs a new CombFilter object.

        Parameters:
        -----------

        delay_in_ms: int
            the delay in ms

        sample_rate: int
            the signal's sample rate

        Returns:
        --------

        CombFilter
            a new CombFilter object

        '''

        self.delay_in_ms = delay_in_ms
        self.delay_in_samples = int(np.ceil(( self.delay_in_ms / 1000 ) * sample_rate))


    def process_buffer(self, x, dampening_coefficient):

        ''' Processes an audio buffer.

        Parameters:
        -----------

        x: np.array
            the audio signal being processed

        dampening_coefficient: float
            the amount of dampening to use, a float between 0 and 1.

        Returns:
        --------
        np.array
            the processed audio signal

        Notes:
        ------

        This filtering implementation is based on the IIR linear filter implementation from SciPi.
        More information can be found at: https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.signal.lfilter.html
        The arrays used for comb filtering are as follows:
            b feedback coefficient [1, zero-padding to length of delay - 1, dampening_coefficient]
            a feedforward coefficient [1, zero-padding to length of b]

        '''

        b = [1]
        a = [1]
        for i in range(self.delay_in_samples - 1):
            b.append(0)
            a.append(0)
        b.append(dampening_coefficient)
        a.append(0)

        return sp.lfilter(b, a, x)


class AllPassFilter():

    ''' A simple all-pass filter that processes a mono signal.
    '''

    def __init__(self, delay_in_ms, sample_rate):
        
        '''Constructs a new AllPassFilter object.

        Parameters:
        -----------

        delay_in_ms: int
            the delay in ms

        sample_rate: int
            the signal's sample rate

        Returns:
        --------

        AllPassFilter
            a new AllPassFilter object

        '''

        self.delay_in_ms = delay_in_ms
        self.delay_in_samples = int(np.ceil(( self.delay_in_ms / 1000 ) * sample_rate))


    def process_buffer(self, x, attenuation_coefficient):
        
        ''' Processes an audio buffer.

        Parameters:
        -----------

        x: np.array
            the audio signal being processed

        attenuation_coefficient: float
            the amount of all-pass attenuation to use, a float between 0 and 1.

        Returns:
        --------
        np.array
            the processed audio signal

        Notes:
        ------

        This filtering implementation is based on the IIR linear filter implementation from SciPi.
        More information can be found at: https://docs.scipy.org/doc/scipy-0.18.1/reference/generated/scipy.signal.lfilter.html
        The arrays used for all-pass filtering are as follows:
            b feedback coefficient [1, zero-padding to length of delay - 1, 1]
            a feedforward coefficient [1, zero-padding to length of delay - 1, attenuation_coefficient]

        '''

        b = [attenuation_coefficient]
        a = [1]

        for i in range(self.delay_in_samples - 1):
            b.append(0)
            a.append(0)

        b.append(1)
        a.append(attenuation_coefficient)

        return sp.lfilter(b, a, x)


class SchroederReverberator():
    ''' Processes mono signals using a signal processing pipeline.
    '''


    def __init__(self, 
                sample_rate, 
                amount=0.5, 
                num_combs=4, 
                comb_dampening=0.5, 
                num_allpasses=2, 
                allpass_attenuation=0.5, 
                delay_times=[25, 30, 35, 40, 25, 50]):
    
        ''' Creates a new reverberator using a combination of comb and all-pass filters.

        Parameters:
        -----------

        sample_rate: int
            the sample rate to use when initializing the reverberator (to convert delay times to sample delays)

        amount: float
            the dry/wet amount to use when initializing the reverberator, a float between 0 and 1

        num_combs: int
            the number of comb filters this reverberator should use in its signal processing pipeline

        comb_dampening: float
            the amount of dampening for the comb filters
        
        num_allpasses: int
            the number of all-pass filters this filter should use in its signal processing pipeline

        allpass_attenuation: float
            the amount of attenuation for the all-pass filters

        delay_times: list
            a list of the delay times in milliseconds for each filter, ordered combs first, then all-passes.

        Example:
        --------

            amount = 0.5
            num_combs = 4
            comb_dampening = 0.25
            num_allpasses = 2
            allpass_attenuation = 0.5
            delay_times = [
                20, # Comb 1
                30, # Comb 2
                40, # Comb 3
                50, # Comb 4
                25, # All-pass 1
                50  # All-pass 2
            ]

            reverberator = SchroederReverberator(
                amount,
                num_combs,
                comb_dampening,
                num_allpasses,
                allpass_attenuation,
                delay_times
            )

        '''

        self.amount = amount
        self.num_combs = num_combs
        self.num_allpasses = num_allpasses
        self.delay_times = delay_times
        self.processing_pipeline = list()
        self.comb_dampening = 1 - comb_dampening
        self.allpass_attenuation = 1 - allpass_attenuation

      for i in range(self.num_combs):
          self.processing_pipeline.append( CombFilter(delay_times[i], sample_rate) )

      for i in range(self.num_combs, self.num_combs + self.num_allpasses):
          self.processing_pipeline.append( AllPassFilter(delay_times[i], sample_rate) )


    def process_buffer(self, x):

        ''' Process a mono signal using the reverberator.

        Parameters:
        -----------
        
        x: np.array
            the audio signal to process

        Returns:
        --------

        np.array
            the processed audio signal

        Example:
        --------

        # Load up a file, separate left and right channels
        x, sample_rate = soundfile.load("SomeFile.wav", sr=None)
        x_l = x[:,0]
        x_r = x[:,1]

        reverberator = SchroederReverberator(
            amount,
            num_combs,
            comb_dampening,
            num_allpasses,
            allpass_attenuation,
            delay_times
        )

        y_l = reverberator.process_buffer(x_l)
        y_r = reverberator.process_buffer(x_r)

        soundfile.write(
            "SomeFileProcessed.wav", 
            [y_l,y_r], 
            rate=sample_rate
        )

        '''

        length = len(x)
        y = np.zeros(length)
        buffers = list()

        for i in range(self.num_combs):
            buffers.append( self.processing_pipeline[i].process_buffer(x, self.comb_dampening) )

        for j in range(self.num_combs):
            y = np.add(y, (1 / self.num_combs) * buffers[j])
        
        for i in range(self.num_combs, self.num_combs + self.num_allpasses):
            y = self.processing_pipeline[i].process_buffer(y, self.allpass_attenuation)
      
        x_pad = np.zeros( len(y) - len(x) )

        x = np.hstack( (x, x_pad) )

        return np.add(y * self.amount, x * (1 - self.amount))

