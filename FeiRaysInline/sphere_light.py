import math
import glm
import VkInline as vki
from .spectrum import *
from .sphere import *
from .interaction import *

class SphereLight(Sphere):
    def __init__(self, center, r, color, intensity):
        Sphere.__init__(self)
        self.m_r = r
        modelMat = glm.identity(glm.mat4)
        modelMat = glm.translate(modelMat, glm.vec3(center))
        self.m_modelMat = glm.scale(modelMat, glm.vec3(r, r, r))
        self.d_center_radius = vki.SVVec4(glm.vec4(center[0],center[1],center[2], r))
        self.d_intensity = Spectrum(glm.vec3(color)*intensity)
        self.m_cptr = SVCombine_Create({'center_radius': self.d_center_radius, 'intensity': self.d_intensity }, '''
void closethit(in Comb_#hash# self, in vec3 hitpoint, inout {HitInfo_UniformEmissive} hitinfo)
{{
    hitinfo.intensity = self.intensity;
}}

Spectrum sample_l(in Comb_#hash# self, in vec3 ip, inout RNGState state, inout vec3 dirToLight, inout float distance, inout float pdfw)
{{
    vec3 dir = self.center_radius.xyz - ip;
    float dis2center = length(dir);
    dir *= 1.0/dis2center;
    float factor = self.center_radius.w/dis2center;
    factor = 1.0 - sqrt(1.0 - factor*factor);

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

    distance = 3.402823466e+38;

    pdfw = 1.0/(radians(360.0)*factor);
    return self.intensity;    

}}
'''.format(HitInfo_UniformEmissive = Name_HitInfo_UniformEmissive))

    def power(self):
        return 4 * math.pi * self.m_r * self.m_r * self.d_intensity.Intensity()

    closest_hit ='''
hitAttributeEXT vec3 hitpoint;
#define HitInfo {HitInfo_UniformEmissive}
void write_payload(in HitInfo hitinfo);
void main()
{{
    HitInfo hitinfo;
    hitinfo.t = gl_HitTEXT;
    hitinfo.light_id = int(sphere_lights.id_offset + gl_InstanceCustomIndexEXT);
    closethit(get_value(sphere_lights, gl_InstanceCustomIndexEXT), hitpoint, hitinfo);
    write_payload(hitinfo);
}}
'''.format(HitInfo_UniformEmissive = Name_HitInfo_UniformEmissive) + define_features(Name_HitInfo_UniformEmissive)        

    name_lst = 'sphere_lights'
    is_light_source = True

    
