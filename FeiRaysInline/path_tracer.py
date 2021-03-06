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

    def trace(self, scene, num_iter = 100, interval = -1):
        if self.m_rng_states == None:
            print("Initializing RNG states..")
            self.m_rng_states = vki.SVVector('RNGState', self.m_batch_size)
            initializer = RNGInitializer()
            initializer.InitRNGVector(self.m_rng_states)

        scene.update()

        sunlight = ''

        estimate_light = ''
        for key in scene.m_obj_lists:
            sublist = scene.m_obj_lists[key]
            if sublist['is_light_source']:
                estimate_light += self.template_estimate_light.format(name_list = sublist['name'])
                if sublist['name'] == 'sun_lights':
                    sunlight = self.sunlight
                    
        miss = self.payload + self.template_miss.format(sunlight=sunlight) + self.template_update_payload.format(estimate_light='')

        print("Doing ray-tracing..")

        lst_param_names = ['camera','states', 'sky', 'pdf_lights'] 
        for key in scene.m_obj_lists:
            sublist = scene.m_obj_lists[key]
            lst_param_names += [sublist['name']]

        hit_shaders = []
        for key in scene.m_obj_lists:
            sublist = scene.m_obj_lists[key]
            if sublist['is_geometry']:                
                closest_hit  = self.payload + sublist['closest_hit'] + self.template_update_payload.format(estimate_light=estimate_light)
                intersection = sublist['intersection']                
                hit_shaders += [vki.HitShaders(closest_hit = closest_hit, intersection = intersection)]


        ray_tracer = vki.RayTracer(lst_param_names, self.raygen, [miss], hit_shaders)

        if interval == -1:
            interval = num_iter;

        lst_params = [self.m_camera, self.m_rng_states, scene.m_sky, scene.m_pdf_lights] + scene.m_lst_obj_lsts


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


    payload = '''
struct Payload
{
    bool is_visibility;

    RNGState rng_state;
    int depth;
    Spectrum color;
    Spectrum f_att;
    bool finished;
    vec3 origin;
    vec3 direction;    

    float distance;
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

    const float russian_roulette_factor = 0.1;

    uint cullMask = 0xff;
    float tmin = 0.001;
    float tmax = 1000000.0;

    payload.depth = 0;
    while (payload.depth < 10)
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
        payload.is_visibility = false;
        traceRayEXT(arr_tlas[0], rayFlags, cullMask, 0, 0, 0, payload.origin, tmin, payload.direction, tmax, 0);

        if (payload.finished) break;

        payload.depth++;
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
    template_update_payload = '''
layout(location = 0) rayPayloadInEXT Payload payload;

void update_payload_visibility(in HitInfo hitinfo)
{{
    payload.distance = hitinfo.t;
}}

void update_payload(in HitInfo hitinfo)
{{
    if (payload.is_visibility)
    {{
        update_payload_visibility(hitinfo);
        return;
    }}

#ifdef HAS_EMISSION
    incr(payload.color, mult(Le(hitinfo, -payload.direction, payload.depth), payload.f_att));
#endif
    
#ifdef HAS_BSDF    
    payload.origin += payload.direction*hitinfo.t;

    if (get_size(pdf_lights.cdf)>1)
    {{
        float sample_light = rand01(payload.rng_state);
        float pdf_light;
        uint light_id = SampleDiscrete(pdf_lights, sample_light, pdf_light);

        vec3 dir;
        float light_dis;
        float pdfw=0.0;
        Spectrum intesity;

        {estimate_light}

        if (pdfw>0.0)
        {{
            uint cullMask = 0xff;
            float tmin = 0.001;
            float tmax = 1000000.0;

            uint rayFlags = gl_RayFlagsOpaqueEXT;
            payload.is_visibility = true;
            traceRayEXT(arr_tlas[0], rayFlags, cullMask, 0, 0, 0, payload.origin, tmin, dir, tmax, 0);

            if (payload.distance<0.0 || (light_dis>0.0 && light_dis - 0.001 <= payload.distance))
            {{
                Spectrum f = evaluate_bsdf(hitinfo, -payload.direction, dir);
                Spectrum att = mult(payload.f_att, div(f, pdfw));               
                incr(payload.color, mult(intesity, att));
            }}
        }}
    }}

    vec3 wi;
    float path_pdf;
    Spectrum f = sample_bsdf(hitinfo, -payload.direction, wi, payload.rng_state, path_pdf);
    if (path_pdf <= 0.0)
    {{
        payload.finished = true;
        return;       
    }}
    amplify(payload.f_att, div(f, path_pdf));    
    payload.direction = wi;
#else
    payload.finished = true;
#endif
}}
'''

    template_estimate_light = '''
        if (light_id>={name_list}.id_offset && light_id-{name_list}.id_offset<get_size({name_list}))
        {{
            uint i = light_id-{name_list}.id_offset;
            intesity = sample_l(get_value({name_list}, i), payload.origin, payload.rng_state, dir, light_dis, pdfw);
            if (pdfw>0.0)
                pdfw*= pdf_light;
        }}
'''

    template_miss = '''
struct HitInfo
{{
    float t;
    int light_id;
}};

Spectrum Le(in HitInfo hitinfo, in vec3 wo, int depth_iter)
{{
    Spectrum color = get_sky_color(sky, -wo);
    {sunlight}
    return color;
}}

void update_payload(in HitInfo hitinfo);

void main()
{{
    HitInfo hitinfo;
    hitinfo.t = -1.0;
    hitinfo.light_id = 0;
    update_payload(hitinfo);
}}

#define HAS_EMISSION
'''
    sunlight = '''
    if (depth_iter<1)
    {                    
        for (uint i=0; i<get_size(sun_lights); i++)
        {
            vec4 dir_radian = get_value(sun_lights, i).dir_radian;
            float theta = acos(dot(-wo, dir_radian.xyz));
            if (theta<dir_radian.w)
            {
                incr(color, get_value(sun_lights, i).intensity);
                break;
            }
        }
    }
'''

