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
    // Reserved GUI colors encode a live scale for this HUD only. Native text
    // measurement stays constant; all artwork/text/head geometry scales together.
    if (abs(ProjMat[3][3] - 1.0) < 0.001 && ProjMat[1][1] < 0.0 &&
        marker.b == 37 && (marker.r == 3 || marker.r == 4) && marker.g >= 50 && marker.g <= 250) {
        if (marker.r == 4) {
            int corner = gl_VertexID & 3;
            position.x += corner < 2 ? -5.0 : 5.0;
            position.y += ((corner == 0 || corner == 3) ? -5.0 : 5.0) + 17.5;
        }
        float scale = float(marker.g) / 200.0;
        float centerX = -ProjMat[3][0] / ProjMat[0][0];
        // BossHealthOverlay centers with integer division. Correct its half-pixel
        // offset on odd GUI widths before scaling the 194px artwork.
        position.x += fract(centerX);
        position.xy = vec2(centerX, 4.0) + (position.xy - vec2(centerX, 4.0)) * scale;
        vertexColor = vec4(1.0,1.0,1.0,Color.a);
    }
    gl_Position = ProjMat * position;
    sphericalVertexDistance = fog_spherical_distance(Position);
    cylindricalVertexDistance = fog_cylindrical_distance(Position);
    texCoord0 = UV0;
}
