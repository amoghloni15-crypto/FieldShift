"""
FieldShift Bidirectional 3D Globe Component Declaration.
Declaring this in an importable module ensures Streamlit's component registry
correctly identifies the parent module name in multi-page st.navigation contexts.
"""
import os
import streamlit.components.v1 as components

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
globe_dir = os.path.join(base_dir, "globe_component")
globe_component = components.declare_component("globe_component", path=globe_dir)
