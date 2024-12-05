<script lang="ts">
import { onDestroy, onMount } from "svelte";
import { writable } from "svelte/store";
import { destroyScanner, scanQRCode, toggleScanner } from "../utils/camera";
import { getAppVersion } from "../utils/reqs";
import {
	handleFileUpload,
	handleFormSubmit,
	triggerFileInput,
} from "../utils/file-upload";
import { browser } from "$app/environment";
    import { registerSw } from "../utils/register-sw";

const qrCodeData = writable<string | null>(null);
const showPopup = writable<boolean>(false);
const productName = writable<string | null>(null);
let operable = "";

async function loadQRScanner() {
	const result = await scanQRCode();
	if (result) {
		toggleScanner(false);
		qrCodeData.set(result);
		productName.set(result);
		showPopup.set(true);
    document.getElementById('qrScanner')?.classList.add('hidden');
	} else { // impossible state: (TODO show errors in the ui)
		qrCodeData.set("");
		productName.set("");
		showPopup.set(false);
		qrCodeData.set("Unable to read QR code.");
	}
}

async function registerServiceWorker() {
  const whatisthis = await registerSw('sw.js', /* 12 hours */ 1000 * 60 * 60 * 12);
  console.log(whatisthis)
}

onMount(() => {
  registerServiceWorker();
	loadQRScanner();
	getAppVersion();
});

onDestroy(() => {
	if (browser) destroyScanner();
});
</script>

<div id="qrScanner" class="relative w-full h-screen flex items-center justify-center bg-black">
  <div id="loadingMessage">🎥 Unable to access video stream (please make sure you have a webcam enabled)</div>
  <canvas id="canvas" hidden style="position: absolute; top: 0; left: 0; width: 100vw; height: 100vh;"></canvas>
  <div id="output" hidden style="position: absolute; top: 20px; right: 20px; z-index: 10;">
    <div id="outputMessage">No QR code detected.</div>
    <div hidden><b>Data:</b> <span id="outputData"></span></div>
  </div>
  <button 
    id="toggleFlashlight" 
    class="flashlight-btn" >
    Toggle Flashlight
  </button>
</div>

{#if $showPopup}
  <div
    class="popup-backdrop fixed inset-0 bg-gray-800 bg-opacity-50 flex items-center justify-center"
  >
    <div
      class="popup-content bg-white w-full max-w-sm rounded-lg shadow-lg p-4 md:p-6"
    >
      <div class="flex justify-between items-center">
        <h2 class="text-lg font-bold">Issue Details for: {$productName}</h2>
        <button
          onclick={async () => {
            showPopup.set(false);
            document.getElementById('qrScanner')?.classList.remove('hidden');
            toggleScanner(true);
            loadQRScanner();
          }}
          class="border border-gray-300 rounded-lg p-2 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Close
        </button>
      </div>
      <form class="space-y-4 mt-4" id="malfunction-report-form" onsubmit={handleFormSubmit}>
        <div>
          <label
            for="product-details"
            class="block text-sm font-medium text-gray-700">Product Details</label>
          <textarea
            id="product-details"
            rows="3"
            class="w-full mt-1 border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Describe the product in detail"
          ></textarea>
        </div>
        <div>
          <label
            for="product-operable"
            class="block text-sm font-medium text-gray-700"
            >Is it operable?</label
          >
          <div class="flex space-x-4 mt-2">
            <button
              type="button"
              class="w-1/2 text-center py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              class:active={operable === "yes"}
              class:bg-blue-500={operable === "yes"}
              class:text-white={operable === "yes"}
              class:text-black={operable !== "yes"}
              onclick={() => (operable = "yes")}
            >
              Yes
            </button>
            <button
              type="button"
              class="w-1/2 text-center py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              class:active={operable === "no"}
              class:bg-blue-500={operable === "no"}
              class:text-white={operable === "no"}
              class:text-black={operable !== "no"}
              onclick={() => (operable = "no")}
            >
              No
            </button>
          </div>
        </div>
        <div>
          <label
            for="attachments"
            class="block text-sm font-medium text-gray-700"
            >Add Photos or Videos</label
          >
          <div
            class="w-full mt-1 border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            id="custom-file-upload"
          >
            <p class="text-sm text-gray-600">Upload up to 4 files</p>
            <input
              type="file"
              id="file-input"
              onchange={handleFileUpload}
              multiple
              accept="image/*, video/*"
              class="hidden"
            />
            <button
              type="button"
              class="mt-2 w-full py-2 bg-gray-100 text-sm rounded-lg border hover:bg-gray-200"
              onclick={triggerFileInput}
            >
              Choose Files
            </button>

            <ul id="file-list" class="mt-2 text-sm text-gray-700"></ul>
          </div>
        </div>
        <div>
          <label
            for="issue-description"
            class="block text-sm font-medium text-gray-700"
            >Describe the Issue</label
          >
          <textarea
            id="issue-description"
            rows="5"
            class="w-full mt-1 border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Provide a detailed explanation of the issue"
          ></textarea>
        </div>
        <button
          type="submit"
          class="w-full py-3 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Submit Issue
        </button>
      </form>
    </div>
  </div>
{/if}

<style>
    #loadingMessage {
      text-align: center;
      padding: 40px;
      background-color: #eee;
    }

    #canvas {
      width: 100%;
    }

    #output {
      margin-top: 20px;
      background: #eee;
      padding: 10px;
      padding-bottom: 0;
    }

    #output div {
      padding-bottom: 10px;
      word-wrap: break-word;
    }

    .flashlight-btn {
      position: fixed;
      bottom: 20px;
      left: 50%;
      transform: translateX(-50%);
      padding: 10px 20px;
      background-color: #007bff;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }
</style>
