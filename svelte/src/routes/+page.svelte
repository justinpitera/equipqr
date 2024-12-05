<script lang="ts">
import { onDestroy, onMount } from "svelte";
import { writable } from "svelte/store";
import {
	LightbulbOff,
	Lightbulb,
	GalleryThumbnails,
	Video,
	Upload,
	Trash,
} from "lucide-svelte";
import { destroyScanner, scanQRCode, toggleScanner } from "../utils/camera";
import { getAppVersion } from "../utils/reqs";
import { browser } from "$app/environment";
import { registerSw } from "../utils/register-sw";
import { Drawer, Button, CloseButton } from "flowbite-svelte";
import { InfoCircleSolid, ArrowRightOutline } from "flowbite-svelte-icons";
import { sineIn } from "svelte/easing";

interface MediaFile {
	file: File;
	url: string;
	type: string;
	deleteFile: (event: Event) => void;
	handleClick: () => void;
}

const maxFiles = 4;
const mediaFiles = writable<MediaFile[]>([]);

let isDragging = false;
let fullscreenViewer: HTMLElement | null;
let fullscreenImage: HTMLImageElement | null;
let fullscreenVideo: HTMLVideoElement | null;

let pressTimer: NodeJS.Timeout;
let closeReportHidden = true;
let transitionParamsTop = {
	y: -320,
	duration: 200,
	easing: sineIn,
};

const qrCodeData = writable<string | null>(null);
const showPopup = writable<boolean>(false);
const productName = writable<string | null>(null);
const flashlightToggle = writable<boolean>(false);
const wiggleModeJustPressed = writable<boolean>(false);
const wiggleModeEnabled = writable<boolean>(false);
let operable = "";

function handleFormSubmit(event: Event): void {
	event.preventDefault();
	const uploadedFiles = $mediaFiles.map(
		(file) => `${file.file.name} (${file.file.size} bytes)`,
	);
	alert(`Selected files:\n${uploadedFiles.join("\n")}`);
	const issueDescription = (
		document.getElementById("issue-description") as HTMLTextAreaElement
	).value;
	alert(
		`Form submitted with the following details:\nIssue Description: ${issueDescription}\nNumber of Files: ${$mediaFiles.length}`,
	);
}

function disableContextMenu(event: Event): boolean {
	event.preventDefault();
	event.stopPropagation();
	event.stopImmediatePropagation();
	return false;
}

async function loadQRScanner(forceDebug?: string) {
	const result = forceDebug || (await scanQRCode());
	if (result) {
		toggleScanner(false);
		qrCodeData.set(result);
		productName.set(result);
		flashlightToggle.set(false);
		showPopup.set(true);
		document.getElementById("qrScanner")?.classList.add("hidden");
	} else {
		// impossible state: (TODO show errors in the ui)
		qrCodeData.set("");
		productName.set("");
		showPopup.set(false);
		qrCodeData.set("Unable to read QR code.");
	}
}

async function registerServiceWorker() {
	await registerSw("sw.js", /* 12 hours */ 1000 * 60 * 60 * 12);
}

const startWiggle = () => {
	isDragging = false;
	const onMove = () => {
		isDragging = true;
		document.removeEventListener("mousemove", onMove);
		document.removeEventListener("touchmove", onMove);
	};
	document.addEventListener("mousemove", onMove);
	document.addEventListener("touchmove", onMove);
	pressTimer = setTimeout(() => {
		if (!isDragging) {
			document.removeEventListener("mousemove", () => {});
			document.removeEventListener("touchmove", () => {});
			wiggleModeJustPressed.set(true);
			wiggleModeEnabled.set(true);
		}
	}, 500);
};

const stopWiggle = () => {
	clearTimeout(pressTimer);
	document.removeEventListener("mousemove", () => {});
	document.removeEventListener("touchmove", () => {});
	setTimeout(() => {
		wiggleModeJustPressed.set(false);
	}, 100);
};

