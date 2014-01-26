# Living Forest

This is a 3D text-based adventure game. You play Muana Loka, a god whose domain
is threatened by human development.

> 3D text?

No! This game plays like a tranditional interactive fiction game, however
the world is actually a 3D scene. The engine render the objects not as pictures,
but as text.

## Playing the Game

This game runs in the Blender Game Engine. To play it:

1. Download [Blender 2.69][bl].
1. Load `game/Level_1.blend` in Blender.
1. Press `p` to start the game.

[bl]: http://blender.org/download

## Developing and Modding

The assets (object locations and flavour text) are in the `.blend` files. In
Blender, the objects can be moved around - the relationship text (e.g. "the
squirrel is next to the tree") will update automatically. Additional details
can be modified by adjusting the [game properties][gp]. There is a custom plugin
for editing Living Forest-specific properties in the `addons` directory.

The logic is written in Python, with minimal hooks into Blender via game logic
bricks. To adjust the logic, use a text editor to modify the `.py` files in the
`gama/tba` directory.

[gp]: http://wiki.blender.org/index.php/Doc:2.6/Manual/Game_Engine/Logic/Properties/Editing

