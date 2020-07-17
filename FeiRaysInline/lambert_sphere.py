import numpy as np
import glm
import VkInline as vki
from .spectrum import *
from .sphere import *
from .interaction import *

class LambertSphere(Sphere):
    def __init__(self, modelMat = glm.identity(glm.mat4), color = (1.0, 1.0, 1.0)):
        Sphere.__init__(self)
        self.m_modelMat = modelMat
        self.m_normMat = glm.transpose(glm.inverse(modelMat))
        self.d_normMat = vki.SVMat4x4(self.m_normMat)
        self.d_color  = Spectrum(color)
        self.m_cptr = SVCombine_Create({'normalMat':  self.d_normMat, 'color': self.d_color }, '''
void closethit(in Comb_#hash# sphere, in vec3 hitpoint, inout {HitInfo_Lambert} hitinfo)
{{
    hitinfo.lambert.color = sphere.color;
    hitinfo.normal = normalize((sphere.normalMat * vec4(hitpoint, 0.0)).xyz);   
}}
'''.format(HitInfo_Lambert = Name_HitInfo_Lambert))

    closest_hit ='''
hitAttributeEXT vec3 hitpoint;
#define HitInfo {HitInfo_Lambert}
void write_payload(in HitInfo hitinfo);
void main()
{{
    HitInfo hitinfo;
    hitinfo.t = gl_HitTEXT;
    closethit(get_value(lambert_spheres, gl_InstanceCustomIndexEXT), hitpoint, hitinfo);
    write_payload(hitinfo);
}}
'''.format(HitInfo_Lambert = Name_HitInfo_Lambert) + define_features(Name_HitInfo_Lambert)

    name_lst = 'lambert_spheres'
    is_light_source = False

