# akarshit-intro

A 24-second animated profile intro built with [HyperFrames](https://github.com/heygen-com/hyperframes).

## Render

Requires Node 22+, FFmpeg, and headless Chrome (installed by the CLI).

```sh
npm install -g hyperframes
hyperframes browser ensure
hyperframes render . -o renders/akarshit-intro.mp4
```

## Preview in the studio

```sh
hyperframes preview
```

## Music

`assets/music.mp3` is generated procedurally by `make_music.py` (needs `numpy`),
so the track is royalty-free and reproducible. Edit the chord list or tempo in
that script and re-run it to change the soundtrack.
