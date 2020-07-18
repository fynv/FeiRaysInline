import numpy as np
import glm
import VkInline as vki
from VkInline.SVCombine import *

class Geometry(vki.ShaderViewable):           
    def __init__(self, modelMat):
        self.m_modelMat = modelMat
        self.m_normMat = glm.transpose(glm.inverse(modelMat))

    def get_world_aabb(self):
        model_x = [self.m_aabb[0], self.m_aabb[3]]
        model_y = [self.m_aabb[1], self.m_aabb[4]]
        model_z = [self.m_aabb[2], self.m_aabb[5]]

        for i in range(2):
            for j in range(2):
                for k in range(2):
                    coord_model = glm.vec4(model_x[i], model_y[j], model_z[k], 1.0)
                    coord_world = self.m_modelMat * coord_model
                    if i==0 and j==0 and k==0:
                        min_corner = glm.vec3(coord_world[0], coord_world[1], coord_world[2])
                        max_corner = glm.vec3(coord_world[0], coord_world[1], coord_world[2])
                    else:
                        min_corner[0] = min(min_corner[0], coord_world[0])
                        min_corner[1] = min(min_corner[1], coord_world[1])
                        min_corner[2] = min(min_corner[2], coord_world[2])
                        max_corner[0] = max(max_corner[0], coord_world[0])
                        max_corner[1] = max(max_corner[1], coord_world[1])
                        max_corner[2] = max(max_corner[2], coord_world[2])

        return np.array([min_corner[0], min_corner[1], min_corner[2], max_corner[0], max_corner[1], max_corner[2]], dtype = np.float32)


    is_geometry = True

