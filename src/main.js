import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import "./style.css";

document.querySelector("#app").innerHTML = `
  <main id="viewer">
    <canvas id="neuron-canvas"></canvas>

    <section id="hud">
      <p class="eyebrow">NEUROVIS 1.1</p>
      <h1>Web Explorer</h1>
      <p id="status">Loading neuron...</p>

      <button id="reset-camera" type="button">
        Reset camera
      </button>
    </section>
  </main>
`;

const canvas = document.querySelector("#neuron-canvas");
const statusElement = document.querySelector("#status");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x05070d);

const camera = new THREE.PerspectiveCamera(
  45,
  window.innerWidth / window.innerHeight,
  0.001,
  100000
);

camera.position.set(0, 0, 10);

const renderer = new THREE.WebGLRenderer({
  canvas,
  antialias: true
});

renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;

const ambientLight = new THREE.AmbientLight(0xffffff, 1.8);
scene.add(ambientLight);

const keyLight = new THREE.DirectionalLight(0xffffff, 3);
keyLight.position.set(5, 8, 10);
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0xffffff, 1.5);
fillLight.position.set(-5, -4, -8);
scene.add(fillLight);

let neuronModel = null;
let animationMixer = null;

const clock = new THREE.Clock();
const loader = new GLTFLoader();

loader.load(
  `${import.meta.env.BASE_URL}models/neuron.glb`,

  (gltf) => {
    neuronModel = gltf.scene;

    applyNeuronMaterial(neuronModel);
    scene.add(neuronModel);
    frameModel(neuronModel);

    if (gltf.animations.length > 0) {
      animationMixer = new THREE.AnimationMixer(neuronModel);

      for (const clip of gltf.animations) {
        animationMixer.clipAction(clip).play();
      }

      statusElement.textContent =
        `Neuron loaded • ${gltf.animations.length} animation clip(s)`;
    } else {
      statusElement.textContent = "Neuron loaded • no animation clips";
    }

    console.log("NeuroVis GLB loaded:", gltf);
  },

  (progressEvent) => {
    if (progressEvent.total > 0) {
      const percent = Math.round(
        (progressEvent.loaded / progressEvent.total) * 100
      );

      statusElement.textContent = `Loading neuron: ${percent}%`;
    }
  },

  (error) => {
    console.error("Could not load neuron.glb:", error);
    statusElement.textContent =
      "Could not load neuron.glb. Check the browser console.";
  }
);

function applyNeuronMaterial(model) {
  const neuronMaterial = new THREE.MeshStandardMaterial({
    color: 0x48d7c4,
    roughness: 0.5,
    metalness: 0.05
  });

  model.traverse((object) => {
    if (object.isMesh) {
      object.material = neuronMaterial;
    }
  });
}

function frameModel(model) {
  const box = new THREE.Box3().setFromObject(model);

  if (box.isEmpty()) {
    statusElement.textContent = "Neuron loaded, but its geometry is empty.";
    return;
  }

  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());

  model.position.sub(center);

  const largestDimension = Math.max(size.x, size.y, size.z);
  const fieldOfViewRadians = THREE.MathUtils.degToRad(camera.fov);

  let cameraDistance =
    largestDimension / (2 * Math.tan(fieldOfViewRadians / 2));

  cameraDistance *= 1.5;

  camera.position.set(0, 0, Math.max(cameraDistance, 1));

  camera.near = Math.max(cameraDistance / 1000, 0.001);
  camera.far = Math.max(cameraDistance * 100, 100);
  camera.updateProjectionMatrix();

  controls.target.set(0, 0, 0);
  controls.update();
  controls.saveState();
}

document
  .querySelector("#reset-camera")
  .addEventListener("click", () => {
    controls.reset();
  });

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();

  renderer.setSize(window.innerWidth, window.innerHeight);
});

function animate() {
  requestAnimationFrame(animate);

  const deltaTime = clock.getDelta();

  if (animationMixer) {
    animationMixer.update(deltaTime);
  }

  controls.update();
  renderer.render(scene, camera);
}

animate();
