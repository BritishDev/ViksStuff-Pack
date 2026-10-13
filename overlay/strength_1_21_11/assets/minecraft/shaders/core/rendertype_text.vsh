#version 330

#moj_import <minecraft:fog.glsl>
#moj_import <minecraft:dynamictransforms.glsl>
#moj_import <minecraft:projection.glsl>

in vec3 Position;
in vec4 Color;
in vec2 UV0;
in ivec2 UV2;
uniform sampler2D Sampler2;
out float sphericalVertexDistance;
out float cylindricalVertexDistance;
out vec4 vertexColor;
out vec2 texCoord0;
flat out int parkourPanelPhase;
flat out float parkourPanelProgress;

void main() {
    gl_Position = ProjMat * ModelViewMat * vec4(Position, 1.0);
    sphericalVertexDistance = fog_spherical_distance(Position);
    cylindricalVertexDistance = fog_cylindrical_distance(Position);
    vertexColor = Color * texelFetch(Sampler2, UV2 / 16, 0);
    texCoord0 = UV0;
    parkourPanelPhase = -1;
    parkourPanelProgress = 1.0;
    ivec3 marker = ivec3(round(Color.rgb * 255.0));
    // Only reserved panel colors in the orthographic GUI path. World text follows vanilla.
    if (abs(ProjMat[3][3] - 1.0) < 0.001 && ProjMat[1][1] < 0.0 &&
        marker.r == 1 && marker.g >= 1 && marker.b >= 37 && marker.b <= 41) {
        parkourPanelPhase = marker.b - 37;
        parkourPanelProgress = float(marker.g - 1) / 254.0;
        vertexColor = vec4(1.0, 1.0, 1.0, Color.a);
    }
}
