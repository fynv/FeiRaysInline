import numpy as np
import glm
import VkInline as vki
from .spectrum import *
from .geometry import *
from .interaction import *

class LambertMesh(Geometry):
    def __init__(self, positions, normals, indices_pos, indices_norm, modelMat = glm.identity(glm.mat4), color = (1.0, 1.0, 1.0)):
        Geometry.__init__(self, modelMat)        
        self.m_gpuPos = vki.device_vector_from_numpy(positions)        
        self.m_gpuNorm = vki.device_vector_from_numpy(normals)
        self.m_gpuIndPos = vki.device_vector_from_numpy(indices_pos)
        self.m_gpuIndNorm = vki.device_vector_from_numpy(indices_norm)
        self.m_blas = vki.BaseLevelAS(self.m_gpuIndPos, self.m_gpuPos)

        vert0 = positions[0]
        self.m_aabb = np.array([vert0[0], vert0[1], vert0[2], vert0[0], vert0[1], vert0[2]], dtype = np.float32)
        for vert in positions:
            self.m_aabb[0] = min(self.m_aabb[0], vert[0])
            self.m_aabb[1] = min(self.m_aabb[1], vert[1])
            self.m_aabb[2] = min(self.m_aabb[2], vert[2])
            self.m_aabb[3] = max(self.m_aabb[3], vert[0])
            self.m_aabb[4] = max(self.m_aabb[4], vert[1])
            self.m_aabb[5] = max(self.m_aabb[5], vert[2])

        self.d_normMat = vki.SVMat4x4(self.m_normMat)
        self.d_color  = Spectrum(color)
        self.m_cptr = SVCombine_Create({'indices': self.m_gpuIndNorm, 'normals': self.m_gpuNorm, 'normalMat':  self.d_normMat, 'color': self.d_color }, '''
void closethit(in Comb_#hash# self, int primitiveId, in vec3 barycentrics, inout {HitInfo_Lambert} hitinfo)
{{    
    uint i0 = get_value(self.indices, 3 * primitiveId);
    uint i1 = get_value(self.indices, 3 * primitiveId + 1);
    uint i2 = get_value(self.indices, 3 * primitiveId + 2);

    vec3 norm0 = get_value(self.normals, i0);
    vec3 norm1 = get_value(self.normals, i1);
    vec3 norm2 = get_value(self.normals, i2);

    vec3 normal = norm0 * barycentrics.x + norm1 * barycentrics.y + norm2 * barycentrics.z;
    normal = normalize((self.normalMat * vec4(normal, 0.0)).xyz);   

    hitinfo.lambert.color = self.color;    
    hitinfo.normal = normal;

}}
'''.format(HitInfo_Lambert = Name_HitInfo_Lambert))

    name_lst = 'lambert_meshes'
    is_light_source = False
    intersection = None
    closest_hit ='''    
hitAttributeEXT vec2 attribs;
#define HitInfo {HitInfo_Lambert}
void update_payload(in HitInfo hitinfo);
void main()
{{
    vec3 barycentrics = vec3(1.0 - attribs.x - attribs.y, attribs.x, attribs.y);
    HitInfo hitinfo;
    hitinfo.t = gl_HitTEXT;
    closethit(get_value(lambert_meshes, gl_InstanceCustomIndexEXT), gl_PrimitiveID, barycentrics, hitinfo);
    update_payload(hitinfo);
}}
'''.format(HitInfo_Lambert = Name_HitInfo_Lambert) + define_features(Name_HitInfo_Lambert)


