import numpy as np
import glm
import VkInline as vki
from VkInline.SVCombine import *

class GradientSky(vki.ShaderViewable):
	def __init__(self, color0 = (1.0, 1.0, 1.0), color1 = (0.5, 0.7, 1.0)):
		self.m_color0 = vki.SVVec3(glm.vec3(color0))
		self.m_color1 = vki.SVVec3(glm.vec3(color1))
		self.m_cptr = SVCombine_Create({'color0': self.m_color0, 'color1': self.m_color1}, '''
Spectrum get_sky_color(in Comb_#hash# sky, in vec3 dir)
{
	float t = 0.5 * (dir.y + 1.0);
	Spectrum col;
	from_rgb(col, (1.0 - t)*sky.color0 + t * sky.color1);
	return col;	
}
''')


class TexturedSky(vki.ShaderViewable):
	def __init__(self, texId, transform = glm.identity(glm.mat3)):
		self.m_texId = vki.SVInt32(texId)
		self.m_trans = vki.SVMat3x3(transform)
		self.m_cptr = SVCombine_Create({'texId': self.m_texId, 'transform': self.m_trans}, '''
Spectrum get_sky_color(in Comb_#hash# sky, in vec3 dir)
{
	vec3 direction = sky.transform*dir;
	Spectrum col;
	from_rgb(col, texture(arr_cubemap[sky.texId], direction).rgb);
	return col;	
}
''')

