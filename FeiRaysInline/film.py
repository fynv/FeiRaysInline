import numpy as np
import VkInline as vki
from VkInline.SVCombine import *

VK_FORMAT_R8G8B8A8_SRGB = 43

class Film(vki.ShaderViewable):
	def __init__(self, width, height):
		self.m_width = width
		self.m_height = height
		self.m_svwidth = vki.SVInt32(width)
		self.m_svheight = vki.SVInt32(height)
		self.m_svbuf = vki.SVBuffer('vec3', width*height)
		self.m_cptr = SVCombine_Create({'data': self.m_svbuf, 'width': self.m_svwidth, 'height': self.m_svheight}, '''
vec3 read_pixel(in Comb_#hash# img, int x, int y)
{
    return img.data[x + y*img.width].v;
}

void write_pixel(in Comb_#hash# img, int x, int y, in vec3 v)
{
    img.data[x + y*img.width].v = v;
}

void incr_pixel(in Comb_#hash# img, int x, int y, in vec3 v)
{
	vec3 col = read_pixel(img, x, y);
	write_pixel(img, x, y, col + v);
}

void incr_pixel(in Comb_#hash# img, int x, int y, in Spectrum col)
{
	incr_pixel(img, x, y, to_xyz(col));
}

''')
		self.m_times_exposure = 0.0

	def inc_times_exposure(self, count = 1.0):
		self.m_times_exposure += count


	film2srgb = vki.Rasterizer(['film', 'times_expo', 'boost'], type_locked=True)
	film2srgb.add_draw_call(vki.DrawCall(
'''
layout (location = 0) out vec2 vUV;
void main() 
{
	vec2 grid = vec2((gl_VertexIndex << 1) & 2, gl_VertexIndex & 2);
	vec2 vpos = grid * vec2(2.0f, 2.0f) + vec2(-1.0f, -1.0f);
	gl_Position = vec4(vpos, 1.0f, 1.0f);
	vUV = grid;
}
''',
'''
layout (location = 0) in vec2 vUV;
layout (location = 0) out vec4 outColor;

void main() 
{
	int x = int(vUV.x * float(film.width));
	int y = int(vUV.y * float(film.height));
	vec3 xyz = read_pixel(film, x, y);
	xyz *= boost/times_expo;
	vec3 rgb = clamp(xyz2rgb(xyz), 0.0, 1.0);
	outColor = vec4(rgb, 1.0);
}
'''))

	def download_srgb(self, boost=1.0):
		sv_times_expo = vki.SVFloat(self.m_times_exposure)
		sv_boost = vki.SVFloat(boost)
		colorBuf = vki.Texture2D(self.m_width, self.m_height, VK_FORMAT_R8G8B8A8_SRGB)
		self.film2srgb.launch([3], [colorBuf], None, [0.5, 0.5, 0.5, 1.0], 1.0, [self, sv_times_expo, sv_boost])
		srgb = np.empty((self.m_height, self.m_width, 4), dtype=np.uint8)
		colorBuf.download(srgb)
		return srgb
