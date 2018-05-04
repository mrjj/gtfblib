from __future__ import division
import numpy as np
from scipy.io import loadmat

from gtfblib.gtfb import ERBnum2Hz
from gtfblib.fir import FIR

#from test_aux_functions import peak_error
def peak_error(a, b):
    assert(a.shape==b.shape)
    return np.max(np.abs(a-b))

# The FIR filterbank is designed to replicate the FB I used for my
# Thesis work, which can be found at
# https://jthiem.bitbucket.io/research.html#Thesis
# "A Sparse Auditory Envelope Representation with Iterative Reconstruction
# for Audio Coding", with the code maintained at
# https://github.com/jthiem/SparseAuditoryEnvelopeCoding
#
# The FIR16kTestdata.mat file can be generated by cloning the above
# github repo, start MATLAB or Octave from that directory, and then
# run
#
# load <...>/gtfblib/test/Inputdata.mat
# FD = FBsetup(struct('L', 1600));
# y = SFanalysis(indata16k, FD)'; <-- note the tick (transpose)
# save FIR16kTestdata.mat y FD
#
# warning: some arrays are transposed depending on if you are using
# MATLAB or Octave

fs = 16000
insig = loadmat('test/Inputdata.mat', squeeze_me=True)['indata16k']
Fdata = loadmat('test/FIR16kTestdata.mat', squeeze_me=True)['FD']
refout = loadmat('test/FIR16kTestdata.mat', squeeze_me=True)['y']
fbFIR = FIR(fs=fs, cfs=ERBnum2Hz(np.arange(1, 32.1, .5)), complexresponse=True)

def test_FIR_ERB():
    assert(peak_error(fbFIR.ERB, Fdata['b'][()])<1e-10)

def test_FIR_ir():
    assert(peak_error(fbFIR.ir, Fdata['G'][()].T.conj())<1e-10)

def test_FIR_process():
    fbFIR._clear()
    outsig = fbFIR.process(insig)
    assert(peak_error(outsig, refout)<1e-10)

def test_FIR_process_single():
    outsig = fbFIR.process_single(insig, 10)
    assert(peak_error(outsig, refout[:, 10])<1e-10)

def test_FIR_process_memory():
    fbFIR._clear()
    outsig1 = fbFIR.process(insig[:800])
    outsig2 = fbFIR.process(insig[800:])
    outsig = np.vstack((outsig1, outsig2))
    assert(peak_error(outsig, refout)<1e-10)

def test_FIR_clear():
    _ = fbFIR.process(np.random.randn(1000))
    fbFIR._clear()
    outsig = fbFIR.process(insig)
    assert(peak_error(outsig, refout)<1e-10)
