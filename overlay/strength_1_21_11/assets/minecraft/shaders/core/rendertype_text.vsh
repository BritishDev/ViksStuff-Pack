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

void main() {
    vec4 position = ModelViewMat * vec4(Position, 1.0);
    vertexColor = Color * texelFetch(Sampler2, UV2 / 16, 0);
    ivec3 marker = ivec3(round(Color.rgb * 255.0));
    // Only the runner's reserved GUI head marker: native 8x8 head -> centered 16x16 portrait.
    if (abs(ProjMat[3][3] - 1.0) < 0.001 && ProjMat[1][1] < 0.0 &&
        marker == ivec3(4,254,37)) {
        int corner = gl_VertexID & 3;
        position.x += corner < 2 ? -4.0 : 4.0;
        position.y += ((corner == 0 || corner == 3) ? -4.0 : 4.0) + 5.0;
        vertexColor = vec4(1.0,1.0,1.0,Color.a);
    }
    gl_Position = ProjMat * position;
    sphericalVertexDistance = fog_spherical_distance(Position);
    cylindricalVertexDistance = fog_cylindrical_distance(Position);
    texCoord0 = UV0;
}
