# FeiRaysInline

This project tries to code a Vulkan acclerated PBRT system fully in Python.

[VkInline](https://github.com/fynv/vkinline) provided an easy to use interface to access latest GPU power from Python.
Based on VkInline, it is possible to contruct sophisticated hybrid CPU/GPU software systems using OOP techniques.

Note that the ray-tracing acceleration is powered by VK_KHR_ray_tracing. For Nvidia users, a [Nvidia Beta driver](https://developer.nvidia.com/vulkan-driver) might be needed.


Install VkInline:
```
$ pip3 install VkInline
```

Install Pillow (needed by the test):
```
$ pip3 install pillow
```

Clone the code then run the tests:
```
$ python3 test_pathtrace.py
```
<img src="doc/result.png" width="900px">

```
$ python3 test_pathtrace2.py
```
<img src="doc/result2.png" width="900px">
