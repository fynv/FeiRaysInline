import math
import glm
import VkInline as vki
from VkInline.SVCombine import *
from .spectrum import *

class PointLight(vki.ShaderViewable):
    def __init__(self, position, color, intensity):
        self.d_pos = vki.SVVec3(glm.vec3(position))
        self.d_intensity = Spectrum(glm.vec3(color)*intensity)
        self.m_cptr = SVCombine_Create({'pos': self.d_pos, 'intensity': self.d_intensity}, '''
Spectrum sample_l(in Comb_#hash# self, in vec3 ip, inout RNGState state, inout vec3 dirToLight, inout float distance, inout float pdfw)
{
    vec3 v = self.pos - ip;
    float len = length(v);
    dirToLight = v / len;
    pdfw = len*len;
    distance = len;
    return self.intensity;    
}
''')

    def power(self, scene):
        return 4.0 * self.d_intensity.Intensity()

    name_lst = 'point_lights'
    is_geometry = False
    is_light_source = True

