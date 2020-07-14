import glm
import VkInline as vki
from .sky import *

class Scene:
    def __init__(self):
        self.m_sky = GradientSky()
        self.m_geo_lists = {}
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

    def add_geometry(self, geo):
        view_type = geo.name_view_type()
        if not view_type in self.m_geo_lists:
            self.m_geo_lists[view_type] = {'name': geo.name_lst, 'lst': [] };
            self.m_need_update_pipeline = True
        self.m_geo_lists[view_type]['lst'] += [geo]
        self.m_need_update = True


    def update(self):
        if self.m_need_update:
            print("Building TLAS..")
            self.m_lst_geo_lsts =[]
            lst_blas = []
            for key in self.m_geo_lists:
                sublist = self.m_geo_lists[key]['lst']
                self.m_lst_geo_lsts += [vki.SVObjVector(sublist)]
                sublist_blas = [(obj.m_blas, obj.m_modelMat) for obj in sublist]
                lst_blas += [sublist_blas]
            self.m_tlas = vki.TopLevelAS(lst_blas)
            self.m_need_update = False

    
