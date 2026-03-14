# -*- coding: utf-8 -*-
"""
render — Rendering layer.

Responsible for drawing the simulation world and all visual effects:
  camera.py       Viewport pan & zoom (maps grid ↔ screen coordinates)
  theme.py        Colour palette, font helpers, panel drawing utilities
  renderer.py     Main renderer — draws cells, fires, trucks, particle effects
  particles.py    Fire & smoke particle system
"""
