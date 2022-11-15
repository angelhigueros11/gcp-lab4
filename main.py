import numpy
import random
import pygame
from OpenGL.GL import *
from OpenGL.GL.shaders import *
import glm

pygame.init()

screen = pygame.display.set_mode(
    (1600, 1200),
    pygame.OPENGL | pygame.DOUBLEBUF
)

vertex_shader = """
#version 460
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 vertexColor;

uniform mat4 amatrix;

out vec3 ourColor;


void main()
{
    gl_Position = amatrix * vec4(position, 1.0f);
    ourColor = vertexColor;

}
"""

fragment_shader = """
#version 460

layout (location = 0) out vec4 fragColor;

uniform vec3 color;


in vec3 ourColor;

void main()
{
    // fragColor = vec4(ourColor, 1.0f);
    fragColor = vec4(color, 1.0f);
}
"""

vertex_shader2 = """
#version 450
layout (location = 0) in vec3 position;
layout (location = 1) in vec3 normal;
layout (location = 2) in vec2 texCoords;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

uniform float tiempo;
uniform float valor;
uniform vec3 pointLight;

out vec3 outColor;
out vec2 outTexCoords;

void main()
{
    vec4 norm = vec4(normal, 0.0);

    vec4 pos = vec4(position, 1.0) + norm * valor;
    pos = modelMatrix * pos;

    vec4 light = vec4(pointLight, 1.0);

    float intensity = dot(modelMatrix * norm, normalize(light - pos));

    gl_Position = projectionMatrix * viewMatrix * pos;

    outColor = vec3(1.0,1.0 - valor * 2,1.0-valor * 2) * intensity;
    outTexCoords = texCoords;
}
"""


fragment_shader2 = """
#version 450
layout (location = 0) out vec4 fragColor;

in vec3 outColor;
in vec2 outTexCoords;

uniform sampler2D tex;

void main()
{
    fragColor = vec4(outColor, 1) * texture(tex, outTexCoords);
}
"""

compiled_vertex_shader = compileShader(vertex_shader, GL_VERTEX_SHADER)
compiled_fragment_shader = compileShader(fragment_shader, GL_FRAGMENT_SHADER)
shader = compileProgram(
    compiled_vertex_shader,
    compiled_fragment_shader
)

glUseProgram(shader)


vertex_data = numpy.array([
    -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
    0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
    0.0,  0.5, 0.0, 0.0, 0.0, 1.0
], dtype=numpy.float32)

vertex_buffer_object = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer_object)
glBufferData(
    GL_ARRAY_BUFFER,
    vertex_data.nbytes,
    vertex_data,
    GL_STATIC_DRAW
)
vertex_array_object = glGenVertexArrays(1)
glBindVertexArray(vertex_array_object)

glVertexAttribPointer(
    0,
    3,
    GL_FLOAT,
    GL_FALSE,
    6 * 4,
    ctypes.c_void_p(0)
)
glEnableVertexAttribArray(0)


glVertexAttribPointer(
    1,
    3,
    GL_FLOAT,
    GL_FALSE,
    6 * 4,
    ctypes.c_void_p(3 * 4)
)
glEnableVertexAttribArray(1)


def calculateMatrix(angle):
    i = glm.mat4(1)
    translate = glm.translate(i, glm.vec3(0, 0, 0))
    rotate = glm.rotate(i, glm.radians(angle), glm.vec3(0, 1, 0))
    scale = glm.scale(i, glm.vec3(1, 1, 1))

    model = translate * rotate * scale

    view = glm.lookAt(
        glm.vec3(0, 0, 5),
        glm.vec3(0, 0, 0),
        glm.vec3(0, 1, 0)
    )

    projection = glm.perspective(
        glm.radians(45),
        1600/1200,
        0.1,
        1000.0
    )

    amatrix = projection * view * model

    glUniformMatrix4fv(
        glGetUniformLocation(shader, 'amatrix'),
        1,
        GL_FALSE,
        glm.value_ptr(amatrix)
    )


glViewport(0, 0, 1600, 1200)


running = True

glClearColor(0.5, 1.0, 0.5, 1.0)
r = 0
# render.scene.append( face )

while running:

    keys = pygame.key.get_pressed()

    # Traslacion de camara
    # if keys[K_d]:
    #     render.camPosition.x += 1
    # if keys[K_a]:
    #     render.camPosition.x -= 1
    # if keys[K_w]:
    #     render.camPosition.z += 1
    # if keys[K_s]:
    #     render.camPosition.z -= 1
    # if keys[K_q]:
    #     render.camPosition.y -= 1
    # if keys[K_e]:
    #     render.camPosition.y += 1

    # if keys[K_LEFT] and render.valor > 0:
    #     render.valor -= 0.1

    # if keys[K_RIGHT] and render.valor < 0.2:
    #     render.valor += 0.1

    # Rotacion de camara
    # if keys[K_z]:
    #     render.camRotation.y += 15
    # if keys[K_x]:
    #     render.camRotation.y -= 15

    for ev in pygame.event.get():
        if ev.type != pygame.QUIT and ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE or ev.type == pygame.QUIT:
            isRunning = False

    r += 1
    glClear(GL_COLOR_BUFFER_BIT)

    color1 = random.random()
    color2 = random.random()
    color3 = random.random()

    color = glm.vec3(color1, color2, color3)

    glUniform3fv(
        glGetUniformLocation(shader, 'color'),
        1,
        glm.value_ptr(color)
    )

    calculateMatrix(r)

    pygame.time.wait(50)

    glDrawArrays(GL_TRIANGLES, 0, 3)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
