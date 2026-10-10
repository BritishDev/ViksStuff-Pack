// Original per-material energy shader. Tagged orb texels only; no screen post-process.
// The second chroma check keeps ordinary alpha textures on their existing render path.
#moj_import <minecraft:globals.glsl>

bool viks_is_orb(vec4 texel) {
    if (abs(texel.a * 255.0 - 249.0) > 0.28) return false;
    float top = max(max(texel.r, texel.g), texel.b);
    if (top < 0.05) return false;
    vec3 chroma = texel.rgb / top;
    return distance(chroma, vec3(242.0 / 255.0, 247.0 / 255.0, 1.0)) < 0.025
        || distance(chroma, vec3(1.0, 36.0 / 255.0, 61.0 / 255.0)) < 0.025;
}

vec4 viks_orb_energy(vec4 texel, vec2 uv) {
    float phase = GameTime * 1800.0;
    float pulse = 1.10 + 0.06 * sin(phase);
    float signal = pow(max(0.0, sin((uv.x + uv.y) * 240.0 - phase * 1.4)), 20.0);
    float edge = clamp(length(fwidth(texel.rgb)) * 2.0, 0.0, 0.14);
    vec3 glow = texel.rgb * (pulse + signal * 0.14) + vec3(edge);
    return vec4(clamp(glow, 0.0, 1.0), 1.0);
}
