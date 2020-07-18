import VkInline as vki
from VkInline.SVCombine import *
import glm
from .spectrum import *

class BxDF_Lambert(vki.ShaderViewable): 
    def __init__(self):
        self.m_color = Spectrum()
        self.m_cptr = SVCombine_Create({'color':  self.m_color }, '''
Spectrum f(in Comb_#hash# self, in vec3 n, in vec3 wo, in vec3 wi)
{
    Spectrum ret;
    float d = dot(wi, n);
    if (d<=0.0)
    {
        from_rgb(ret, vec3(0.0));
    }
    else
    {
        ret = mult(self.color, d/radians(180.0));
    }
    return ret;
}

float pdf(in Comb_#hash# self, in vec3 n, in vec3 wo, in vec3 wi)
{
    float d = dot(wi, n);
    if (d<=0.0) return 0.0;
    return d/radians(180.0);
}

Spectrum sample_f(in Comb_#hash# self, in vec3 n,  in vec3 wo, inout vec3 wi, inout RNGState state, inout float path_pdf)
{
    vec3 a, b;
    if (abs(n.x)>0.8)
        a = vec3(0.0, 1.0, 0.0);
    else 
        a = vec3(1.0, 0.0, 0.0);

    a = normalize(cross(a, n));
    b = cross(a, n);

    float z = sqrt(rand01(state));
    float xy = sqrt(1.0 - z*z);
    float alpha = rand01(state)*radians(360.0);
    float x = xy * cos(alpha);
    float y = xy * sin(alpha);

    wi = x*a + y*b + z * n;

    path_pdf = pdf(self, n, wo, wi);
    return f(self, n, wo, wi);
}
''')

BxDF_Lambert.dummy = BxDF_Lambert()
Name_BxDF_Lambert = BxDF_Lambert.dummy.name_view_type()

class HitInfo_Lambert(vki.ShaderViewable):
    def __init__(self):
        self.m_t = vki.SVFloat(0.0)
        self.m_normal = vki.SVVec3(glm.vec3(0.0))
        self.m_cptr = SVCombine_Create({'t':  self.m_t, 'normal': self.m_normal, 'lambert': BxDF_Lambert.dummy }, '''
Spectrum evaluate_bsdf(in Comb_#hash# self, in vec3 wo, in vec3 wi)
{
    return f(self.lambert, self.normal, wo, wi);
}

float pdf_bsdf(in Comb_#hash# self, in vec3 wo, in vec3 wi)
{
    return pdf(self.lambert, self.normal, wo, wi);
}

Spectrum sample_bsdf(in Comb_#hash# self, in vec3 wo, inout vec3 wi, inout RNGState state, inout float path_pdf)
{
    return sample_f(self.lambert, self.normal, wo, wi, state, path_pdf);
}
''')

HitInfo_Lambert.dummy = HitInfo_Lambert()
Name_HitInfo_Lambert = HitInfo_Lambert.dummy.name_view_type()

class HitInfo_UniformEmissive(vki.ShaderViewable):
    def __init__(self):
        self.m_t = vki.SVFloat(0.0)
        self.m_light_id = vki.SVInt32(0)        
        self.m_intensity = Spectrum()
        self.m_cptr = SVCombine_Create({'t':  self.m_t, 'light_id': self.m_light_id, 'intensity': self.m_intensity}, '''
Spectrum Le(in Comb_#hash# self, in vec3 wo, int depth_iter)
{
    Spectrum ret = self.intensity;
    if (depth_iter>0)
    {
        from_rgb(ret, vec3(0.0));
    }
    return ret;
}
''')

HitInfo_UniformEmissive.dummy = HitInfo_UniformEmissive()
Name_HitInfo_UniformEmissive = HitInfo_UniformEmissive.dummy.name_view_type()


map_features = {
    Name_HitInfo_Lambert: ['HAS_BSDF'],
    Name_HitInfo_UniformEmissive: ['HAS_EMISSION']
}

def define_features(type_hitinfo):
    features = map_features[type_hitinfo]
    definitions = ''
    for f in features:
        definitions += '#define ' + f + '\n'
    return definitions
