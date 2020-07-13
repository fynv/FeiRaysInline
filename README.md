# FeiRaysInline

This project tries to code a Vulkan acclerated PBRT system fully in Python.

[VkInline](https://github.com/fynv/vkinline) provided an easy to use interface to access latest GPU power from Python.
Based on VkInline, it is possible to contruct sophisticated hybrid CPU/GPU software systems using OOP techniques.

Install VkInline:
```
$ pip3 install VkInline
```

Install Pillow (needed by the test):
```
$ pip3 install pillow
```

Clone the code then run the test:
```
$ python3 test_pathtrace.py
```
<img src="doc/result.png" width="900px">
