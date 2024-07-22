from typing import Any
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import glm

from builder import vertices


def createProgram() -> int:
    vertexShaderSource = open("res/vertex.glsl").read()
    fragmentShaderSource = open("res/frag.glsl").read()

    vertexShader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertexShader, [vertexShaderSource])
    glCompileShader(vertexShader)

    success = glGetShaderiv(vertexShader, GL_COMPILE_STATUS)
    if success != GL_TRUE:
        log = glGetShaderInfoLog(vertexShader)
        raise Exception(str(log))

    fragShader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragShader, [fragmentShaderSource])
    glCompileShader(fragShader)

    success = glGetShaderiv(fragShader, GL_COMPILE_STATUS)
    if success != GL_TRUE:
        log = glGetShaderInfoLog(fragShader)
        raise Exception(str(log))

    shaderProgram = glCreateProgram()
    glAttachShader(shaderProgram, vertexShader)
    glAttachShader(shaderProgram, fragShader)
    glLinkProgram(shaderProgram)

    success = glGetProgramiv(shaderProgram, GL_LINK_STATUS)
    if success != GL_TRUE:
        log = glGetProgramInfoLog(shaderProgram)
        raise Exception(str(log))

    glDeleteShader(vertexShader)
    glDeleteShader(fragShader)

    return shaderProgram


def createBuffers(vertices: np.ndarray[Any, np.dtype[np.float32]]) -> tuple[int, int]:
    fsize = glm.sizeof(glm.float32)

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * fsize, None)
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(
        1, 3, GL_FLOAT, GL_FALSE, 6 * fsize, ctypes.c_void_p(3 * fsize)
    )
    glEnableVertexAttribArray(1)

    glBindVertexArray(0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    return vao, vbo


def drawModel(vao, program, model, view, proj, cameraPos, propCam, invert):
    glUseProgram(program)

    modelLoc = glGetUniformLocation(program, "model")
    viewLoc = glGetUniformLocation(program, "view")
    projLoc = glGetUniformLocation(program, "projection")
    cameraPosLoc = glGetUniformLocation(program, "cameraPos")
    propCamLoc = glGetUniformLocation(program, "propCamPos")
    invertLoc = glGetUniformLocation(program, "invert")

    glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm.value_ptr(model))
    glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm.value_ptr(view))
    glUniformMatrix4fv(projLoc, 1, GL_FALSE, glm.value_ptr(proj))
    glUniform3fv(cameraPosLoc, 1, glm.value_ptr(cameraPos))
    glUniform3fv(propCamLoc, 1, glm.value_ptr(propCam))
    glUniform1i(invertLoc, int(invert))

    glBindVertexArray(vao)
    glDrawArrays(GL_TRIANGLES, 0, vertices.shape[0])


def drawProjBox(view, projection):
    invProj = glm.inverse(projection)
    invView = glm.inverse(view)

    drawOrder = [
        (0, 1),
        (0, 2),
        (0, 4),
        (3, 1),
        (3, 2),
        (3, 7),
        (5, 1),
        (5, 4),
        (5, 7),
        (6, 2),
        (6, 4),
        (6, 7),
    ]

    assert len(drawOrder) == 12

    ndcCorners = [
        glm.vec4(-1, -1, -1, 1),  # 0
        glm.vec4(-1, -1, +1, 1),  # 1
        glm.vec4(-1, +1, -1, 1),  # 2
        glm.vec4(-1, +1, +1, 1),  # 3
        glm.vec4(+1, -1, -1, 1),  # 4
        glm.vec4(+1, -1, +1, 1),  # 5
        glm.vec4(+1, +1, -1, 1),  # 6
        glm.vec4(+1, +1, +1, 1),  # 7
    ]

    # From NDC to Eye (Camera)
    eyeCorners = [(e := invProj * c) / e.w for c in ndcCorners]

    # From Eye to World
    worldCorners = [(w := invView * c) / w.w for c in eyeCorners]

    glBegin(GL_LINES)
    for line in drawOrder:
        for vert in line:
            glVertex3f(*worldCorners[vert].xyz)
    glEnd()


def main():
    pygame.init()
    # display = (1280, 720)
    display = (1920, 1080)
    pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 8)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    fov = 30
    aspect = display[0] / display[1]
    near = 1
    far = 500
    projection = glm.perspective(glm.radians(fov), aspect, near, far)

    propProjection = glm.perspective(glm.radians(45), 1, 1, 8)

    propCam = glm.vec3(-10, 0, 0)
    target = propCam / 3
    cameraPos = glm.vec3(0, 3.4, 10) * 1.3

    propView = glm.lookAt(propCam, glm.vec3(0), glm.vec3(0, 1, 0))
    view = glm.lookAt(cameraPos, target, glm.vec3(0, 1, 0))

    model = glm.mat4(1)
    model = glm.translate(model, propCam / 3)

    propModel = glm.mat4(1)
    propModel = glm.translate(model, propCam)
    propModel = glm.scale(model, glm.vec3(0.1))

    glViewport(0, 0, *display)
    glEnable(GL_MULTISAMPLE)

    program = createProgram()

    vao, vbo = createBuffers(vertices)

    clock = pygame.time.Clock()

    counter = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                glDeleteProgram(program)
                glDeleteVertexArrays(1, [vao])
                glDeleteBuffers(1, [vbo])
                pygame.quit()
                quit()

        glDisable(GL_LIGHTING)
        glUseProgram(0)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glDisable(GL_CULL_FACE)
        glEnable(GL_DEPTH_TEST)

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        drawModel(vao, program, model, view, projection, cameraPos, propCam, False)
        glLineWidth(1)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        drawModel(vao, program, model, view, projection, cameraPos, propCam, True)

        # glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        # drawModel(vao, program, propModel, view, projection, cameraPos, cameraPos, False)

        glUseProgram(0)
        glLineWidth(2.5)
        glColor3f(1.0, 0.0, 0.0)
        glBindVertexArray(0)
        drawProjBox(propView, propProjection)

        pygame.display.flip()
        counter += clock.tick() / 1000
        if counter >= 1:
            counter -= 1
            print("\r", clock.get_fps(), end="", flush=True)


main()
