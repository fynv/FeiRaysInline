import numpy as np
import glm
import VkInline as vki
import FeiRaysInline as fri
from PIL import Image

VK_FORMAT_R8G8B8A8_SRGB = 43

width = 900
height = 600

scene = fri.Scene()

sky_cube = np.array(Image.open('cubemap.png').convert('RGBA'))
gpu_sky_cube = vki.Cubemap(512, 512, VK_FORMAT_R8G8B8A8_SRGB)
gpu_sky_cube.upload(sky_cube)

sky = fri.TexturedSky(scene.add_cubemap(gpu_sky_cube))
scene.set_sky(sky)

identity = glm.identity(glm.mat4)

model = glm.translate(identity, glm.vec3(0.0, -1000.0, 0.0))
model = glm.scale(model, glm.vec3(1000.0, 1000.0, 1000.0))
sphere = fri.ColoredUnitSphere(model, (0.5, 0.5, 0.5))
scene.add_geometry(sphere)

model = glm.translate(identity, glm.vec3(0.0, 1.0, 0.0))
sphere = fri.ColoredUnitSphere(model, (1.0, 1.0, 1.0))
scene.add_geometry(sphere)

model = glm.translate(identity, glm.vec3(-4.0, 1.0, 0.0))
sphere = fri.ColoredUnitSphere(model, (0.4, 0.2, 0.1))
scene.add_geometry(sphere)

model = glm.translate(identity, glm.vec3(4.0, 1.0, 0.0))
sphere = fri.ColoredUnitSphere(model, (0.7, 0.6, 0.5))
scene.add_geometry(sphere)

world2camera = glm.lookAt(glm.vec3(15.0, 3.0, 3.0), glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))
camera2world = glm.inverse(world2camera)
camera = fri.PerspectiveCamera(width, height, camera2world, 20.0, 0.2, 12.0)
pt = fri.PathTracer(camera)

pt.trace(scene, 100)
img_out = camera.m_film.download_srgb(2.0)
Image.fromarray(img_out, 'RGBA').save('output.png')


