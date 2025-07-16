# Tileslice Addon for Blender
# https://github.com/mtskelton/BlenderSliceToTiles

import bpy, bmesh
from mathutils import Vector

bl_info = {
    "name": "Slice To Tiles",
    "author": "Mark Skelton",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Object > Slice to Tiles",
    "description": "Slices an object into smaller tiles or segments based on a specified size",
    "category": "Object",
}

class OBJECT_OT_slice_tiles(bpy.types.Operator):
    bl_idname = "object.slice_tiles"
    bl_label = "Slice to Tiles"
    bl_options = {'REGISTER', 'UNDO'}

    size: bpy.props.FloatProperty(name="Segment Size", description="Size of each segment", default=10.0, min=0.01)
    apply_x: bpy.props.BoolProperty(name="Slice X", description="Slice along the X axis", default=True)
    apply_y: bpy.props.BoolProperty(name="Slice Y", description="Slice along the Y axis", default=True)
    apply_z: bpy.props.BoolProperty(name="Slice Z", description="Slice along the Z axis", default=False)
    recenter_objects: bpy.props.BoolProperty(name="Recenter Objects", description="Recenter the origin of the new objects", default=True)
    use_duplicate: bpy.props.BoolProperty(name="Use Duplicate", description="Duplicate the original object instead of slicing it", default=False)
    max_new_objects: bpy.props.IntProperty(name="Max New Objects", description="Maximum number of new objects to create.  You can increase this, but if it's too high you might be here all day.", default=1000, min=1)

    def execute(self, context):
        objects = self.split(context)
        if self.recenter_objects:
            self.recenter(objects)
        return {'FINISHED'}

    def split(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Active object is not a mesh.")
            return
        
        if self.use_duplicate:
            name = obj.name
            obj = obj.copy()
            obj.data = obj.data.copy()
            obj.name = f"{name}_tiles"
            context.collection.objects.link(obj)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
        
        size = self.size

        dimensions = obj.dimensions
        x_segments = (int(dimensions.x // size) + 1) if self.apply_x else 1
        y_segments = (int(dimensions.y // size) + 1) if self.apply_y else 1
        z_segments = (int(dimensions.z // size) + 1) if self.apply_z else 1

        total_new_objects = x_segments * y_segments * z_segments
        if total_new_objects > self.max_new_objects:
            self.report({'ERROR'}, "Too many segments created (" + str(total_new_objects) + "). Please increase the segment size or, if you think your rig can handle it, increase the max number of segments.  Proceed at your own risk!")
            return []

        bm = bmesh.new()
        mesh = obj.data
        bm.from_mesh(mesh)

        o, x, y, z = self.bbox_axes(obj)

        if self.apply_x:
            self.slice(bm, o, x, x_segments)
        if self.apply_y:
            self.slice(bm, o, y, y_segments)
        if self.apply_z:
            self.slice(bm, o, z, z_segments)
        bm.to_mesh(mesh)

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.mode_set()

        self.report({'INFO'}, f"Created {total_new_objects} new objects.")

        return [ob for ob in bpy.context.selected_objects if ob.type == 'MESH']

    def recenter(self, selected_objects):
        original_cursor_location = bpy.context.scene.cursor.location.copy()
        for ob in selected_objects:
            if ob.type == 'MESH':
                center = self.bbox_center(ob)

                bpy.context.scene.cursor.location = (center.x, center.y, 0.0 if not self.apply_z else center.z)
                bpy.ops.object.select_all(action='DESELECT')
                ob.select_set(True)
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')

        bpy.context.scene.cursor.location = original_cursor_location

    def bbox(self, ob):
        return (Vector(b) for b in ob.bound_box)

    def bbox_center(self, ob):
        return sum(self.bbox(ob), Vector()) / 8

    def bbox_axes(self, ob):
        bb = list(self.bbox(ob))
        return tuple(bb[i] for i in (0, 4, 3, 1))

    def slice(self, bm, start, end, segments):
        def g(bm):
            return bm.verts[:] + bm.edges[:] + bm.faces[:]

        if segments == 1:
            return
        planes = [start.lerp(end, f / segments) for f in range(1, segments)]
        plane_no = (end - start).normalized()

        while (planes):
            p0 = planes.pop(0)
            ret = bmesh.ops.bisect_plane(bm,
                                         geom=g(bm),
                                         plane_co=p0,
                                         plane_no=plane_no)
            bmesh.ops.split_edges(bm,
                                  edges=[e for e in ret['geom_cut'] if isinstance(e, bmesh.types.BMEdge)])


def menu_func(self, context):
    self.layout.operator(OBJECT_OT_slice_tiles.bl_idname)

def register():
    bpy.utils.register_class(OBJECT_OT_slice_tiles)
    bpy.types.VIEW3D_MT_object.append(menu_func)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_slice_tiles)
    bpy.types.VIEW3D_MT_object.remove(menu_func)


if __name__ == "__main__":
    register()
