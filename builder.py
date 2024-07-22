import numpy as np

obj = open("res/sphere2.obj").readlines()

_verts = []
_normals = []
_faces = []

for line in obj:
    if line.startswith('v '):
        _verts.append([np.float32(v) for v in line[2:].split(' ')])
    elif line.startswith('vn '):
        _normals.append([np.float32(n) for n in line[3:].split(' ')])
    elif line.startswith('f '):
        face = [[np.uint16(s if s else 0) for i, s in enumerate(f.split('/')) if i != 1] for f in line[2:].split(' ')]
        assert len(face) >= 3
        for i in range(len(face) - 2):
            _faces.append([face[0], face[i+1], face[i+2]])

vertices = []
for face in _faces:
    for [pos, norm] in face:
        vertices.append(_verts[pos-1] + _normals[norm-1])
vertices = np.array(vertices, dtype=np.float32)

assert vertices.shape == (len(_faces) * 3, len(_verts[0]) + len(_normals[0])), (vertices.shape, (len(_faces) * 3, len(_verts[0]) + len(_normals[0])))
