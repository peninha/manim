#version 330

uniform vec3 light_source_position;
uniform mat4 to_screen_space;

in vec4 color;
in float fill_all;  // Either 0 or 1e
in float uv_anti_alias_width;

in vec3 xyz_coords;
in vec3 global_unit_normal;
in float orientation;
in vec2 uv_coords;
in vec2 uv_b2;
in float bezier_degree;
in float gloss;

out vec4 frag_color;

// Needed for quadratic_bezier_distance insertion below
float modify_distance_for_endpoints(vec2 p, float dist, float t){
    return dist;
}

// To my knowledge, there is no notion of #include for shaders,
// so to share functionality between this and others, the caller
// replaces this line with the contents of quadratic_bezier_sdf.glsl
#INSERT quadratic_bezier_distance.glsl
#INSERT add_light.glsl


float sdf(){
    if(bezier_degree < 2){
        return abs(uv_coords[1]);
    }
    float u2 = uv_b2.x;
    float v2 = uv_b2.y;
    // For really flat curves, just take the distance to x-axis
    if(abs(v2 / u2) < 0.1 * uv_anti_alias_width){
        return abs(uv_coords[1]);
    }
    // For flat-ish curves, take the curve
    else if(abs(v2 / u2) < 0.5 * uv_anti_alias_width){
        return min_dist_to_curve(uv_coords, uv_b2, bezier_degree);
    }
    // I know, I don't love this amount of arbitrary-seeming branching either,
    // but a number of strange dimples and bugs pop up otherwise.

    // This converts uv_coords to yet another space where the bezier points sit on
    // (0, 0), (1/2, 0) and (1, 1), so that the curve can be expressed implicityly
    // as y = x^2.
    mat2 to_simple_space = mat2(
        v2, 0,
        2 - u2, 4 * v2
    );
    vec2 p = to_simple_space * uv_coords;
    // Sign takes care of whether we should be filling the inside or outside of curve.
    float sn = orientation * sign(v2);
    float Fp = sn * (p.x * p.x - p.y);
    vec2 grad = vec2(
        -2 * p.x * v2,  // del C / del u
        4 * v2 - 4 * p.x * (2 - u2)  // del C / del v
    );
    return Fp / length(grad);
}


void main() {
    if (color.a == 0) discard;
    frag_color = add_light(color, xyz_coords, global_unit_normal, light_source_position, gloss);
    if (fill_all == 1.0) return;
    frag_color.a *= smoothstep(1, 0, sdf() / uv_anti_alias_width);
}
