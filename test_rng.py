import numpy as np
import VkInline as vki
import FeiRaysInline as fri

count = 1 << 18
d_states = vki.SVVector('RNGState', count)
initializer = fri.RNGInitializer()
initializer.InitRNGVector(d_states)

states = np.empty((count, 6), dtype=np.uint32)
d_states.m_buf.to_host(states.__array_interface__['data'][0])

print(states)
