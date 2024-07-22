#version 330 core
precision mediump float;

uniform mat4 projection;
uniform mat4 model;
uniform mat4 view;

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;

out vec3 Normal;
out vec4 WorldPos;

void main() {
    WorldPos = model * vec4(aPos, 1.0);
    gl_Position = projection * view * WorldPos;
    Normal = aNormal;
}