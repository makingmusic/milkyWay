# EchoMaze

## A basic maze game.
Keyboard arrow keys for navigation
Spacebar or left-mouse click for echo

The walls are not shown by default, when you press the spacebar, it does echo location and shows the nearby walls for a brief period.

<img width="766" height="420" alt="image" src="https://github.com/user-attachments/assets/a39985c0-1c5e-4a83-92ed-36fff64dc535" />


TODO: 
* hiding the walls and using echolocation to find the walls is tbd. 


TODO: Performance improvmeent ideas 
1) Stop full-grid rebuilds per frame
Maintain a persistent base_surface for the maze with paths + hidden walls, drawn once at init.
Maintain a persistent revealed_surface that you only draw onto when a wall becomes revealed. Each frame, just blit base_surface, then revealed_surface. Avoid per-cell loops each frame.
2) Replace full copy of the maze for echoes
Eliminate getMazeWithinEchoCircle’s full maze_subset = [row[:] for row in maze] per frame.
Track a boolean mask or set[(x,y)] of revealed wall-cells globally. Echo updates should only add cells to this set; drawing uses the surfaces above.
3) Incremental reveal instead of recomputing circles
For each echo, store center, radius, last_radius. On each tick, only compute the newly revealed “ring” cells between last_radius and radius and append to revealed set and draw rects once to revealed_surface.
Don’t iterate entire grid; iterate only cells in the echo’s bounding box and test distance.
4) Limit work to circle bounding boxes
Any per-echo cell checks must iterate only x ∈ [cx−r, cx+r], y ∈ [cy−r, cy+r], clamped to maze bounds, instead of full mazeY × mazeX.
5) Kill per-frame allocations for echo overlay
Reuse the alpha Surface for echo circles. Create it once and clear each frame with fill((0,0,0,0)) rather than reallocating a new surface.
6) Reduce draw calls with rect batching
When revealing cells, build batches and use pygame.draw.rect in loops only at reveal-time (not every frame). Per-frame, you’re just blitting two surfaces.
7) Disable per-frame prints
Guard the debug prints under a fast flag or frame throttling (e.g., print every N frames) or disable in release. Current radius/cell counts printed each frame will tank performance.
8) Cap echo count and lifespan
Hard limit number of concurrent echoes. Increase ECHO_RADIUS_INCREMENT and/or ECHO_ALPHA_DECREMENT so echoes expire faster.
9) Precompute static geometry helpers
Precompute cell center coordinates or reuse them. This avoids repeated x*CELL_SIZE + CELL_SIZE//2 math in hot loops.
Precompute r^2 and compare to squared distances (already done), but avoid recomputing center_of_circle for each cell.
10) Use NumPy masks for large grids
If maze sizes grow, accelerate reveal-ring computation with numpy:
Build a 2D grid of cell centers once.
For each echo update, vectorize the ring mask (d2 <= r2) & (d2 > last_r2) and OR into a global boolean mask.
Convert only newly True cells into rect draws on revealed_surface.
11) Clip rendering to dirty regions
Use screen.set_clip to restrict drawing to the union of updated areas (echo bounding boxes) each frame. This reduces fill/draw overhead on large screens.
12) Use a tile atlas or pre-colored tiles
Pre-create small Surface tiles (path/hidden wall/shown wall) and blit them during initial maze build or reveal-only updates. Avoid pygame.draw.rect in inner loops.
13) Consider thicker cell size or lower frame rate
Larger CELL_SIZE reduces number of cells.
If acceptable, cap GAME_FRAME_RATE at 45 or 30 in release.
14) Optional visual compromises
Lower ECHO_THICKNESS, reduce alpha precision steps, and avoid anti-aliased circle drawing if using gfxdraw (filled circle + outline can be cheaper).
15) Avoid list mutation while iterating echoes
Use index-based loop or build a new list for alive echoes. It avoids potential O(n^2) behaviors and keeps things predictable under higher echo counts.