const handleFileChange = (event: Event) => {
	const target = event.target as HTMLInputElement;
	if (target?.files) {
		const newFiles: MediaFile[] = [];
		for (const file_obj of Array.from(target.files)) {
			const file = file_obj as File;
			const url = URL.createObjectURL(file);
			const newMedia: MediaFile = {
				file,
				url,
				type: file.type,
				deleteFile: (e: Event) => {
					e.stopPropagation();
					wiggleModeJustPressed.set(false);
					wiggleModeEnabled.set(false);
					const confirmDelete = confirm(
						"Are you sure you want to delete this file?",
					);
					if (confirmDelete) {
						mediaFiles.update((files) =>
							files.filter((item) => item.url !== url),
						);
					}
				},
				handleClick: () => {
					if (!fullscreenVideo || !fullscreenImage || !fullscreenViewer) return;
					if ($wiggleModeJustPressed) return;
					if ($wiggleModeEnabled) {
						wiggleModeJustPressed.set(false);
						wiggleModeEnabled.set(false);
					} else {
						fullscreenViewer.classList.remove("hidden");
						fullscreenViewer.classList.add("flex");
						if (file.type.startsWith("image/")) {
							fullscreenImage.src = url;
							fullscreenImage.classList.remove("hidden");
							fullscreenVideo.classList.add("hidden");
						} else if (file.type.startsWith("video/")) {
							fullscreenVideo.src = url;
							fullscreenVideo.classList.remove("hidden");
							fullscreenImage.classList.add("hidden");
						}
					}
				},
			};
			newFiles.push(newMedia);
		}
		mediaFiles.update((files) => [...files, ...newFiles]);
		target.value = "";
	}
};

const closeFullscreen = () => {
	if (!fullscreenVideo || !fullscreenImage || !fullscreenViewer) return;
	fullscreenViewer.classList.add("hidden");
	fullscreenViewer.classList.remove("flex");
	fullscreenImage.src = "";
	fullscreenVideo.src = "";
};

onMount(() => {
	registerServiceWorker();
	loadQRScanner("AHU 00001"); // Debug by adding an ID here
	getAppVersion();

	// Cleanup
	return () => {};
});

onDestroy(() => {
	if (browser) destroyScanner();
});
</script>

<Drawer placement="top" width="w-full" transitionType="fly" transitionParams={transitionParamsTop} bind:hidden={closeReportHidden}>
  <div class="flex items-center justify-between">
    <h5 id="drawer-label" class="inline-flex items-center mb-4 text-base font-semibold text-gray-500 dark:text-gray-400">
      <InfoCircleSolid oncontextmenu={disableContextMenu} class="w-5 h-5 me-2.5" />Cancel Report?
    </h5>
    <CloseButton on:click={() => (closeReportHidden = true)} class="mb-4 dark:text-white" />
  </div>
  <p class="max-w-lg mb-6 text-sm text-gray-500 dark:text-gray-400">
    Are you sure you want to cancel the report for:<br/>{$productName}?
  </p>
  <Button type="button" color="light" on:click={() => (closeReportHidden = true)} class="p-2 pr-3 pl-3 select-none">No, Let me finish it</Button>
  <Button type="button" color="light" on:click={() => {
    closeReportHidden = true;
    showPopup.set(false);
    document.getElementById('qrScanner')?.classList.remove('hidden');
    toggleScanner(true);
    loadQRScanner();
  }} href="/" class="px-4 p-2 pr-3 pl-3 select-none">Yes, Cancel it <ArrowRightOutline oncontextmenu={disableContextMenu} class="w-5 h-5 ms-2" /></Button>
</Drawer>

