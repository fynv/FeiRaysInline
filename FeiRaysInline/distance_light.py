import math
import glm
import VkInline as vki
from VkInline.SVCombine import *
from .spectrum import *

class DistanceLight(vki.ShaderViewable):
    def __init__(self, direction, color, intensity):
        self.d_dir = vki.SVVec3(glm.normalize(glm.vec3(direction)))
        self.d_intensity = Spectrum(glm.vec3(color)*intensity)
        self.m_cptr = SVCombine_Create({'dir': self.d_dir, 'intensity': self.d_intensity}, '''
Spectrum sample_l(in Comb_#hash# self, in vec3 ip, inout RNGState state, inout vec3 dirToLight, inout float distance, inout float pdfw)
{
    dirToLight = self.dir;
    distance = -1.0;
    pdfw = 1.0;
    return self.intensity;
}
''')

    def power(self, scene):
        scene_size = glm.vec3(scene.m_aabb[3], scene.m_aabb[4], scene.m_aabb[5]) - glm.vec3(scene.m_aabb[0], scene.m_aabb[1], scene.m_aabb[2])
        scene_len = glm.length(scene_size)
        return scene_len*scene_len* self.d_intensity.Intensity()

    name_lst = 'distance_lights'
    is_geometry = False
    is_light_source = True

