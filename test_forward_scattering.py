import numpy as np
import glm
import VkInline as vki
import FeiRaysInline as fri
from PIL import Image

VK_FORMAT_R8G8B8A8_SRGB = 43

width = 640
height = 480

count = 1 << 18
states = vki.SVVector('RNGState', count)
initializer = fri.RNGInitializer()
initializer.InitRNGVector(states)

world2camera = glm.lookAt(glm.vec3(0.0, 0.0, 10.0), glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))
camera2world = glm.inverse(world2camera)
camera = fri.PerspectiveCamera(width, height, camera2world , 20.0)

sphere_light = fri.SphereLight((0.0, 0.0, 0.0), 1.0, (0.5, 0.5, 0.5), 1.0)


kernel = vki.For(['width', 'height', 'camera', 'sphere_light', 'states'], 'inner', '''
void inner(uint idx)
{
	RNGState state = get_value(states, idx);

	vec3 origin = (camera.camera2world*vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	vec3 dir_center = normalize((camera.camera2world*vec4(0.0, 0.0, -1.0, 0.0)).xyz);
	vec3 dir_x = normalize((camera.camera2world*vec4(1.0, 0.0, 0.0, 0.0)).xyz);
	vec3 dir_y = normalize((camera.camera2world*vec4(0.0, 1.0, 0.0, 0.0)).xyz);

	vec3 dirToLight;
	float distance;
	float pdfw; 
	Spectrum col = sample_l(sphere_light, origin, state, dirToLight, distance, pdfw);	
	float p = pdfw * (camera.size_pix*camera.size_pix*float(camera.film.width)*float(camera.film.height)*dot(dir_center, dirToLight))/(camera.focus_dist*camera.focus_dist);
	amplify(col, 1.0/p);

	vec3 vec_pix = dirToLight * camera.focus_dist / dot(dirToLight, dir_center);

	float x = 0.5*float(camera.film.width) + dot(vec_pix, dir_x)/camera.size_pix;
	float y = 0.5*float(camera.film.height) - dot(vec_pix, dir_y)/camera.size_pix;

	incr_pixel(camera.film, int(x), int(y), col);	

	set_value(states, idx, state);
}
''')

exposure_rate = count / (width*height)
times_submission = 1
kernel.launch_n(count, [vki.SVInt32(width), vki.SVInt32(height), camera, sphere_light, states], times_submission=times_submission)
camera.m_film.inc_times_exposure(exposure_rate*times_submission)

img_out = camera.m_film.download_srgb()
Image.fromarray(img_out, 'RGBA').save('output.png')
