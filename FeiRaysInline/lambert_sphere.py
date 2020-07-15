import numpy as np
import glm
import VkInline as vki
from .sphere import *
from .interaction import *

class LambertSphere(Sphere):
	def __init__(self, modelMat = glm.identity(glm.mat4), color = (1.0, 1.0, 1.0)):
		Sphere.__init__(self, 'lambert_spheres', Name_HitInfo_Lambert)
		self.m_modelMat = modelMat
		self.m_normMat = glm.transpose(glm.inverse(modelMat))
		aabb = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, 1.0], dtype = np.float32)
		d_aabb = vki.device_vector_from_numpy(aabb)
		self.m_blas = vki.BaseLevelAS(gpuAABB = d_aabb)
		self.d_normMat = vki.SVMat4x4(self.m_normMat)
		self.d_color  = vki.SVVec3(glm.vec3(color))
		self.m_cptr = SVCombine_Create({'normalMat':  self.d_normMat, 'color': self.d_color }, '''
void closethit(in Comb_#hash# sphere, in vec3 hitpoint, inout {HitInfo_Lambert} hitinfo)
{{
	from_rgb(hitinfo.lambert.color, sphere.color);
	hitinfo.normal = normalize((sphere.normalMat * vec4(hitpoint, 0.0)).xyz);	
}}
'''.format(HitInfo_Lambert = Name_HitInfo_Lambert))





