import VkInline as vki
from VkInline.SVCombine import *

class Distribution1D(vki.ShaderViewable):
    def __init__(self, power):
        sum_power = 0.0
        cdf = [0.0]
        for p in power:
            sum_power += p
            cdf += [sum_power]
        cdf = [f/sum_power for f in cdf]
        self.m_cdf = vki.device_vector_from_list(cdf, 'float')
        self.m_cptr = SVCombine_Create({'cdf': self.m_cdf}, '''
uint SampleDiscrete(in Comb_#hash# self, float u, inout float pdf)
{
    if (u<0.0) 
    {
        pdf = 0.0;
        return 0;
    }
    
    uint begin = 0;
    uint end = get_size(self.cdf);

    if (u>=1.0)
    {
        pdf = get_value(self.cdf, end-1) - get_value(self.cdf, end-2);
        return end-1;
    }
    
    while (end > begin +1)
    {
        uint mid = begin + ((end-begin)>>1);
        if (u<get_value(self.cdf, mid))
            end = mid;
        else
            begin = mid;
    }
    pdf = get_value(self.cdf, end) - get_value(self.cdf, end-1);
    return end;
}
''')
