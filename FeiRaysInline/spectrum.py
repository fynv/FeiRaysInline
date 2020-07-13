import VkInline as vki

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

struct RGBSpectrum
{
    vec3 data;
};

void incr(inout RGBSpectrum a, in RGBSpectrum b)
{
    a.data += b.data;
}

RGBSpectrum add(in RGBSpectrum a, in RGBSpectrum b)
{
    RGBSpectrum ret;
    ret.data = a.data + b.data;
    return ret;
}

RGBSpectrum sub(in RGBSpectrum a, in RGBSpectrum b)
{
    RGBSpectrum ret;
    ret.data = a.data - b.data;
    return ret;
}

RGBSpectrum mult(in RGBSpectrum a, in RGBSpectrum b)
{
    RGBSpectrum ret;
    ret.data = a.data * b.data;
    return ret;
}

RGBSpectrum div(in RGBSpectrum a, in RGBSpectrum b)
{
    RGBSpectrum ret;
    ret.data = a.data / b.data;
    return ret;
}

RGBSpectrum mult(in RGBSpectrum a, float b)
{
    RGBSpectrum ret;
    ret.data = a.data * b;
    return ret;
}


void amplify(inout RGBSpectrum a, in RGBSpectrum b )
{
    a.data *= b.data;
}

void amplify(inout RGBSpectrum a, float b )
{
    a.data *= b;
}

RGBSpectrum div(in RGBSpectrum a, float b)
{
    RGBSpectrum ret;
    ret.data = a.data / b;
    return ret;
}

void diminish(inout RGBSpectrum a, float b )
{
    a.data /= b;
}

RGBSpectrum neg(in RGBSpectrum a)
{
    RGBSpectrum ret;
    ret.data =  -a.data;
    return ret; 
}

void from_rgb(out RGBSpectrum a, in vec3 rgb)
{
    a.data = rgb;
}

vec3 to_rgb(in RGBSpectrum a)
{
    return a.data;
}

void from_xyz(out RGBSpectrum a, in vec3 xyz)
{
    a.data = xyz2rgb(xyz);
}

vec3 to_xyz(in RGBSpectrum a)
{
    return rgb2xyz(a.data);
}

float max_component_value(in RGBSpectrum a)
{
    return max(max(a.data.x, a.data.y), a.data.z);
}

#define Spectrum RGBSpectrum
''')
vki.Add_Inlcude_Filename('spectrum.shinc')

