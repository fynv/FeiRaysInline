import glm
import VkInline as vki
from .xorwow import *
from .sky import *

class PathTracer:
    def __init__(self, camera):
        self.m_camera = camera
       
        self.m_batch_size = 1<<18
        if self.m_batch_size>camera.m_film.m_width*camera.m_film.m_height:
            self.m_batch_size = camera.m_film.m_width*camera.m_film.m_height
        self.m_batch_size = int((self.m_batch_size + 63) / 64) * 64

        self.m_rng_states = None

    payload = '''
struct Payload
{
    RNGState rng_state;
    Spectrum color;
    Spectrum f_att;
    bool finished;
    vec3 origin;
    vec3 direction;    
};
'''

    raygen = payload + '''    
layout(location = 0) rayPayloadEXT Payload payload;

void rt_main(int ix, int iy) 
{
    float fx = float(ix)+ rand01(payload.rng_state);
    float fy = float(iy)+ rand01(payload.rng_state);

    vec2 rnd_lens = vec2(0.0, 0.0);
    if (camera.lens_radius>0.0f)
        rnd_lens = rand_in_unit_disk(payload.rng_state);

    from_rgb(payload.color, vec3(0.0, 0.0, 0.0));
    from_rgb(payload.f_att, vec3(1.0, 1.0, 1.0));
    payload.finished = false;

    generate_ray(camera, fx, fy, rnd_lens.x, rnd_lens.y, payload.origin, payload.direction);    

    int depth = 0;
    const float russian_roulette_factor = 0.1;

    uint cullMask = 0xff;
    float tmin = 0.001;
    float tmax = 1000000.0;

    while (depth < 10)
    {
        //  Russian Roulette
        float max_att = max_component_value(payload.f_att);
        if (max_att<russian_roulette_factor)
        {
            max_att /= russian_roulette_factor;
            if (rand01(payload.rng_state)>max_att) break;
            amplify(payload.f_att, 1.0/max_att);
        }       

        uint rayFlags = gl_RayFlagsOpaqueEXT;
        traceRayEXT(arr_tlas[0], rayFlags, cullMask, 0, 0, 0, payload.origin, tmin, payload.direction, tmax, 0);

        if (payload.finished) break;

        depth++;
    }

    incr_pixel(camera.film, ix, iy, payload.color);
}

void main()
{
    int ray_id = int(gl_LaunchIDEXT.x);
    int d = ray_id & 0x3F;
    int b = ray_id >> 6;
    int dx = (d&1)|((d&4)>>1)|((d&16)>>2);
    int dy = ((d&2)>>1)|((d&8)>>2)|((d&32)>>3);

    int step = int(gl_LaunchSizeEXT.x)>>6;
    int bw = (camera.film.width+7)>>3;
    int bh = (camera.film.height+7)>>3;
    int total = bw*bh;

    payload.rng_state = get_value(states, ray_id);

    for (int i=b; i<total; i+=step)
    {
        int i_bx = i%bw;
        int i_by = i/bw;
        int ix = (i_bx<<3) + dx;
        int iy = (i_by<<3) + dy;
        if (ix<camera.film.width && iy<camera.film.height) rt_main(ix, iy);
    }

    set_value(states, ray_id, payload.rng_state);
}
'''
    write_payload = '''
layout(location = 0) rayPayloadInEXT Payload payload;

void write_payload(in HitInfo hitinfo)
{
#ifdef HAS_EMISSION
    incr(payload.color, mult(Le(hitinfo, -payload.direction), payload.f_att));
#endif
    
#ifdef HAS_BSDF
    vec3 wi;
    float path_pdf;
    Spectrum f = sample_bsdf(hitinfo, -payload.direction, wi, payload.rng_state, path_pdf);
    if (path_pdf <= 0.0)
    {
        payload.finished = true;
        return;       
    }
    amplify(payload.f_att, div(f, path_pdf));
    payload.origin += payload.direction*hitinfo.t;
    payload.direction = wi;
#else
    payload.finished = true;
#endif
}
'''

    miss = payload + '''
struct HitInfo
{
    float t;
};

Spectrum Le(in HitInfo hitinfo, in vec3 wo)
{
    return get_sky_color(sky, -wo);
}

void write_payload(in HitInfo hitinfo);

void main()
{
    HitInfo hitinfo;
    hitinfo.t = -1.0;
    write_payload(hitinfo);
}

#define HAS_EMISSION
''' + write_payload

    def trace(self, scene, num_iter = 100, interval = -1):
        if self.m_rng_states == None:
            print("Initializing RNG states..")
            self.m_rng_states = vki.SVVector('RNGState', self.m_batch_size)
            initializer = RNGInitializer()
            initializer.InitRNGVector(self.m_rng_states)

        scene.update()

        print("Doing ray-tracing..")

        lst_param_names = ['camera','states', 'sky'] 
        for key in scene.m_geo_lists:
            sublist = scene.m_geo_lists[key]
            lst_param_names += [sublist['name']]

        hit_shaders = []
        for key in scene.m_geo_lists:
            geo = scene.m_geo_lists[key]['lst'][0]
            closest_hit  = self.payload + geo.closest_hit + self.write_payload
            intersection = None
            if hasattr(geo, 'intersection'):
                intersection = geo.intersection
            hit_shaders += [vki.HitShaders(closest_hit = closest_hit, intersection = intersection)]

        ray_tracer = vki.RayTracer(lst_param_names, self.raygen, [self.miss], hit_shaders)

        if interval == -1:
            interval = num_iter;

        lst_params = [self.m_camera, self.m_rng_states, scene.m_sky] + scene.m_lst_geo_lsts

        i = 0
        while i < num_iter:
            end = i + interval
            if end > num_iter:
                end = num_iter
            ray_tracer.launch(self.m_batch_size, lst_params, [scene.m_tlas], tex2ds=scene.m_tex2d_list, tex3ds=scene.m_tex3d_list, cubemaps=scene.m_cubemap_list, times_submission = end - i)
            self.m_camera.m_film.inc_times_exposure(end - i)
            i = end;

            if i < num_iter:
                print('%.2f%%' % (i / num_iter*100.0))





