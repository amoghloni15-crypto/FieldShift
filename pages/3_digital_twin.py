"""
FieldShift 3D Farm Digital Twin (Page 3).
Interactive Procedural WebGL Canopy & Subterranean Soil/Root Cross-Section.
Powered by Three.js (InstancedMesh) & FAO-56 Rooting Depth Metrics.
"""

import json
import streamlit as st
import pandas as pd

from core.ui_theme import (
    render_html, inject_vault_styles, render_command_bar,
    render_provenance_badge, render_empty_analysis_notice,
    render_error_boundary, fmt_num
)
from core.agronomy_engine import load_crop_database

inject_vault_styles()

render_command_bar(
    "3D FARM DIGITAL TWIN",
    "PROCEDURAL CANOPY ARCHITECTURE • ROOT STRATIGRAPHY & HYDROLOGICAL INFILTRATION"
)

if not st.session_state.get("analysis_completed"):
    render_empty_analysis_notice()
    if st.button("🚀 GO TO MISSION CONTROL", use_container_width=True):
        st.switch_page("pages/1_mission_control.py")
else:
    farm_name = st.session_state.get("farm_name", "Target Sector")
    coords = st.session_state.get("coords", (33.5779, -101.8552))
    climate_data = st.session_state.get("climate_data", {})
    soil_data = st.session_state.get("soil_data", {})
    crop_df = st.session_state.get("crop_df")
    if crop_df is None:
        crop_df = load_crop_database()

    top_rotations = st.session_state.get("top_rotations", [])
    active_scenario = st.session_state.get("active_scenario", {})

    # Available crops for selection
    available_crops = crop_df["crop_name"].tolist()
    default_crop = top_rotations[0]["crops"][0] if top_rotations else available_crops[0]
    default_idx = available_crops.index(default_crop) if default_crop in available_crops else 0

    # SIDEBAR CONTROLS
    render_html("""<div style="font-family: 'Orbitron', monospace; font-size: 1.15rem; font-weight: 800; color: #19F3FF; letter-spacing: 2px; margin-bottom: 12px; text-transform: uppercase;">🌱 TWIN CONTROLS</div>""", sidebar=True)

    selected_crop_name = st.sidebar.selectbox(
        "Select Active Crop:",
        available_crops,
        index=default_idx,
        key="twin_crop_select"
    )

    crop_meta = crop_df[crop_df["crop_name"] == selected_crop_name].iloc[0].to_dict()
    root_depth_m = float(crop_meta.get("rooting_depth_m", 1.2))
    water_need = float(crop_meta.get("water_need_mm", 500))
    family = crop_meta.get("plant_family", "Poaceae")
    is_cereal = family in ["Poaceae"]

    st.sidebar.markdown("---")
    st.sidebar.markdown("### // PHENOLOGY & SEASONS")
    growth_stage = st.sidebar.slider(
        "Phenological Growth Stage:",
        min_value=0,
        max_value=5,
        value=3,
        step=1,
        format="%d",
        help="0: Seed/Furrow, 1: Emergence, 2: Vegetative, 3: Flowering, 4: Grain Fill, 5: Maturity/Harvest",
        key="twin_growth_slider"
    )

    stage_names = [
        "Stage 0: Sown Furrow & Seed Imbibition",
        "Stage 1: Emergence & Early Seedling (15%)",
        "Stage 2: Vegetative Canopy Expansion (40%)",
        "Stage 3: Flowering & Anthesis / Tasseling (75%)",
        "Stage 4: Grain / Pod Fill (95%)",
        "Stage 5: Physiological Maturity & Harvest Ready (100%)"
    ]
    st.sidebar.caption(f"**Status:** {stage_names[growth_stage]}")

    season_option = st.sidebar.selectbox(
        "Atmospheric Environment:",
        ["Summer (Kharif / High Sun)", "Monsoon (Overcast & Rain Infiltration)", "Post-Monsoon (Warm Golden Hour)", "Winter (Crisp Ambient Light)"],
        index=0,
        key="twin_season_select"
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### // CAMERA & STRATIGRAPHY")
    camera_view = st.sidebar.selectbox(
        "Camera Viewpoint:",
        ["Aerial Overview (45° Perspective)", "Field Level (Crop Row Walk)", "Subsoil Cutaway Profile (Root Zone)"],
        index=0,
        key="twin_cam_select"
    )

    show_cutaway = st.sidebar.checkbox(
        "Subterranean Soil Cutaway",
        value=True,
        help="Exposes the 0-150cm soil stratigraphy, root architecture, and moisture infiltration front.",
        key="twin_cutaway_check"
    )

    show_infiltration = st.sidebar.checkbox(
        "Simulate Water Infiltration Flow",
        value=True,
        help="Animates pore-water percolation through the root zone.",
        key="twin_infil_check"
    )

    # Color palette based on soil texture
    soil_texture = soil_data.get("texture", "Clay Loam")
    if "Clay" in soil_texture:
        soil_color_top = "#452A18"
        soil_color_sub = "#5C381E"
    elif "Sand" in soil_texture:
        soil_color_top = "#8C7A58"
        soil_color_sub = "#A3916D"
    elif "Silt" in soil_texture:
        soil_color_top = "#574838"
        soil_color_sub = "#6B5A49"
    else:
        soil_color_top = "#3D2B1F"
        soil_color_sub = "#4E3728"

    # Context Header & Provenance Badge
    prov_badge = render_provenance_badge("MODELED / SIMULATED", "Procedural 3D WebGL")
    render_html(f"""
    <div class="holo-metric-card" style="margin-bottom: 20px;">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
        <div>
          <div class="holo-label">PROCEDURAL TWIN // {farm_name.upper()}</div>
          <div style="font-family: 'Orbitron', monospace; font-size: 1.4rem; color: #FFFFFF; margin: 4px 0;">
            {selected_crop_name} <span style="font-size: 1rem; color: #19F3FF;">(Max Root Depth: {root_depth_m:.1f} m)</span>
          </div>
          <div style="font-family: 'Share Tech Mono', monospace; font-size: 0.88rem; color: #2CFFB0;">
            SOIL: {soil_texture.upper()} • PH: {soil_data.get('ph', 6.8)} • WATER NEED: {water_need:.0f} mm/yr • {stage_names[growth_stage]}
          </div>
        </div>
        <div>{prov_badge}</div>
      </div>
      <div style="margin-top: 10px; font-family: 'Rajdhani', sans-serif; font-size: 0.92rem; color: #8FA6B8; border-top: 1px solid rgba(25, 243, 255, 0.15); padding-top: 8px;">
        <em>DISCLAIMER:</em> Modeled 3D simulation constructed from FAO-56 crop canopy parameters and SoilGrids stratigraphic depths. <strong>This is an illustrative procedural visualization, not a real-time satellite optical image.</strong>
      </div>
    </div>
    """)

    # Pass parameters into Three.js WebGL component
    twin_config = {
        "cropName": selected_crop_name,
        "isCereal": is_cereal,
        "growthStage": growth_stage,
        "rootDepth": root_depth_m,
        "season": season_option,
        "cameraView": camera_view,
        "showCutaway": show_cutaway,
        "showInfiltration": show_infiltration,
        "soilColorTop": soil_color_top,
        "soilColorSub": soil_color_sub,
        "soilTexture": soil_texture,
        "annualRain": climate_data.get("mean_annual_rainfall_mm", 450)
    }

    config_json = json.dumps(twin_config)

    # Three.js 3D Canvas Container
    twin_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <style>
        body, html {{
          margin: 0;
          padding: 0;
          width: 100%;
          height: 100%;
          overflow: hidden;
          background: #050B10;
          font-family: 'Share Tech Mono', monospace;
        }}
        #canvas-container {{
          width: 100%;
          height: 600px;
          position: relative;
          border: 1px solid rgba(25, 243, 255, 0.35);
          box-shadow: 0 0 25px rgba(25, 243, 255, 0.15) inset, 0 0 15px rgba(0, 0, 0, 0.8);
          background: radial-gradient(circle at center, #0B1724 0%, #050B10 100%);
        }}
        #hud-overlay {{
          position: absolute;
          top: 12px;
          left: 14px;
          color: #19F3FF;
          font-size: 11px;
          letter-spacing: 1px;
          pointer-events: none;
          z-index: 10;
          text-shadow: 0 0 8px rgba(25, 243, 255, 0.6);
        }}
        #hud-reticle {{
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          width: 50px;
          height: 50px;
          border: 1px dashed rgba(25, 243, 255, 0.35);
          border-radius: 50%;
          pointer-events: none;
          z-index: 5;
        }}
        #hud-controls {{
          position: absolute;
          bottom: 12px;
          right: 14px;
          color: #8FA6B8;
          font-size: 10px;
          z-index: 10;
          pointer-events: none;
          text-align: right;
        }}
        .hud-btn {{
          background: rgba(10, 20, 30, 0.85);
          border: 1px solid #19F3FF;
          color: #19F3FF;
          font-family: 'Share Tech Mono', monospace;
          font-size: 11px;
          padding: 4px 10px;
          cursor: pointer;
          border-radius: 2px;
          margin-top: 6px;
          pointer-events: auto;
        }}
        .hud-btn:hover {{
          background: #19F3FF;
          color: #050B10;
        }}
        #fallback-card {{
          display: none;
          position: absolute;
          top: 20%;
          left: 10%;
          width: 80%;
          padding: 24px;
          background: rgba(10, 20, 30, 0.95);
          border: 1px solid #FF9E1F;
          color: #E8F6FF;
          text-align: center;
          z-index: 20;
        }}
      </style>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
      <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
      <div id="canvas-container">
        <div id="hud-overlay">
          <div>// SECTOR: {farm_name.upper()}</div>
          <div style="color: #FFFFFF; font-weight: bold; font-size: 13px; margin: 3px 0;">CROP: {selected_crop_name.upper()}</div>
          <div style="color: #2CFFB0;">ROOTING HORIZON: 0.0m ➔ -{root_depth_m:.1f}m</div>
          <div style="color: #FF9E1F;">STATUS: {stage_names[growth_stage].upper()}</div>
        </div>
        <div id="hud-reticle"></div>
        <div id="hud-controls">
          <div>ROTATE: Left-Click + Drag</div>
          <div>PAN: Right-Click + Drag</div>
          <div>ZOOM: Mouse Wheel</div>
          <button class="hud-btn" id="reset-cam-btn">RESET ORBIT</button>
        </div>
        <div id="fallback-card">
          <h3 style="color:#FF9E1F; margin-top:0;">⚠️ WebGL Hardware Acceleration Unavailable</h3>
          <p>WebGL could not be initialized in this browser viewport. Displaying stratigraphic baseline parameters:</p>
          <div style="text-align:left; max-width:400px; margin: 0 auto; line-height: 1.6;">
            • Active Crop: <strong>{selected_crop_name}</strong><br/>
            • Maximum Root Penetration: <strong>{root_depth_m} meters</strong><br/>
            • Topsoil Depth (0-30cm): <strong>{soil_texture}</strong><br/>
            • Subsoil Depth (30-100cm): Dense Mineral Substratum<br/>
            • Estimated Hydrological Need: <strong>{water_need} mm/season</strong>
          </div>
        </div>
      </div>

      <script>
        const CONFIG = {config_json};
        const container = document.getElementById('canvas-container');
        const fallbackCard = document.getElementById('fallback-card');

        // Check WebGL availability
        function isWebGLAvailable() {{
          try {{
            const canvas = document.createElement('canvas');
            return !!(window.WebGLRenderingContext && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
          }} catch (e) {{
            return false;
          }}
        }}

        if (!isWebGLAvailable()) {{
          fallbackCard.style.display = 'block';
        }} else {{
          initThreeScene();
        }}

        function initThreeScene() {{
          const width = container.clientWidth || 800;
          const height = container.clientHeight || 600;

          // Scene & Fog
          const scene = new THREE.Scene();
          scene.background = new THREE.Color(0x060E17);
          scene.fog = new THREE.FogExp2(0x060E17, 0.018);

          // Camera
          const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
          
          // Set initial camera based on config
          function applyCameraView(viewName) {{
            if (viewName.includes("Field Level")) {{
              camera.position.set(0, 3.2, 14);
              controls.target.set(0, 2.5, 0);
            }} else if (viewName.includes("Subsoil")) {{
              camera.position.set(0, -3.5, 22);
              controls.target.set(0, -3.0, 0);
            }} else {{
              // Aerial Overview
              camera.position.set(22, 20, 22);
              controls.target.set(0, 0, 0);
            }}
            controls.update();
          }}

          // Renderer
          const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
          renderer.setSize(width, height);
          renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
          renderer.shadowMap.enabled = true;
          renderer.shadowMap.type = THREE.PCFSoftShadowMap;
          container.appendChild(renderer.domElement);

          // OrbitControls
          const controls = new THREE.OrbitControls(camera, renderer.domElement);
          controls.enableDamping = true;
          controls.dampingFactor = 0.05;
          controls.maxPolarAngle = Math.PI / 2 + 0.15; // Allow slight sub-surface view
          controls.minDistance = 5;
          controls.maxDistance = 65;

          applyCameraView(CONFIG.cameraView);

          document.getElementById('reset-cam-btn').addEventListener('click', () => {{
            applyCameraView(CONFIG.cameraView);
          }});

          // Lighting Environment based on Season
          const ambientLight = new THREE.AmbientLight(0xffffff, 0.45);
          scene.add(ambientLight);

          const sunLight = new THREE.DirectionalLight(0xffffff, 0.85);
          sunLight.castShadow = true;
          sunLight.shadow.mapSize.width = 1024;
          sunLight.shadow.mapSize.height = 1024;
          sunLight.shadow.camera.near = 0.5;
          sunLight.shadow.camera.far = 80;
          const d = 25;
          sunLight.shadow.camera.left = -d;
          sunLight.shadow.camera.right = d;
          sunLight.shadow.camera.top = d;
          sunLight.shadow.camera.bottom = -d;

          if (CONFIG.season.includes("Summer")) {{
            sunLight.position.set(15, 35, 15);
            sunLight.color.setHex(0xFFFFFF);
            ambientLight.color.setHex(0x90CAF9);
            ambientLight.intensity = 0.5;
          }} else if (CONFIG.season.includes("Monsoon")) {{
            sunLight.position.set(8, 25, 8);
            sunLight.color.setHex(0x9E9E9E);
            sunLight.intensity = 0.45;
            ambientLight.color.setHex(0x607D8B);
            ambientLight.intensity = 0.4;
            scene.fog.color.setHex(0x0E1A24);
          }} else if (CONFIG.season.includes("Post-Monsoon")) {{
            sunLight.position.set(30, 14, 15);
            sunLight.color.setHex(0xFFB74D);
            sunLight.intensity = 1.0;
            ambientLight.color.setHex(0xFFE082);
            ambientLight.intensity = 0.4;
          }} else {{
            // Winter
            sunLight.position.set(10, 18, 20);
            sunLight.color.setHex(0xBBDEFB);
            sunLight.intensity = 0.6;
            ambientLight.color.setHex(0x90A4AE);
            ambientLight.intensity = 0.35;
          }}
          scene.add(sunLight);

          // Grid & Tactical Boundary
          const gridHelper = new THREE.GridHelper(36, 18, 0x19F3FF, 0x0C2333);
          gridHelper.position.y = -0.01;
          scene.add(gridHelper);

          // TERRAIN & SOIL BLOCK
          const plotWidth = 24;
          const plotLength = 24;
          const topsoilThickness = 1.2;
          const subsoilThickness = 4.5;

          const topsoilMat = new THREE.MeshStandardMaterial({{
            color: new THREE.Color(CONFIG.soilColorTop),
            roughness: 0.9,
            metalness: 0.1
          }});

          const subsoilMat = new THREE.MeshStandardMaterial({{
            color: new THREE.Color(CONFIG.soilColorSub),
            roughness: 0.95,
            metalness: 0.05
          }});

          // Topsoil surface mesh
          const topGeom = new THREE.BoxGeometry(plotWidth, topsoilThickness, plotLength);
          const topMesh = new THREE.Mesh(topGeom, topsoilMat);
          topMesh.position.set(0, -topsoilThickness / 2, 0);
          topMesh.receiveShadow = true;
          scene.add(topMesh);

          // If cutaway enabled, show subsoil cross-section block
          if (CONFIG.showCutaway) {{
            const subGeom = new THREE.BoxGeometry(plotWidth, subsoilThickness, plotLength);
            const subMesh = new THREE.Mesh(subGeom, subsoilMat);
            subMesh.position.set(0, -topsoilThickness - (subsoilThickness / 2), 0);
            subMesh.receiveShadow = true;
            scene.add(subMesh);

            // Soil strata depth markers
            createDepthMarker("-0.3m (Topsoil)", -topsoilThickness);
            createDepthMarker("-1.0m (Subsoil)", -topsoilThickness - 2.5);
            createDepthMarker("-" + CONFIG.rootDepth.toFixed(1) + "m (Max Root)", -topsoilThickness - (CONFIG.rootDepth * 2.2));
          }}

          function createDepthMarker(text, yPos) {{
            const lineGeom = new THREE.BufferGeometry().setFromPoints([
              new THREE.Vector3(-plotWidth / 2 - 0.5, yPos, plotLength / 2 + 0.1),
              new THREE.Vector3(plotWidth / 2 + 0.5, yPos, plotLength / 2 + 0.1)
            ]);
            const lineMat = new THREE.LineBasicMaterial({{ color: 0x19F3FF, transparent: true, opacity: 0.6 }});
            const line = new THREE.Line(lineGeom, lineMat);
            scene.add(line);
          }}

          // PROCEDURAL CROPS VIA INSTANCED MESH
          const growthStage = CONFIG.growthStage; // 0 to 5
          const stageScales = [0.05, 0.20, 0.55, 0.85, 0.98, 1.0];
          const currentScale = stageScales[growthStage];

          const rows = 10;
          const plantsPerRow = 14;
          const totalPlants = rows * plantsPerRow;

          // Color palette based on crop type and stage
          let plantColor = 0x2E7D32; // Default lush green
          if (growthStage === 0) {{
            plantColor = 0x5D4037; // Sown furrow/soil
          }} else if (growthStage === 4) {{
            plantColor = CONFIG.isCereal ? 0xC0CA33 : 0x388E3C; // Ripening
          }} else if (growthStage === 5) {{
            plantColor = CONFIG.isCereal ? 0xE6C160 : 0x6D4C41; // Harvest golden/mature
          }}

          const plantMaterial = new THREE.MeshStandardMaterial({{
            color: plantColor,
            roughness: 0.6,
            metalness: 0.1
          }});

          // Plant Geometry: Stalk + Leaves
          let plantGeometry;
          if (CONFIG.isCereal) {{
            // Slender cereal stalk with tapering top
            plantGeometry = new THREE.CylinderGeometry(0.04, 0.08, 1.8, 6);
            plantGeometry.translate(0, 0.9, 0);
          }} else {{
            // Broadleaf bushy canopy
            plantGeometry = new THREE.ConeGeometry(0.45, 1.4, 7);
            plantGeometry.translate(0, 0.7, 0);
          }}

          const instancedCrops = new THREE.InstancedMesh(plantGeometry, plantMaterial, totalPlants);
          instancedCrops.castShadow = true;
          instancedCrops.receiveShadow = true;

          const dummy = new THREE.Object3D();
          let pIdx = 0;
          const rowSpacing = plotWidth / (rows + 1);
          const colSpacing = plotLength / (plantsPerRow + 1);

          for (let r = 0; r < rows; r++) {{
            for (let c = 0; c < plantsPerRow; c++) {{
              const px = -plotWidth / 2 + (r + 1) * rowSpacing + (Math.sin(c * 1.5) * 0.15);
              const pz = -plotLength / 2 + (c + 1) * colSpacing + (Math.cos(r * 1.5) * 0.15);
              
              // Jitter height slightly for organic realism
              const hVar = 0.85 + (Math.sin(r * 3 + c * 7) * 0.15);
              const scaleY = currentScale * hVar;
              const scaleXZ = Math.min(1.0, currentScale * 1.2);

              dummy.position.set(px, 0, pz);
              dummy.scale.set(scaleXZ, scaleY, scaleXZ);
              dummy.rotation.y = Math.sin(r + c) * 0.4;
              dummy.updateMatrix();

              instancedCrops.setMatrixAt(pIdx++, dummy.matrix);
            }}
          }}
          instancedCrops.instanceMatrix.needsUpdate = true;
          scene.add(instancedCrops);

          // ROOT ARCHITECTURE (IF CUTAWAY VISIBLE)
          const rootLinesGroup = new THREE.Group();
          if (CONFIG.showCutaway && growthStage > 0) {{
            const rootDepthVisual = CONFIG.rootDepth * 2.2 * (growthStage / 5.0);
            const frontRowCrops = plantsPerRow;

            for (let c = 0; c < frontRowCrops; c += 2) {{
              const rx = -plotWidth / 2 + (rows / 2) * rowSpacing + (c * colSpacing * 0.6) - 4;
              const rz = plotLength / 2 - 0.2; // Placed right at the cutaway boundary

              // Central Taproot
              const points = [
                new THREE.Vector3(rx, 0, rz),
                new THREE.Vector3(rx + (Math.sin(c) * 0.15), -rootDepthVisual * 0.4, rz),
                new THREE.Vector3(rx + (Math.cos(c) * 0.25), -rootDepthVisual * 0.75, rz),
                new THREE.Vector3(rx + (Math.sin(c * 2) * 0.1), -rootDepthVisual, rz)
              ];
              const rootGeom = new THREE.BufferGeometry().setFromPoints(points);
              const rootMat = new THREE.LineBasicMaterial({{
                color: 0xE8F6FF,
                linewidth: 2,
                transparent: true,
                opacity: 0.85
              }});
              const rootLine = new THREE.Line(rootGeom, rootMat);
              rootLinesGroup.add(rootLine);

              // Secondary lateral fine rootlets
              const lateralPoints1 = [
                new THREE.Vector3(rx, -rootDepthVisual * 0.3, rz),
                new THREE.Vector3(rx - 0.5, -rootDepthVisual * 0.45, rz)
              ];
              const lateralGeom1 = new THREE.BufferGeometry().setFromPoints(lateralPoints1);
              rootLinesGroup.add(new THREE.Line(lateralGeom1, rootMat));

              const lateralPoints2 = [
                new THREE.Vector3(rx, -rootDepthVisual * 0.55, rz),
                new THREE.Vector3(rx + 0.6, -rootDepthVisual * 0.7, rz)
              ];
              const lateralGeom2 = new THREE.BufferGeometry().setFromPoints(lateralPoints2);
              rootLinesGroup.add(new THREE.Line(lateralGeom2, rootMat));
            }}
            scene.add(rootLinesGroup);
          }}

          // ANIMATED WATER INFILTRATION DROPLETS
          const particleCount = 200;
          const particleGeom = new THREE.BufferGeometry();
          const particlePositions = new Float32Array(particleCount * 3);
          const particleSpeeds = new Float32Array(particleCount);

          for (let i = 0; i < particleCount; i++) {{
            particlePositions[i * 3 + 0] = (Math.random() - 0.5) * (plotWidth - 2);
            particlePositions[i * 3 + 1] = -Math.random() * (topsoilThickness + subsoilThickness);
            particlePositions[i * 3 + 2] = (plotLength / 2) - (Math.random() * 2.5); // near cutaway edge
            particleSpeeds[i] = 0.015 + Math.random() * 0.025;
          }}

          particleGeom.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));

          const particleMat = new THREE.PointsMaterial({{
            color: 0x19F3FF,
            size: 0.12,
            transparent: true,
            opacity: 0.75
          }});

          const infiltrationParticles = new THREE.Points(particleGeom, particleMat);
          if (CONFIG.showCutaway && CONFIG.showInfiltration) {{
            scene.add(infiltrationParticles);
          }}

          // ANIMATION LOOP
          let clock = new THREE.Clock();

          function animate() {{
            requestAnimationFrame(animate);
            const delta = clock.getDelta();

            // Animate infiltration particles
            if (CONFIG.showCutaway && CONFIG.showInfiltration) {{
              const positions = infiltrationParticles.geometry.attributes.position.array;
              const maxY = 0;
              const minY = -(topsoilThickness + subsoilThickness);

              for (let i = 0; i < particleCount; i++) {{
                positions[i * 3 + 1] -= particleSpeeds[i];
                if (positions[i * 3 + 1] < minY) {{
                  positions[i * 3 + 1] = maxY;
                }}
              }}
              infiltrationParticles.geometry.attributes.position.needsUpdate = true;
            }}

            controls.update();
            renderer.render(scene, camera);
          }}
          animate();

          // Handle Window Resize
          window.addEventListener('resize', onWindowResize, false);
          function onWindowResize() {{
            const newW = container.clientWidth || 800;
            const newH = container.clientHeight || 600;
            camera.aspect = newW / newH;
            camera.updateProjectionMatrix();
            renderer.setSize(newW, newH);
          }}
        }}
      </script>
    </body>
    </html>
    """

    st.components.v1.html(twin_html, height=620)

    # 3 Tabbed Agronomic Analysis Panels Below the 3D Deck
    render_html('<div class="module-header" style="margin-top: 25px;">02 // TWIN SCIENTIFIC PROFILE & CANOPY DYNAMICS</div>')

    tab_profile, tab_phenology, tab_soil = st.tabs([
        "🌾 Crop Morphometry", "📅 Phenological Timeline", "🧪 Soil Stratigraphy & Infiltration"
    ])

    with tab_profile:
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            render_html(f"""
            <div class="holo-metric-card">
              <div class="holo-label">MAX ROOTING DEPTH</div>
              <div class="holo-val">{root_depth_m:.1f} <span style="font-size:0.9rem; color:#8FA6B8;">m</span></div>
              <div class="holo-delta positive">CIT: {crop_meta.get('fao_source', 'FAO-56')}</div>
            </div>
            """)
        with col_m2:
            render_html(f"""
            <div class="holo-metric-card">
              <div class="holo-label">SEASON WATER REQUIREMENT</div>
              <div class="holo-val">{water_need:.0f} <span style="font-size:0.9rem; color:#8FA6B8;">mm</span></div>
              <div class="holo-delta {'positive' if water_need <= 450 else 'amber'}">DROUGHT TOL: {crop_meta.get('drought_tolerance', 'Moderate').upper()}</div>
            </div>
            """)
        with col_m3:
            render_html(f"""
            <div class="holo-metric-card">
              <div class="holo-label">NITROGEN FIXATION</div>
              <div class="holo-val" style="color: {'#2CFFB0' if crop_meta.get('nitrogen_fixing') == 'Yes' else '#8FA6B8'};">{crop_meta.get('nitrogen_fixing', 'No').upper()}</div>
              <div class="holo-delta positive">FAMILY: {family.upper()}</div>
            </div>
            """)
        with col_m4:
            render_html(f"""
            <div class="holo-metric-card">
              <div class="holo-label">OPTIMAL SOIL PH RANGE</div>
              <div class="holo-val">{crop_meta.get('ph_min', 6.0)} - {crop_meta.get('ph_max', 7.5)}</div>
              <div class="holo-delta positive">SITE PH: {soil_data.get('ph', 6.8)}</div>
            </div>
            """)

        render_html(f"""
        <div class="holo-metric-card" style="margin-top: 15px;">
          <div class="holo-label">AGRONOMIC PROFILE & CANOPY ARCHITECTURE</div>
          <div style="font-family: 'Rajdhani', sans-serif; font-size: 1.05rem; color: #E8F6FF; line-height: 1.6; margin-top: 6px;">
            {crop_meta.get('approximate_notes', 'Standard agronomic crop profile based on FAO crop database.')}
          </div>
        </div>
        """)

    with tab_phenology:
        st.markdown(f"### Phenological Growth Phases for {selected_crop_name}")
        stages_info = [
            ("Stage 0: Sowing / Imbibition", "Seed rests in furrow; water uptake activates enzymatic digestion of cotyledon reserves. Root radicle emerges downward."),
            ("Stage 1: Emergence (VE-V2)", "Hypocotyl pushes cotyledons above surface. Initial taproot branches into primary laterals (0-20cm depth)."),
            ("Stage 2: Vegetative Growth (V4-VT)", "Rapid leaf area index (LAI) expansion, high photosynthetic nitrogen assimilation. Root system expands through topsoil horizon."),
            ("Stage 3: Flowering / Anthesis (R1)", "Peak water sensitivity. Pollen shedding and fertilization occur. Any extreme heat (>35°C) risks floret sterility."),
            ("Stage 4: Grain / Pod Fill (R3-R5)", "Carbohydrates translocate from stems and leaves to fill grain/seed. Transpiration demand remains elevated."),
            ("Stage 5: Physiological Maturity (R6)", "Black layer or abscission layer forms; grain moisture drops toward harvest levels. Foliage desiccates into organic residue.")
        ]
        for s_title, s_desc in stages_info:
            active_marker = " 🟢 **[ACTIVE STAGE IN 3D DECK]**" if s_title.startswith(f"Stage {growth_stage}") else ""
            st.markdown(f"**{s_title}**{active_marker}")
            st.caption(s_desc)

    with tab_soil:
        st.markdown(f"### Stratigraphic Soil Profile — {farm_name}")
        st.markdown(f"""
        - **Horizon A (Topsoil 0 - 30 cm):** High organic matter zone. Texture: `{soil_texture}`. Organic Carbon: `{soil_data.get('organic_carbon_g_kg', 12.0)} g/kg`. Primary rooting density zone for lateral nutrient uptake.
        - **Horizon B (Subsoil 30 - 100 cm):** Dense illuvial mineral stratum. High moisture retention capacity. Provides emergency drought buffer during dry spells.
        - **Horizon C (Deep Substratum 100+ cm):** Weathered bedrock or parent material. Accessed primarily by deep-rooted taproots (e.g. Alfalfa, Sorghum, Sunflower).
        """)
