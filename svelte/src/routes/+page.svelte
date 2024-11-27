<script lang="ts">
  import { onMount } from "svelte";
  import { writable } from "svelte/store";
  import { BrowserMultiFormatReader } from "@zxing/browser";

  let videoElement: HTMLVideoElement | null = null;
  let canvasElement: HTMLCanvasElement | null = null;

  const qrCodeData = writable<string | null>(null);
  const showPopup = writable<boolean>(false);
  const productName = writable<string | null>(null);

  let stream: MediaStream | null = null;
  let operable = "";
  const maxFiles = 4;

  function stopCamera() {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      stream = null;
    }
  }

  async function startCamera() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      });

      if (videoElement) {
        videoElement.srcObject = stream;
        await videoElement.play();
        scanQRCode(); // Start scanning QR codes once the camera feed is ready
      } else {
        console.error("Video element is not available.");
      }
    } catch (error) {
      console.error("Error starting camera:", error);
      qrCodeData.set("Unable to access the camera.");
    }
  }

  function triggerFileInput(): void {
    const fileInput = document.getElementById("file-input") as HTMLInputElement;
    if (fileInput) {
      fileInput.click();
    } else {
      console.error("File input element not found.");
    }
  }

  async function scanQRCode() {
    const codeReader = new BrowserMultiFormatReader();

    try {
      if (videoElement) {
        // Ensure videoElement is not null
        await codeReader.decodeFromVideoDevice(
          undefined,
          videoElement,
          (result) => {
            if (result) {
              qrCodeData.set(result.getText());
              productName.set(result.getText());
              showPopup.set(true);
              stopCamera();
            }
          }
        );
      } else {
        console.error("Video element is not initialized.");
      }
    } catch (error) {
      console.error("QR scanning error:", error);
    }
  }

  function closePopup() {
    showPopup.set(false);
    startCamera();
  }

  onMount(() => {
    if (videoElement) {
      startCamera();
    }

    const fileInput = document.getElementById("file-input") as HTMLInputElement;
    const fileList = document.getElementById("file-list") as HTMLUListElement;

    function handleFileUpload(event: Event): void {
      const target = event.target as HTMLInputElement;
      const files = Array.from(target.files || []);

      if (files.length > maxFiles) {
        alert(`You can only upload up to ${maxFiles} files.`);
        fileInput.value = "";
        return;
      }

      fileList.innerHTML = "";

      files.forEach((file, index) => {
        const listItem = document.createElement("li");
        listItem.textContent = `${index + 1}. ${file.name}`;
        fileList.appendChild(listItem);
      });
    }

    function handleFormSubmit(event: Event): void {
      event.preventDefault();

      const productDetails = (
        document.getElementById("product-details") as HTMLTextAreaElement
      ).value;
      const issueDescription = (
        document.getElementById("issue-description") as HTMLTextAreaElement
      ).value;

      alert(
        "Form submitted with the following details:\n" +
          `Product Details: ${productDetails}\n` +
          `Issue Description: ${issueDescription}\n` +
          `Number of Files: ${(fileInput.files || []).length}`
      );
    }

    fileInput.addEventListener("change", handleFileUpload);
    document
      .querySelector("form")
      ?.addEventListener("submit", handleFormSubmit);

    return stopCamera;
  });
</script>

<div
  class="camera-container w-full h-screen flex items-center justify-center bg-black"
>
  <div class="qr-overlay"></div>
  {#if !$showPopup}
    <video
      bind:this={videoElement}
      autoplay
      playsinline
      class="camera-feed w-full h-auto object-cover"
    >
      <track kind="captions" label="Camera feed" srclang="en" default />
    </video>

    <canvas bind:this={canvasElement} class="hidden"></canvas>
  {/if}
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
          onclick={closePopup}
          class="border border-gray-300 rounded-lg p-2 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Close
        </button>
      </div>
      <form class="space-y-4 mt-4">
        <div>
          <label
            for="product-details"
            class="block text-sm font-medium text-gray-700"
            >Product Details</label
          >
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
  .camera-feed {
    position: absolute;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    object-fit: cover; /* Ensures the video covers the container without distortion */
  }

  .camera-container {
    position: relative;
  }

  .qr-overlay {
    position: absolute;
    inset: 0;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 10;
  }

  .qr-overlay::after {
    content: "";
    display: block;
    width: 50vmin;
    height: 25vmax;
    background: transparent;
    border: 3px solid rgba(0, 255, 0, 0.7);
    border-radius: 10px;
    box-shadow: 0 0 15px 4px rgba(0, 255, 0, 0.5);
    animation: pulse 1.5s infinite;
    z-index: 20;
  }

  @keyframes pulse {
    0% {
      box-shadow: 0 0 15px 4px rgba(0, 255, 0, 0.5);
      opacity: 1;
    }
    50% {
      box-shadow: 0 0 25px 10px rgba(0, 255, 0, 0.3);
      opacity: 0.8;
    }
    100% {
      box-shadow: 0 0 15px 4px rgba(0, 255, 0, 0.5);
      opacity: 1;
    }
  }
</style>
