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

    def add_object(self, obj, isGeometry = False, isLightSource = False):
        view_type = obj.name_view_type()
        if not view_type in self.m_obj_lists:
            self.m_obj_lists[view_type] = {'name': obj.name_lst, 'is_geometry': isGeometry, 'is_light_source': isLightSource, 'lst': [] };
            self.m_need_update_pipeline = True
        self.m_obj_lists[view_type]['lst'] += [obj]
        self.m_need_update = True

    def add_geometry(self, geo):
        self.add_object(geo, isGeometry = True)

    def add_light_source(self, light_source):
        self.add_object(light_source, isLightSource = True)

    def update(self):
        if self.m_need_update:
            print("Building TLAS..")
            self.m_lst_obj_lsts =[]
            lst_blas = []
            for key in self.m_obj_lists:
                sublist = self.m_obj_lists[key]
                self.m_lst_obj_lsts += [vki.SVObjVector(sublist['lst'])]
                if sublist['is_geometry']:
                    sublist_blas = [(obj.m_blas, obj.m_modelMat) for obj in sublist['lst']]
                    lst_blas += [sublist_blas]
            self.m_tlas = vki.TopLevelAS(lst_blas)
            self.m_need_update = False

    
