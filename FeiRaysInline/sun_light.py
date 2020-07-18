import math
import glm
import VkInline as vki
from VkInline.SVCombine import *
from .spectrum import *

class SunLight(vki.ShaderViewable):
    def __init__(self, direction, radian, color, intensity):
        direction = glm.normalize(glm.vec3(direction))
        self.m_radian = radian
        self.d_dir_radian = vki.SVVec4(glm.vec4(direction, radian))
        self.d_intensity = Spectrum(glm.vec3(color)*intensity)
        self.m_cptr = SVCombine_Create({'dir_radian': self.d_dir_radian, 'intensity': self.d_intensity}, '''
Spectrum sample_l(in Comb_#hash# self, in vec3 ip, inout RNGState state, inout vec3 dirToLight, inout float distance, inout float pdfw)
{
    vec3 dir = self.dir_radian.xyz;
    float factor = 1.0 - cos(self.dir_radian.w);

    float r1 = rand01(state);
    float r2 = rand01(state) * radians(360.0);
    vec3 a, b;
    if (abs(dir.x)>0.8)
        a = vec3(0.0, 1.0, 0.0);
    else 
        a = vec3(1.0, 0.0, 0.0);

    a = normalize(cross(a, dir));
    b = cross(a, dir);

    float v_z = 1.0 - r1 * factor;
    float v_xy = sqrt(1.0 - v_z*v_z);
    float v_x = v_xy * cos(r2);
    float v_y = v_xy * sin(r2);

    dirToLight = v_z*dir + a*v_x + b*v_y;

    distance = -1.0;
    pdfw = 1.0/(radians(360.0)*factor);

    return self.intensity;
}
''')

    def power(self, scene):
        scene_size = glm.vec3(scene.m_aabb[3], scene.m_aabb[4], scene.m_aabb[5]) - glm.vec3(scene.m_aabb[0], scene.m_aabb[1], scene.m_aabb[2])
        scene_len = glm.length(scene_size)
        factor = 1.0 - math.cos(self.m_radian)
        return 2.0 * math.pi * factor * scene_len*scene_len* self.d_intensity.Intensity()

    name_lst = 'sun_lights'
    is_geometry = False
    is_light_source = True

