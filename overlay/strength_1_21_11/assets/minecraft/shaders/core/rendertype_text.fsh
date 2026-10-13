#version 330

#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:dynamictransforms.glsl>

uniform sampler2D Sampler0;
in float sphericalVertexDistance;
in float cylindricalVertexDistance;
in vec4 vertexColor;
in vec2 texCoord0;
flat in int parkourPanelPhase;
flat in float parkourPanelProgress;
out vec4 fragColor;

void main() {
    vec4 texel = texture(Sampler0, texCoord0);
    vec4 color = texel * vertexColor * ColorModulator;
    if (color.a < 0.1) discard;
    // Colored masks only exist in the panel. Red encodes the progress pixel's horizontal position.
    if (parkourPanelPhase >= 0 && texel.g < 0.01 && texel.b > 0.99) {
        vec3 accent = vec3(0.16, 0.91, 1.0);
        if (parkourPanelPhase == 0 || parkourPanelPhase == 2) accent = vec3(1.0, 0.84, 0.0);
        if (parkourPanelPhase == 3) accent = vec3(0.80, 0.40, 1.0);
        if (parkourPanelPhase == 4) accent = vec3(0.22, 1.0, 0.53);
        bool track = texel.b < 0.999;
        float position = (texel.r * 255.0 - 1.0) / 253.0;
        color.rgb = (track && position > parkourPanelProgress ? vec3(0.22, 0.26, 0.32) : accent) * ColorModulator.rgb;
    }
    fragColor = apply_fog(color, sphericalVertexDistance, cylindricalVertexDistance,
        FogEnvironmentalStart, FogEnvironmentalEnd, FogRenderDistanceStart, FogRenderDistanceEnd, FogColor);
}
