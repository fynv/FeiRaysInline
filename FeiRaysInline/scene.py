import glm
import VkInline as vki
from .sky import *

class Scene:
    def __init__(self):
        self.m_sky = GradientSky()
        self.m_obj_lists = {}
        self.m_need_update = True
        self.m_tex2d_list = []
        self.m_tex3d_list = []
        self.m_cubemap_list = []

    def add_texture2d(self, tex2d):
        idx = len(self.m_tex2d_list)
        self.m_tex2d_list += [tex2d]
        return idx

    def add_texture3d(self, tex3d):
        idx = len(self.m_tex3d_list)
        self.m_tex3d_list += [tex3d]
        return idx

    def add_cubemap(self, cubemap):
        idx = len(self.m_cubemap_list)
        self.m_cubemap_list += [cubemap]
        return idx

    def set_sky(self, sky):
        self.m_sky = sky

    def add_object(self, obj):
        view_type = obj.name_view_type()
        if not view_type in self.m_obj_lists:
            sublist = {'name': obj.name_lst, 'is_geometry': obj.is_geometry, 'is_light_source': obj.is_light_source, 'lst': [] }            
            if obj.is_geometry:
                sublist['closest_hit'] = obj.closest_hit
                sublist['intersection'] = None
                if hasattr(obj, 'intersection'):
                    sublist['intersection'] = obj.intersection
            self.m_obj_lists[view_type] = sublist
        self.m_obj_lists[view_type]['lst'] += [obj]
        self.m_need_update = True

    def update(self):
        if self.m_need_update:
            print("Building TLAS..")
            self.m_lst_obj_lsts =[]
            lst_blas = []
            power_lights = []
            for key in self.m_obj_lists:
                sublist = self.m_obj_lists[key]
                self.m_lst_obj_lsts += [vki.SVObjVector(sublist['lst'])]
                if sublist['is_geometry']:
                    sublist_blas = [(obj.m_blas, obj.m_modelMat) for obj in sublist['lst']]
                    lst_blas += [sublist_blas]
                if sublist['is_light_source']:
                    power_lights += [light.power() for light in sublist['lst']]
            self.m_tlas = vki.TopLevelAS(lst_blas)
            

            sum_power = 0.0
            for p in power_lights:
                sum_power += p

            pdf = 0.0
            light_pdf = [0.0]
            for p in power_lights:
                pdf += p
                light_pdf += [pdf/sum_power]

            self.m_pdf_lights = vki.device_vector_from_list(light_pdf, 'float')
            self.m_need_update = False

    
