import math
import glm
import VkInline as vki
from VkInline.SVCombine import *
from .spectrum import *

class PointLight(vki.ShaderViewable):
    def __init__(self, position, intensity):
        self.m_pos = vki.SVVec3(glm.vec3(position))
        self.m_intensity = Spectrum(intensity)
        self.m_cptr = SVCombine_Create({'pos': self.m_pos, 'intensity': self.m_intensity}, '''
Spectrum sample_l(in Comb_#hash# self, in vec3 ip, inout vec3 dirToLight, inout float distance, inout float pdfw)
{
    vec3 v = self.pos - ip;
    float len = v.length();
    dirToLight = v / len;
    pdfw = len*len;
    distance = len;
    return self.intensity;    
}
''')

    def power(self):
        return 4 * math.pi * self.m_intensity.Intensity()

    name_lst = 'point_lights'
    is_geometry = False
    is_light_source = True

