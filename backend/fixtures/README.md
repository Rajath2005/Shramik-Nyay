# Audio fixtures

`replay_recorded_call.pcm` is a committed, synthetic demo fixture. It is
8 kHz, mono, signed little-endian 16-bit PCM and is deliberately streamed
through the same 1024-byte, 64 ms Prisma pacer used by the microphone path.

The speech source was generated once with Gnani Timbre v3.0 (Shivani voice)
and mixed with deterministic procedural industrial-site noise before the raw
PCM was committed. It is not a recording of a real worker or call and must
not be treated as evidence.
