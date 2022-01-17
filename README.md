# REVERBERATOR

**Author: Sean Goldie**

A simple Schroeder reverberator for Python projects that processes monophonic sound. This code was written for the Advanced Musical Acoustics class at NYU, and therefore gives you lots of control over the parameters of the reverb so as to model different spaces. It could be easily adapted to work on stereo by splitting the left and right channels and processing them separately.

## Usage
reverberator.py contains code for CombFilter(), AllPassFilter(), and SchroederReveberator() classes. Import them:
`from reverberator import *`
and use them to process Numpy arrays like so:
```
# Load up a file, separate left and right channels
x, sample_rate = soundfile.read("SomeFile.wav")
x_l = x[:,0]
x_r = x[:,1]

# Define our space and reverberator parameters
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

# Create the reverberator
reverberator = SchroederReverberator(
	amount,
	num_combs,
	comb_dampening,
	num_allpasses,
	allpass_attenuation,
	delay_times
	)

# Call the process method
y_l = reverberator.process_buffer(x_l)
y_r = reverberator.process_buffer(x_r)

# Write a new file
soundfile.write(
    "SomeFileProcessed.wav", 
    [y_l,y_r], 
    rate=sample_rate
)
```
You will need the dependencies Numpy and SciPy.