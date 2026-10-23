# R010 K1 copy traffic as a negative novelty finding
Read-only source Joshua-Zhang-Jiaquan/LaLaLanD_qwen@80e4869016628733674c4d5dc605cc9f008d9f17:
qwen_shared/ced32_core.py GlobalKVBank.append:
key=torch.cat([key,new_key],dim=-2)
value=torch.cat([value,new_value],dim=-2).
qwen_shared/attention_only.py appends once per forward.
A T-token one-by-one continuation after N existing tokens,
combined bank bytes/token d, allocates d*(NT+T(T+1)/2)
bytes in the consecutive new cat outputs, vs d*T actual new
KV content. With d=4096: 4096+1024 -> 18.001953125 GiB
written; 8192+8192 -> 384.015625 GiB.
No physical GPU traffic measurement, runtime measurement,
or overall asymptotic inference speed claim.
The project documentation explicitly acknowledges O(N)
copy per append and disclaims optimized decode latency.
Thus PARK K1 as original scientific discovery while retaining
a source-grounded engineering diagnostic. Do not edit
or run the separately active 27B training repository.
Related: NVIDIA 2026 KV Cache Compression and Infra Problems
https://research.nvidia.com/labs/eai/post/kv-cache-compression-and-its-infra-problems/
