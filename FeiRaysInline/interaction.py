import VkInline as vki

vki.Add_Built_In_Header('interaction.shinc', '''

struct HitInfo_Lambert
{
    float t;
    Spectrum color;
    vec3 normal;
};

Spectrum bsdf(in HitInfo_Lambert hitinfo, in vec3 wo, in vec3 wi)
{
    Spectrum ret;
    float d = dot(wi, hitinfo.normal);
    if (d<=0.0)
    {
        from_rgb(ret, vec3(0.0));
    }
    else
    {
        ret = mult(hitinfo.color, d/radians(180.0));
    }
    return ret;
}

float pdf(in HitInfo_Lambert hitinfo, in vec3 wo, in vec3 wi)
{
    float d = dot(wi, hitinfo.normal);
    if (d<=0.0) return 0.0;
    return d/radians(180.0);
}

Spectrum sample_bsdf(in HitInfo_Lambert hitinfo, in vec3 wo, inout vec3 wi, inout RNGState state, inout float path_pdf)
{
    vec3 a, b;
    if (abs(hitinfo.normal.x)>0.8)
        a = vec3(0.0, 1.0, 0.0);
    else 
        a = vec3(1.0, 0.0, 0.0);

    a = normalize(cross(a, hitinfo.normal));
    b = cross(a, hitinfo.normal);

    float z = sqrt(rand01(state));
    float xy = sqrt(1.0 - z*z);
    float alpha = rand01(state)*radians(360.0);
    float x = xy * cos(alpha);
    float y = xy * sin(alpha);

    wi = x*a + y*b + z * hitinfo.normal;

    path_pdf = pdf(hitinfo, wo, wi);
    return bsdf(hitinfo, wo, wi);
}
''')
vki.Add_Inlcude_Filename('interaction.shinc')

map_features = {
    'HitInfo_Lambert': ['HAS_BSDF']
}

def define_features(type_hitinfo):
    features = map_features[type_hitinfo]
    definitions = ''
    for f in features:
        definitions += '#define ' + f + '\n'
    return definitions
