import numpy as np, wave
SR=44100; DUR=24.0; N=int(SR*DUR); t=np.arange(N)/SR
rng=np.random.default_rng(7)
def note(f): return 440*2**((f-69)/12)
def env(n,a,d,s,r,total):
    e=np.zeros(n); A=int(a*SR); D=int(d*SR); R=int(r*SR); T=int(total*SR)
    e[:A]=np.linspace(0,1,A); e[A:A+D]=np.linspace(1,s,D); e[A+D:T-R]=s; e[T-R:T]=np.linspace(s,0,R); return e[:n]
# Chord progression: Am9 - Fmaj7 - Cmaj9 - G6 , 6s each
chords=[[57,60,64,67,71],[53,57,60,64,67],[48,52,55,59,62],[55,59,62,64,67]]
pad=np.zeros(N)
for i,ch in enumerate(chords):
    s0=int(i*6*SR); seg=N-s0 if i==3 else int(6.5*SR); seg=min(seg,N-s0)
    tt=np.arange(seg)/SR; e=env(seg,1.5,0.5,0.8,1.5,seg/SR)
    for m in ch:
        f=note(m-12)
        det=[0.997,1.0,1.003]
        v=sum(np.sin(2*np.pi*f*d*tt+0.3*np.sin(2*np.pi*0.2*tt)) for d in det)/3
        v+=0.25*np.sin(2*np.pi*2*f*tt)
        pad[s0:s0+seg]+=v*e*0.08
# Sub bass
bass=np.zeros(N)
for i,ch in enumerate(chords):
    s0=int(i*6*SR); seg=min(int(6*SR),N-s0); tt=np.arange(seg)/SR
    f=note(ch[0]-24); bass[s0:s0+seg]+=np.sin(2*np.pi*f*tt)*env(seg,0.5,0.5,0.7,1.0,seg/SR)*0.22
# Arpeggio plucks, 72 bpm eighth notes
bpm=72; step=60/bpm/2; pl=np.zeros(N)
k=0
for s in np.arange(0,DUR,step):
    ci=int(s//6); ch=chords[ci]; m=ch[(k*2)%len(ch)]+12 if k%3 else ch[(k)%len(ch)]+24; k+=1
    if s<1.0 or s>22.5: continue
    if rng.random()<0.22: continue
    s0=int(s*SR); L=int(1.6*SR); L=min(L,N-s0); tt=np.arange(L)/SR; f=note(m)
    v=(np.sin(2*np.pi*f*tt)+0.4*np.sin(2*np.pi*2*f*tt)+0.15*np.sin(2*np.pi*3*f*tt))*np.exp(-tt*3.2)
    amp=0.07 if k%4 else 0.1
    pl[s0:s0+L]+=v*amp
# Soft noise shimmer
sh=rng.normal(0,1,N); 
# crude lowpass via moving average then highpass by subtracting slower average
def ma(x,w): c=np.cumsum(np.insert(x,0,0)); return (c[w:]-c[:-w])/w
shf=np.zeros(N); a=ma(sh,6); b=ma(sh,40); m=min(len(a),len(b)); shf[:m]=a[:m]-b[:m]
shf*= (0.5+0.5*np.sin(2*np.pi*0.1*t-1.5))*0.012
mix=pad+bass+pl+shf
# simple reverb: exponentially decaying noise impulse
ir=rng.normal(0,1,int(1.8*SR))*np.exp(-np.arange(int(1.8*SR))/SR*3.0); ir/=np.abs(ir).sum()/4
wet=np.fft.irfft(np.fft.rfft(mix,N+len(ir))*np.fft.rfft(ir,N+len(ir)))[:N]
mix=mix*0.75+wet*0.9
# master fade
fade=np.ones(N); fi=int(2*SR); fo=int(3*SR); fade[:fi]=np.linspace(0,1,fi); fade[-fo:]=np.linspace(1,0,fo)
mix*=fade; mix/=np.abs(mix).max()*1.15
# stereo widen: slight delay on right
R=np.roll(mix,int(0.012*SR)); L=mix
st=np.stack([L*0.98+R*0.02, R*0.98+L*0.02],1)
data=(st*32767).astype(np.int16)
with wave.open('assets/music.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())
print("ok", data.shape)
