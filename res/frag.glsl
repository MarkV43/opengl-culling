#version 330 core
precision mediump float;

uniform vec3 cameraPos;
uniform vec3 propCamPos;
uniform int invert;

out vec4 FragColor;

in vec3 Normal;
in vec4 WorldPos;

void main() {
    vec3 propDir = vec3(WorldPos) - propCamPos;
    if ((invert > 0) != (dot(propDir, Normal) > 0)) {
        discard;
    }

    vec3 rayDir = normalize(vec3(WorldPos) - cameraPos);

    float perp = dot(rayDir, Normal);
    float minSh = perp > 0 ? 0.2 : 0.6;
    float maxSh = perp > 0 ? 0.6 : 1.0;

    float shade = mix(minSh, maxSh, abs(perp));
    vec3 color = abs(Normal);

    FragColor = vec4(color * shade, 1.0);

    // mix
    // FragColor = vec4(abs(rayDir), 1.0);
}