import numpy as np
import VkInline as vki
from VkInline.SVCombine import *

class Sphere(vki.ShaderViewable):           
    def __init__(self):
        aabb = np.array([-1.0, -1.0, -1.0, 1.0, 1.0, 1.0], dtype = np.float32)
        d_aabb = vki.device_vector_from_numpy(aabb)
        self.m_blas = vki.BaseLevelAS(gpuAABB = d_aabb)        

    intersection = '''
hitAttributeEXT vec3 hitpoint;

void main()
{
    vec3 origin = gl_ObjectRayOriginEXT;
    vec3 direction = gl_ObjectRayDirectionEXT;
    float tMin = gl_RayTminEXT;
    float tMax = gl_RayTmaxEXT;

    const float a = dot(direction, direction);
    const float b = dot(origin, direction);
    const float c = dot(origin, origin) - 1.0;
    const float discriminant = b * b - a * c;

    if (discriminant >= 0)
    {
        const float t1 = (-b - sqrt(discriminant)) / a;
        const float t2 = (-b + sqrt(discriminant)) / a;

        if ((tMin <= t1 && t1 < tMax) || (tMin <= t2 && t2 < tMax))
        {
            float t = t1;
            if (tMin <= t1 && t1 < tMax)
            {
                hitpoint = origin + direction * t1;
            }
            else
            {
                t = t2;
                hitpoint = origin + direction * t2;
            }
            reportIntersectionEXT(t, 0);
        }
    }

}
'''    
    is_geometry = True
