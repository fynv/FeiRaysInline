import numpy as np
import glm
import VkInline as vki
import FeiRaysInline as fri
from PIL import Image

VK_FORMAT_R8G8B8A8_SRGB = 43

width = 640
height = 480

world2camera = glm.lookAt(glm.vec3(0.0, 0.0, 0.0), glm.vec3(1.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))
camera2world = glm.inverse(world2camera)
camera = fri.PerspectiveCamera(width, height, camera2world , 90.0)

# sky = fri.GradientSky()

sky_cube = np.array(Image.open('cubemap.png').convert('RGBA'))
gpu_sky_cube = vki.Cubemap(512, 512, VK_FORMAT_R8G8B8A8_SRGB)
gpu_sky_cube.upload(sky_cube)

sky = fri.TexturedSky(0)


kernel = vki.Computer(['width', 'height', 'camera', 'sky'],
'''
void main()
{
    int x = int(gl_GlobalInvocationID.x);
    int y = int(gl_GlobalInvocationID.y);
    if (x >= width || y>=height) return;

    float fx = float(x)+0.5;
    float fy = float(y)+0.5;

    vec3 origin, dir;
    generate_ray(camera, fx, fy, 0.0, 0.0, origin, dir);
    Spectrum col = get_sky_color(sky, dir);
    incr_pixel(camera.film, x, y, col);
}
''')


blockSize = (8,8)
gridSize = (int((width+7)/8), int((height+7)/8))
kernel.launch(gridSize, blockSize, [vki.SVInt32(width), vki.SVInt32(height), camera, sky], cubemaps = [gpu_sky_cube])
camera.m_film.inc_times_exposure()

img_out = camera.m_film.download_srgb()
Image.fromarray(img_out, 'RGBA').save('output.png')

