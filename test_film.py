import numpy as np
import VkInline as vki
import FeiRaysInline as fri
from PIL import Image

width = 640
height = 480

film = fri.Film(width, height)

kernel = vki.Computer(['width', 'height', 'film'],
'''
void main()
{
    int x = int(gl_GlobalInvocationID.x);
    int y = int(gl_GlobalInvocationID.y);
    if (x >= width || y>=height) return;

    float u = (float(x)+0.5)/float(width);
    float v = (float(y)+0.5)/float(height);

    incr_pixel(film, x, y, vec3(u, v, 0));
}
''')

blockSize = (8,8)
gridSize = (int((width+7)/8), int((height+7)/8))
kernel.launch(gridSize, blockSize, [vki.SVInt32(width), vki.SVInt32(height), film])
film.inc_times_exposure()

img_out = film.download_srgb()
Image.fromarray(img_out, 'RGBA').save('output.png')
