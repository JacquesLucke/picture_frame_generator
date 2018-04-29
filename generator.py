import bmesh

def createFrameBM(cornerSource, width, height):
    frameBM = cornerSource.copy()
    
    # create meshes for corners by mirroring the source
    corner1Verts, corner1Edges, corner1Faces = frameBM.verts[:], frameBM.edges[:], frameBM.faces[:]
    corner2Verts, corner2Edges, corner2Faces = mirror(frameBM, corner1Faces, "x")
    corner3Verts, corner3Edges, corner3Faces = mirror(frameBM, corner1Faces, "y")
    corner4Verts, corner4Edges, corner4Faces = mirror(frameBM, corner2Faces, "y")
    
    # move corners to final positions
    wHalf, hHalf = width / 2, height / 2
    translate(frameBM, corner1Verts, (-wHalf, -hHalf, 0))
    translate(frameBM, corner2Verts, (wHalf, -hHalf, 0))
    translate(frameBM, corner3Verts, (-wHalf, hHalf, 0))
    translate(frameBM, corner4Verts, (wHalf, hHalf, 0))
    
    # find edges to be bridged
    corner1Right = getEdgesInDirection(corner1Edges, "x")
    corner1Top = getEdgesInDirection(corner1Edges, "y")
    corner2Left = getEdgesInDirection(corner2Edges, "-x")
    corner2Top = getEdgesInDirection(corner2Edges, "y")
    corner3Right = getEdgesInDirection(corner3Edges, "x")
    corner3Bottom = getEdgesInDirection(corner3Edges, "-y")
    corner4Left = getEdgesInDirection(corner4Edges, "-x")
    corner4Bottom = getEdgesInDirection(corner4Edges, "-y")

    # bridge edges
    bridge(frameBM, corner1Right, corner2Left)
    bridge(frameBM, corner1Top, corner3Bottom)
    bridge(frameBM, corner2Top, corner4Bottom)
    bridge(frameBM, corner3Right, corner4Left)
    
    # recalc normals
    bmesh.ops.recalc_face_normals(frameBM, faces = frameBM.faces[:])
    
    return frameBM

def bmeshFromObject(object):
    bm = bmesh.new()
    bm.from_mesh(object.data)
    return bm

def duplicate(bm, faces):
    ret = bmesh.ops.duplicate(bm, geom = faces)
    return getRetData(ret)

def mirror(bm, geom, axis):
    ret = bmesh.ops.mirror(bm, geom = geom, axis = "xyz".index(axis))
    return getRetData(ret)

def translate(bm, verts, offset):
    bmesh.ops.translate(bm, vec = offset, verts = verts)
    
def bridge(bm, loop1, loop2):
    bmesh.ops.bridge_loops(bm, edges = loop1 + loop2)
    
def getEdgesInDirection(edges, axis):
    findMinOrMax = min if axis[0] == "-" else max
    axisIndex = "xyz".index(axis[-1])
    extrema = findMinOrMax((getEdgeCenter(edge)[axisIndex] for edge in edges))
    
    epsilon = 0.001
    foundEdges = [edge for edge in edges if abs(getEdgeCenter(edge)[axisIndex] - extrema) < epsilon]
    return foundEdges
    
def getEdgeCenter(edge):
    return (edge.verts[0].co + edge.verts[1].co) / 2
    
def getRetData(ret):
    newVerts = [e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)]
    newEdges = [e for e in ret["geom"] if isinstance(e, bmesh.types.BMEdge)]
    newFaces = [e for e in ret["geom"] if isinstance(e, bmesh.types.BMFace)]
    return newVerts, newEdges, newFaces