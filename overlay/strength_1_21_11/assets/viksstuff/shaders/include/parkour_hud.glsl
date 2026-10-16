// Shared by ordinary, intensity and see-through text pipelines.
void parkourHud(inout vec4 position, inout vec4 vertexColor) {
    ivec3 marker = ivec3(round(Color.rgb * 255.0));
    // A dedicated title glyph expands to an opaque full-screen curtain. No world shaders are replaced.
    if (abs(ProjMat[3][3] - 1.0) < 0.001 && marker == ivec3(2, 1, 38)) {
        int corner = gl_VertexID & 3;
        float x = corner < 2 ? -1.01 : 1.01;
        float y = (corner == 0 || corner == 3) ? 1.01 : -1.01;
        position.x = (x - ProjMat[3][0]) / ProjMat[0][0];
        position.y = (y - ProjMat[3][1]) / ProjMat[1][1];
        vertexColor = vec4(0.0, 0.0, 0.0, Color.a);
        return;
    }
    // Reserved GUI colors encode a live scale for this HUD only. Native text
    // measurement stays constant; all artwork/text/head geometry scales together.
    if (abs(ProjMat[3][3] - 1.0) < 0.001 &&
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
        float topY = (1.0 - ProjMat[3][1]) / ProjMat[1][1];
        position.xy = vec2(centerX, topY + 4.0) + (position.xy - vec2(centerX, topY + 4.0)) * scale;
        vertexColor = vec4(1.0,1.0,1.0,Color.a);
    }
}
