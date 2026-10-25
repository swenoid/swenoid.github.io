"""Export the prepared MuJoCo visual model as a static, colored GLB.

Requires mujoco, numpy and trimesh. Inputs are the prepared scene XML and its
render-provenance JSON from the SWENOID figure project. Collision geometry,
dynamics, and the original simulation files are not changed.
"""
import argparse
import hashlib
import json
from pathlib import Path

import mujoco
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('scene', type=Path)
parser.add_argument('provenance', type=Path)
args = parser.parse_args()
source = json.loads(args.provenance.read_text())
model = mujoco.MjModel.from_xml_path(str(args.scene))
data = mujoco.MjData(model)
for joint, value in source['pose_radians'].items():
    data.qpos[model.joint(joint).qposadr[0]] = value
mujoco.mj_forward(model, data)

# MuJoCo +X is forward and +Z is up. glTF +Z is forward and +Y is up.
rotation = np.array([[0., 1., 0.], [0., 0., 1.], [1., 0., 0.]])
properties = {
    'plastic': (0.0, 0.78), 'motor': (0.15, 0.55),
    'bearing': (0.8, 0.35), 'steel': (0.85, 0.3),
    'battery': (0.0, 0.8), 'battery_label': (0.0, 0.7),
    'case': (0.4, 0.45), 'electronics': (0.0, 0.7),
}
materials = {}
meshes = []
for gid in range(model.ngeom):
    if model.geom_group[gid] != 2 or model.geom_type[gid] != mujoco.mjtGeom.mjGEOM_MESH:
        continue
    mid = int(model.geom_dataid[gid])
    va, vn = int(model.mesh_vertadr[mid]), int(model.mesh_vertnum[mid])
    fa, fn = int(model.mesh_faceadr[mid]), int(model.mesh_facenum[mid])
    vertices = model.mesh_vert[va:va+vn].copy()
    vertices = vertices @ data.geom_xmat[gid].reshape(3, 3).T + data.geom_xpos[gid]
    vertices = vertices @ rotation.T
    mesh = trimesh.Trimesh(vertices=vertices, faces=model.mesh_face[fa:fa+fn].copy(), process=False).smooth_shaded
    material_id = int(model.geom_matid[gid])
    name = model.material(material_id).name.removeprefix('physical_')
    if name not in materials:
        metallic, roughness = properties[name]
        materials[name] = trimesh.visual.material.PBRMaterial(
            name=name,
            baseColorFactor=np.round(model.mat_rgba[material_id] * 255).astype(np.uint8),
            metallicFactor=metallic, roughnessFactor=roughness,
        )
    mesh.visual = trimesh.visual.TextureVisuals(material=materials[name])
    meshes.append((model.geom(gid).name, mesh))

# Put both feet on the viewer's ground and center the robot horizontally.
bounds = np.array([mesh.bounds for _, mesh in meshes])
lower, upper = bounds[:, 0].min(axis=0), bounds[:, 1].max(axis=0)
offset = np.array([-(lower[0] + upper[0])/2, -lower[1], -(lower[2] + upper[2])/2])
scene = trimesh.Scene()
for name, mesh in meshes:
    mesh.apply_translation(offset)
    scene.add_geometry(mesh, geom_name=name, node_name=name)

out = ROOT / 'assets/models/swenoid.glb'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_bytes(scene.export(file_type='glb'))
reloaded = trimesh.load(out, force='scene')
assert np.allclose(scene.bounds, reloaded.bounds, atol=1e-6)
assert len(reloaded.geometry) == len(meshes)
assert out.stat().st_size < 100 * 1024 * 1024
metadata = {
    'sourceRepository': source['repository'],
    'sourceCommit': source['commit'],
    'sourceModel': 'src/swenoid/assets/swenoid/xmls/swenoid.xml',
    'format': 'glTF binary 2.0', 'units': 'metres', 'upAxis': '+Y',
    'poseRadians': source['pose_radians'],
    'visualRepair': source['geometry_repairs']['description'],
    'materialScheme': source['material_scheme'],
    'visualMeshes': len(meshes),
    'triangles': sum(len(mesh.faces) for _, mesh in meshes),
    'boundsMetres': scene.bounds.tolist(),
    'actuatedJointsInSource': int(model.nu),
    'simulationIncluded': False,
    'sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
    'bytes': out.stat().st_size,
}
(ROOT / 'assets/models/swenoid.json').write_text(json.dumps(metadata, indent=2)+'\n')
print(json.dumps({key: metadata[key] for key in ['visualMeshes', 'triangles', 'boundsMetres', 'bytes']}, indent=2))
