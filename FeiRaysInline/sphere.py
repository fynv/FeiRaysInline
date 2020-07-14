import VkInline as vki
from VkInline.SVCombine import *
from .interaction import *

class Sphere(vki.ShaderViewable):			
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
	tmpl_closest_hit = '''
hitAttributeEXT vec3 hitpoint;
#define HitInfo {hitinfo}
void write_payload(in HitInfo hitinfo);
void main()
{{
	HitInfo hitinfo;
	hitinfo.t = gl_HitTEXT;
	closethit(get_value({sphere_list}, gl_InstanceCustomIndexEXT), hitpoint, hitinfo);
	write_payload(hitinfo);
}}
'''

	def __init__(self, name_sphere_list, type_hitinfo):
		self.name_lst = name_sphere_list
		self.closest_hit = self.tmpl_closest_hit.format(sphere_list = name_sphere_list, hitinfo = type_hitinfo)
		self.closest_hit += define_features(type_hitinfo)
		
