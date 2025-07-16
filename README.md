# Slice to Tiles Addon for Blender

This addon allows you to slice a mesh object into smaller tiles based on a specified segment size. It provides options to slice along the X, Y, and Z axes, and can recenter the new objects after slicing.
It's intended use is to evenly split large terrain meshes into manageable tiles for game development, particularly for use in Godot, Unity and other game engines, but it can be applied for other purposes as well.

# Installation
1. Download the `tileslice_addon.py` file.
2. Open Blender.
3. Go to `Edit` > `Preferences`.
4. Select the `Add-ons` tab.
5. Click on `Install...` and select the downloaded `tileslice_addon.py` file.
6. Enable the addon by checking the box next to it in the list.

# Usage
1. Select the mesh object you want to slice.
2. Under the `Object` menu, find the `Slice to Tiles` option.
3. Set the desired segment size for slicing.
4. Choose the axes along which you want to slice (X, Y, Z).
5. Optionally, check the `Recenter` option to recenter the new objects after slicing.

# Caveats
- The addon currently only works with mesh objects.
- Ensure that the segment size is appropriate for the size of your mesh to avoid creating too many small tiles.  It's a very slow operation for large meshes and small segment sizes.

# Credits
The base concept of this was adapted from the stackexchange answer and wider discussion [here](https://blender.stackexchange.com/a/133258).