<div id="qrScanner" class="relative w-full h-screen flex items-center justify-center bg-black">
  <div id="loadingMessage">🎥 Unable to access video stream (please make sure you have a webcam enabled)</div>
  <canvas id="canvas" hidden style="position: absolute; top: 0; left: 0; width: 100vw; height: 100vh;"></canvas>
  <div id="output" hidden>
    <div id="outputMessage">No QR code detected.</div>
    <div hidden><b>Data:</b> <span id="outputData"></span></div>
  </div>
  <button type="button" id="toggleFlashlight" class="select-none" onclick={() => {
		flashlightToggle.set(!$flashlightToggle);
  }}>
    {#if $flashlightToggle}
      <Lightbulb oncontextmenu={disableContextMenu} class="flashlight-btn animate-pulse w-8 h-8" style="filter: drop-shadow(0px 0px 6px yellow) blur(0.2px)" />
    {:else}
      <LightbulbOff oncontextmenu={disableContextMenu} class="flashlight-btn w-8 h-8" />
    {/if}
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
          type="button"
          onclick={async () => {
            closeReportHidden = false;
          }}
          class="border border-gray-300 rounded-lg p-2 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 select-none"
        >
          Close
        </button>
      </div>
      <form class="space-y-4 mt-4" id="malfunction-report-form" onsubmit={handleFormSubmit}>
        <div>
          <label
            for="issue-description"
            class="block text-sm font-medium text-gray-700"
            >Describe the Issue</label
          >
          <textarea
            id="issue-description"
            rows="5"
            class="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Provide a detailed explanation of the issue"
          ></textarea>
        </div>
        <div style="margin-top: 0.5rem;">
          <label
            for="product-operable"
            class="block text-sm font-medium text-gray-700"
            >Is it operable?</label
          >
          <div class="flex space-x-4 mt-2">
            <button
              type="button"
              class="w-1/2 text-center py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 select-none"
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
              class="w-1/2 text-center py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 select-none"
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
            <p class="text-center text-sm text-gray-600 mb-2">Upload up to 4 files</p>
            <div class="flex justify-center">
              <label for="takePicture" class="file-button w-12 h-12">
                <GalleryThumbnails oncontextmenu={disableContextMenu} class="w-6 h-6" />
              </label>
              <input id="takePicture" type="file" accept="image/*" capture="environment" multiple class="file-input" onchange={handleFileChange}>
              <label for="captureVideo" class="file-button ml-4 w-12 h-12">
                <Video oncontextmenu={disableContextMenu} class="w-6 h-6" />
              </label>
              <input id="captureVideo" type="file" accept="video/*" capture="environment" multiple class="file-input" onchange={handleFileChange}>
              <label for="selectMediaFiles" class="file-button ml-4 w-12 h-12">
                <Upload oncontextmenu={disableContextMenu} class="w-6 h-6" />
              </label>
              <input id="selectMediaFiles" type="file" accept="image/*,video/*" multiple class="file-input" onchange={handleFileChange}>
            </div>
            {#if $mediaFiles.length > 0}
              <hr class="my-4" />
              <div id="gallery-container">
                <div id="gallery">
                  {#each $mediaFiles as { url, type, deleteFile, handleClick }}
                    <div class={`gallery-item select-none relative ${$wiggleModeEnabled ? 'wiggle' : ''}`} onclick={handleClick} onkeypress={handleClick} onmousedown={startWiggle} onmouseup={stopWiggle} onmouseleave={() => {
                      clearTimeout(pressTimer);
                      isDragging = false;
                    }} ontouchstart={startWiggle} ontouchend={stopWiggle} role="button" tabindex="0">
                      {#if type.startsWith('image/')}
                        <img src={url} alt="media" class="disableSave" draggable="false" oncontextmenu={disableContextMenu}>
                      {:else if type.startsWith('video/')}
                        <video src={url} controls={false} loop={true} autoplay={true} muted={true} class="disableSave" draggable="false" oncontextmenu={disableContextMenu}></video>
                      {/if}
                      <button type="button" class={`delete-button select-none ${$wiggleModeEnabled ? 'flex' : 'hidden'}`} onclick={deleteFile} aria-label="Delete Uploaded Item">
                        <Trash oncontextmenu={disableContextMenu} class="w-4 h-4" />
                      </button>
                    </div>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
          <div id="fullscreenViewer" bind:this={fullscreenViewer} role="button" tabindex="0" class="fixed inset-0 bg-black bg-opacity-90 items-center justify-center select-none hidden" onclick={closeFullscreen} onkeypress={closeFullscreen}>
            <button id="closeButton" type="button" onclick={closeFullscreen} class="absolute select-none top-4 right-4 text-white text-3xl z-10">×</button>
            <div role="button" tabindex="0" onclick={(e) => {
              e.stopPropagation();
              e.preventDefault();
            }} onkeypress={(e) => {
              e.stopPropagation();
              e.preventDefault();
            }}>
              <img id="fullscreenImage" bind:this={fullscreenImage} alt="" class="max-w-full max-h-full hidden" oncontextmenu={disableContextMenu} />
              <video id="fullscreenVideo" bind:this={fullscreenVideo} class="max-w-full max-h-full hidden" controls={true} loop={true} autoplay={true} muted={false}>
                <track kind="captions">
              </video>
            </div>
          </div>
        </div>
        <button
          type="submit"
          class="w-full select-none py-3 bg-blue-500 text-white font-medium rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Submit Issue
        </button>
      </form>
    </div>
  </div>
{/if}
