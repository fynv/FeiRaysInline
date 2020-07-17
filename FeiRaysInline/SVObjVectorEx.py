import numpy as np
import VkInline as vki
from VkInline.SVCombine import *

class SVObjVectorEx(vki.ShaderViewable):
    def __init__(self, lst_svobjs, objIdOffset):
        self.m_size = vki.SVUInt32(len(lst_svobjs))
        self.m_buf = vki.SVObjBuffer(lst_svobjs)
        self.m_id_offset = vki.SVUInt32(objIdOffset)
        self.m_cptr = SVCombine_Create({'size':  self.m_size, 'data': self.m_buf, 'id_offset': self.m_id_offset}, '''
uint get_size(in Comb_#hash# vec)
{{
     return vec.size;
}}

{0} get_value(in Comb_#hash# vec, in uint id)
{{
    return vec.data[id].v;
}}
'''.format(self.name_elem_type()))

    def name_elem_type(self):
        return self.m_buf.name_elem_type()

    def elem_size(self):
        return self.m_buf.elem_size()

    def size(self):
        return self.m_buf.size()
