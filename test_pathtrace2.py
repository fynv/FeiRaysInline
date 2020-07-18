import numpy as np
import tinyobjloader
import glm
import VkInline as vki
import FeiRaysInline as fri
from PIL import Image

reader = tinyobjloader.ObjReader()
reader.ParseFromFile('spider.obj')
attrib = reader.GetAttrib()

positions = np.array(attrib.vertices, dtype=np.float32)
positions = np.reshape(positions, (-1, 3))

normals = np.array(attrib.normals, dtype=np.float32)
normals = np.reshape(normals, (-1, 3))

shapes = reader.GetShapes()
lst_vertex_inds = []
lst_normal_inds = []
for shape in shapes:
	for ind in shape.mesh.indices:
		lst_vertex_inds += [ind.vertex_index]
		lst_normal_inds += [ind.normal_index]

vertex_inds = np.array(lst_vertex_inds, dtype=np.uint32)
normal_inds = np.array(lst_normal_inds, dtype=np.uint32)

VK_FORMAT_R8G8B8A8_SRGB = 43

width = 900
height = 600

scene = fri.Scene()

sky_cube = np.array(Image.open('cubemap.png').convert('RGBA'))
gpu_sky_cube = vki.Cubemap(512, 512, VK_FORMAT_R8G8B8A8_SRGB)
gpu_sky_cube.upload(sky_cube)

sky = fri.TexturedSky(scene.add_cubemap(gpu_sky_cube))
scene.set_sky(sky)

'''
sky = fri.GradientSky((0.0,0.0,0.0), (0.0,0.0,0.0))
scene.set_sky(sky)
'''

'''
point_light0 = fri.PointLight((-5.0, 20.0, -5.0), (0.5, 1.0, 0.5), 1000.0)
scene.add_object(point_light0)

point_light1 = fri.PointLight((5.0, 20.0, 5.0), (1.0, 0.5, 0.5), 1000.0)
scene.add_object(point_light1)
'''

'''
sphere_light0 = fri.SphereLight((-5.0, 20.0, -5.0), 0.5, (0.5, 1.0, 0.5), 1500.0)
scene.add_object(sphere_light0)

sphere_light1 = fri.SphereLight((5.0, 20.0, 5.0), 0.5, (1.0, 0.5, 0.5), 1500.0)
scene.add_object(sphere_light1)
'''

'''
dis_light = fri.DistanceLight((-1.0, 4.0, -1.0), (1.0, 1.0, 0.8), 5.0)
scene.add_object(dis_light)
'''

sun_light = fri.SunLight((-1.0, 4.0, -1.0), 0.05, (1.0, 1.0, 0.8), 750.0)
scene.add_object(sun_light)

identity = glm.identity(glm.mat4)

model = glm.translate(identity, glm.vec3(0.0, -1000.0, 0.0))
model = glm.scale(model, glm.vec3(1000.0, 1000.0, 1000.0))
sphere = fri.LambertSphere(model, (0.5, 0.5, 0.5))
scene.add_object(sphere)

model = glm.translate(identity, glm.vec3(0.0, 1.0, 0.0))
model = glm.scale(model, glm.vec3(0.03, 0.03, 0.03))
spider = fri.LambertMesh(positions, normals, vertex_inds, normal_inds, model, (0.1, 0.04, 0.02))
scene.add_object(spider)

model = glm.translate(identity, glm.vec3(-4.0, 1.0, 3.0))
sphere = fri.LambertSphere(model, (0.4, 0.2, 0.1))
scene.add_object(sphere)

model = glm.translate(identity, glm.vec3(4.0, 1.0, -3.0))
sphere = fri.LambertSphere(model, (0.7, 0.6, 0.5))
scene.add_object(sphere)

world2camera = glm.lookAt(glm.vec3(-15.0, 5.0, 3.0), glm.vec3(0.0, 0.0, 0.0), glm.vec3(0.0, 1.0, 0.0))
camera2world = glm.inverse(world2camera)
camera = fri.PerspectiveCamera(width, height, camera2world, 20.0, 0.2, 15.0)
pt = fri.PathTracer(camera)

pt.trace(scene, 100)
img_out = camera.m_film.download_srgb()
Image.fromarray(img_out, 'RGBA').save('output.png')


