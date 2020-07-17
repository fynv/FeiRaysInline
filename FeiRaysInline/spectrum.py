import VkInline as vki
from VkInline.SVCombine import *
import glm

vki.Add_Built_In_Header('spectrum.shinc', '''

mat3 mat_rgb2xyz = mat3(
0.412453, 0.212671, 0.019334,
0.357580, 0.715160, 0.119193,
0.180423, 0.072169, 0.950227);

mat3 mat_xyz2rgb = mat3(
3.240479, -0.969256, 0.055648,
-1.537150, 1.875991, -0.204043,
-0.498535, 0.041556, 1.057311);

vec3 rgb2xyz(in vec3 rgb)
{
    return mat_rgb2xyz * rgb;
}

vec3 xyz2rgb(in vec3 xyz)
{
    return mat_xyz2rgb * xyz;
}
''')

vki.Add_Inlcude_Filename('spectrum.shinc')

class RGBSpectrum(vki.ShaderViewable):
    def __init__(self, color = (0.0, 0.0, 0.0)):
        self.m_rgb = glm.vec3(color)
        self.m_svdata = vki.SVVec3(self.m_rgb)
        self.m_cptr = SVCombine_Create({'data':  self.m_svdata }, '''
void incr(inout Comb_#hash# a, in Comb_#hash# b)
{
    a.data += b.data;
}

Comb_#hash# add(in Comb_#hash# a, in Comb_#hash# b)
{
    Comb_#hash# ret;
    ret.data = a.data + b.data;
    return ret;
}

Comb_#hash# sub(in Comb_#hash# a, in Comb_#hash# b)
{
    Comb_#hash# ret;
    ret.data = a.data - b.data;
    return ret;
}

Comb_#hash# mult(in Comb_#hash# a, in Comb_#hash# b)
{
    Comb_#hash# ret;
    ret.data = a.data * b.data;
    return ret;
}

Comb_#hash# div(in Comb_#hash# a, in Comb_#hash# b)
{
    Comb_#hash# ret;
    ret.data = a.data / b.data;
    return ret;
}

Comb_#hash# mult(in Comb_#hash# a, float b)
{
    Comb_#hash# ret;
    ret.data = a.data * b;
    return ret;
}

Comb_#hash# mult(float b, in Comb_#hash# a)
{
    Comb_#hash# ret;
    ret.data = a.data * b;
    return ret;
}


void amplify(inout Comb_#hash# a, in Comb_#hash# b )
{
    a.data *= b.data;
}

void amplify(inout Comb_#hash# a, float b )
{
    a.data *= b;
}

Comb_#hash# div(in Comb_#hash# a, float b)
{
    Comb_#hash# ret;
    ret.data = a.data / b;
    return ret;
}

void diminish(inout Comb_#hash# a, float b )
{
    a.data /= b;
}

Comb_#hash# neg(in Comb_#hash# a)
{
    Comb_#hash# ret;
    ret.data =  -a.data;
    return ret; 
}

void from_rgb(out Comb_#hash# a, in vec3 rgb)
{
    a.data = rgb;
}

vec3 to_rgb(in Comb_#hash# a)
{
    return a.data;
}

void from_xyz(out Comb_#hash# a, in vec3 xyz)
{
    a.data = xyz2rgb(xyz);
}

vec3 to_xyz(in Comb_#hash# a)
{
    return rgb2xyz(a.data);
}

float max_component_value(in Comb_#hash# a)
{
    return max(max(a.data.x, a.data.y), a.data.z);
}

#define Spectrum Comb_#hash#

''')
    def Intensity(self):
        return 0.212671*self.m_rgb[0] + 0.715160*self.m_rgb[1] + 0.072169*self.m_rgb[2]

RGBSpectrum.dummy = RGBSpectrum()
Name_RGBSpectrum = RGBSpectrum.dummy.name_view_type()
Spectrum = RGBSpectrum

