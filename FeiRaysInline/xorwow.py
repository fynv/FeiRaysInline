import os
import numpy as np
import VkInline as vki
from VkInline.SVCombine import *

vki.Add_Built_In_Header('rand_xorwow.shinc', '''
struct V5
{
    uint v0;
    uint v1;
    uint v2;
    uint v3;
    uint v4;
};

struct RNGState 
{
    V5 v;
    uint d;
};

uint rand(inout RNGState state)
{
    uint t;
    t = (state.v.v0 ^ (state.v.v0 >> 2));
    state.v.v0 = state.v.v1;
    state.v.v1 = state.v.v2;
    state.v.v2 = state.v.v3;
    state.v.v3 = state.v.v4;
    state.v.v4 = (state.v.v4 ^ (state.v.v4 << 4)) ^ (t ^ (t << 1));
    state.d += 362437;
    return state.v.v4 + state.d;
}

float rand01(inout RNGState state)
{
    uint64_t urand = rand(state);
    return float(urand) / float(1UL << 32);
}

vec3 rand_in_unit_sphere(inout RNGState rstate)
{
    vec3 ret;
    do{
        ret = vec3(rand01(rstate)*2.0 - 1.0, rand01(rstate)*2.0 - 1.0, rand01(rstate)*2.0 - 1.0);
    } while (length(ret) > 1.0);
    return ret;
}

vec2 rand_in_unit_disk(inout RNGState rstate)
{
    vec2 ret;
    do {
        ret = vec2(rand01(rstate)*2.0 - 1.0, rand01(rstate)*2.0 - 1.0);
    } while (length(ret) > 1.0);
    return ret;
}

vec3 rand_on_unit_sphere(inout RNGState rstate)
{
    float theta = rand01(rstate) * radians(360.0);
    float z = rand01(rstate)*2.0 - 1.0;
    float r = 1.0 - z*z;
    if (r<0.0) r = 0.0;
    r = sqrt(r);
    vec3 ret;
    ret.z = z;
    ret.x = r*cos(theta);
    ret.y = r*sin(theta);
    return ret;
}

vec2 rand_on_unit_circle(inout RNGState rstate)
{
    float theta = rand01(rstate) * radians(360.0);
    vec2 ret;
    ret.x = cos(theta);
    ret.y = sin(theta);
    return ret;
}
''')

vki.Add_Inlcude_Filename('rand_xorwow.shinc')

class RNGInitializer(vki.ShaderViewable):
    def __init__(self):
        xorwow_data = np.fromfile(os.path.dirname(__file__) + '/' + 'xor_wow_data.bin', dtype=np.uint32)
        self.d_xorwow_data = vki.device_vector_from_numpy(xorwow_data)
        self.m_cptr = SVCombine_Create({'data':  self.d_xorwow_data}, '''
void matvec_i(int i, uint v_i, in Comb_#hash# initializer, int offset, inout V5 result)
{
    for (int j = 0; j < 32; j++)
        if ((v_i & (1 << j))!=0)
        {
            int k = (i * 32 + j)*5 + offset;            
            result.v0 ^= get_value(initializer.data, k);
            result.v1 ^= get_value(initializer.data, k + 1);
            result.v2 ^= get_value(initializer.data, k + 2);
            result.v3 ^= get_value(initializer.data, k + 3);
            result.v4 ^= get_value(initializer.data, k + 4);
        }
}

void matvec(in V5 vector, in Comb_#hash# initializer, int offset, inout V5 result)
{
    result.v0 = result.v1 = result.v2 = result.v3 = result.v4 = 0;
    matvec_i(0, vector.v0, initializer, offset, result);
    matvec_i(1, vector.v1, initializer, offset, result);
    matvec_i(2, vector.v2, initializer, offset, result);
    matvec_i(3, vector.v3, initializer, offset, result);
    matvec_i(4, vector.v4, initializer, offset, result);                    
}

void state_init(in Comb_#hash# initializer, uint64_t seed, uint64_t subsequence, inout RNGState state)
{
    if (subsequence>= (1<<18) ) subsequence= (1<<18) -1;

    uint s0 = uint(seed) ^ 0xaad26b49U;
    uint s1 = uint(seed >> 32) ^ 0xf7dcefddU;
    uint t0 = 1099087573U * s0;
    uint t1 = 2591861531U * s1;
    state.d = 6615241 + t1 + t0;
    state.v.v0 = 123456789U + t0;
    state.v.v1 = 362436069U ^ t0;
    state.v.v2 = 521288629U + t1;
    state.v.v3 = 88675123U ^ t1;
    state.v.v4 = 5783321U + t0;

    // apply sequence matrix
    V5 result;
    uint64_t p = subsequence;
    int i_mat = 0;

    while (p!=0 && i_mat<7)
    {
        for (uint t = 0; t < (p & 3); t++)
        {
            matvec(state.v, initializer, i_mat*800, result);
            state.v = result;
        }
        p >>= 2;
        i_mat++;
    }
    
    for (uint t = 0; t < (p & 0xF); t++)
    {
        matvec(state.v, initializer, i_mat*800, result);
        state.v = result;
    }
}
''')

        
    rand_init = vki.Computer(['initializer', 'arr_out'], '''
void main()
{
    uint id = gl_GlobalInvocationID.x;
    if (id >= get_size(arr_out)) return;
    RNGState state;
    state_init(initializer, 1234, uint64_t(id), state);
    set_value(arr_out, id, state);
}
''', type_locked=True)

    def InitRNGVector(self, arr_out):
        blocks = int((arr_out.size() + 127)/128)
        self.rand_init.launch(blocks, 128, [self, arr_out])





