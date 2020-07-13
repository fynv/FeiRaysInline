import math
import VkInline as vki
from VkInline.SVCombine import *
from .film import *

class PerspectiveCamera(vki.ShaderViewable):
	def __init__(self, film_width, film_height, camera2world, vfov, aperture=0.0, focus_dist=1.0):
		self.m_film = Film(film_width, film_height)
		self.m_sv_camera2world = vki.SVMat4x4(camera2world)
		theta = vfov * math.pi / 180.0
		half_height = math.tan(theta*0.5)*focus_dist
		size_pix = half_height * 2.0 / film_height
		lens_radius = aperture * 0.5
		self.m_sv_size_pix = vki.SVFloat(size_pix)
		self.m_sv_lens_radius = vki.SVFloat(lens_radius)
		self.m_sv_focus_dist = vki.SVFloat(focus_dist)
		self.m_cptr = SVCombine_Create({'film':  self.m_film, 'camera2world': self.m_sv_camera2world, 'size_pix': self.m_sv_size_pix, 'lens_radius': self.m_sv_lens_radius, 'focus_dist': self.m_sv_focus_dist}, '''
void generate_ray(in Comb_#hash# camera, float film_x, float film_y, float lens_x, float lens_y, out vec3 origin, out vec3 dir)
{
	origin = vec3(lens_x*camera.lens_radius, lens_y*camera.lens_radius, 0.0);
	origin = (camera.camera2world*vec4(origin, 1.0)).xyz;
	vec3 pos_pix = vec3((film_x - float(camera.film.width)*0.5)*camera.size_pix, (float(camera.film.height)*0.5 - film_y)*camera.size_pix, -camera.focus_dist);
	pos_pix = (camera.camera2world*vec4(pos_pix, 1.0)).xyz;
	dir = normalize(pos_pix - origin);	
}
''')

