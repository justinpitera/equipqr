<script lang="ts">
  // Icons and components
  import { Image, Video, Upload, Trash, ArrowLeft } from "lucide-svelte";
  import { Button, Badge, Avatar } from "flowbite-svelte";
  // Utilities
  import { disableContextMenu, formatNumber } from "$lib/helpers/basics";
  // QR Scanner utilities
  import { qrScannerStore } from "$lib/helpers/camera";
  const { qrCodeData, showPopup } = qrScannerStore;
  // File upload utilities
  import {
    startWiggle,
    stopWiggle,
    fileUploadStore,
    handleFileChange,
    closeFullscreen,
  } from "$lib/helpers/file-upload";
  const {
    mediaFiles,
    fullscreenViewer,
    fullscreenImage,
    fullscreenVideo,
    wiggleModeEnabled,
    pressTimer,
    isDragging,
  } = fileUploadStore;
  // Cancel report utilities
  import { cancelReportStore } from "$lib/helpers/cancel-report";
  const { closeReportHidden } = cancelReportStore;
  import { writable } from "svelte/store";
  // Details Drawer utilities
  import { detailsDrawerStore } from "$lib/helpers/details";
  import { onDestroy, onMount } from "svelte";
  import { maxFiles } from "$lib/config";
  const { hideGSEDetail } = detailsDrawerStore;

  const operable = writable("");

  function handleFormSubmit(event: Event): void {
    event.preventDefault();
    const form = event.target as HTMLFormElement;
    const formData = new FormData();
    const issue_description =
      (form.querySelector("#issue-description") as HTMLTextAreaElement)
      ?.value || "";
    const employee_name =
      (form.querySelector("#employee-name") as HTMLTextAreaElement)
        ?.value || "";
    const is_operable = $operable === "yes";
    formData.append("gse_id", $qrCodeData || 'Unknown');
    formData.append("employee_name", employee_name);
    formData.append("issue_description", issue_description);
    formData.append("is_operable", String(is_operable));

    // Append uploaded files
    $mediaFiles.forEach((file) => {
      formData.append("attachments", file.file, file.file.name);
    });

    // Send the data via fetch
    submitIssue(formData);
  }

  async function submitIssue(formData: FormData) {
    try {
      const response = await fetch("/api/gse/issues/submit", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Status Code:", response.status);
        console.log("Response Data:", data);
      } else {
        console.error("Error submitting the issue:", response.statusText);
      }
    } catch (error) {
      console.error("An error occurred:", error);
    }
  }

  const handleWindowClick = (event: MouseEvent) => {
    const target = event.target as HTMLElement;
    if (!target.closest(".ignore-js")) {
      stopWiggle();
      fileUploadStore.wiggleModeEnabled.set(false);
    }
  };

  onMount(() => {
    if (typeof window !== "undefined")
      document.addEventListener("click", handleWindowClick);
  });
  onDestroy(() => {
    if (typeof window !== "undefined")
      document.removeEventListener("click", handleWindowClick);
  });
</script>

<div
  class={`popup-backdrop fixed inset-0 bg-gray-800 bg-opacity-50 items-center justify-center ${$showPopup ? "flex" : "hidden"}`}
>
  <div class="popup-content bg-white w-full h-full">
    <div class="flex items-center justify-between p-4 md:p-6">
      <button
        type="button"
        onclick={async () => {
          $closeReportHidden = false;
        }}
        class="p-2 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 select-none"
      >
        <ArrowLeft />
      </button>
      <div class="flex flex-col items-center">
        <h2 class="text-base font-bold text-center">Issue Details for:</h2>
        <div
          onclick={() => hideGSEDetail.set(false)}
          onkeydown={() => hideGSEDetail.set(false)}
          role="button"
          tabindex="0"
          class="font-medium inline-flex items-center justify-center px-2.5 py-0.5 text-xs border bg-purple-100 text-purple-800 dark:bg-gray-700 dark:text-purple-400 border-purple-400 dark:border-purple-400 rounded"
        >
          {$qrCodeData}
        </div>
      </div>
      <Avatar
        src="/images/kalmar.png"
        rounded
        class="bg-transparent ring-red-400 dark:ring-red-300"
      />
    </div>
    <hr
      class="mt-2"
      style="filter: drop-shadow(0px 1px 3px rgba(0,0,0,0.4));"
    />
    <form
      class="space-y-4 mt-0 p-4 pt-5 md:p-6 md:pt-7"
      id="malfunction-report-form"
      onsubmit={handleFormSubmit}
    >
      <div>
        <label
          for="employee-name"
          class="block text-sm font-medium text-gray-700 mb-1"
        >
          Employee Name
        </label>
        <input
          id="employee-name"
          class="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter your 3-letters name"
          maxlength="3"
        />
        <div class="flex items-center justify-between mb-1 mt-2">
          <label
            for="issue-description"
            class="block text-sm font-medium text-gray-700"
          >
            Describe the Issue
          </label>
          <Button class="p-1 pr-3 pl-3 flex items-center">
            Past Issues
            <Badge
              rounded
              class="w-6 h-6 ms-2 p-0 font-semibold text-primary-800 bg-white dark:text-primary-800 dark:bg-white"
            >
              {formatNumber(100)}
            </Badge>
          </Button>
        </div>
        <textarea
          id="issue-description"
          rows="2"
          class="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Provide a detailed explanation of the issue"
        ></textarea>
      </div>
      <div style="margin-top: 0.5rem;">
        <label
          for="product-operable"
          class="block text-sm font-medium text-gray-700">Is it operable?</label
        >
        <div class="flex space-x-4 mt-2">
          <button
            type="button"
            class="w-1/2 text-center py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-400 select-none"
            class:active={$operable === "yes"}
            class:bg-green-500={$operable === "yes"}
            class:text-white={$operable === "yes"}
            class:text-black={$operable !== "yes"}
            onclick={() => ($operable = "yes")}
          >
            Yes
          </button>
          <button
            type="button"
            class="w-1/2 text-center py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-400 select-none"
            class:active={$operable === "no"}
            class:bg-red-500={$operable === "no"}
            class:text-white={$operable === "no"}
            class:text-black={$operable !== "no"}
            onclick={() => ($operable = "no")}
          >
            No
          </button>
        </div>
      </div>
      <div>
        <label for="attachments" class="block text-sm font-medium text-gray-700"
          >Add Photos or Videos</label
        >
        <div
          class="w-full mt-1 border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          id="custom-file-upload"
        >
          <p class="text-center text-sm text-gray-600 mb-2">
            Upload up to {maxFiles} files
          </p>
          <div class="flex justify-center">
            <label for="takePicture" class="file-button w-12 h-12">
              <Image oncontextmenu={disableContextMenu} class="w-6 h-6" />
            </label>
            <input
              id="takePicture"
              type="file"
              accept="image/*"
              capture="environment"
              multiple
              class="file-input"
              onchange={handleFileChange}
            />
            <label for="captureVideo" class="file-button ml-4 w-12 h-12">
              <Video oncontextmenu={disableContextMenu} class="w-6 h-6" />
            </label>
            <input
              id="captureVideo"
              type="file"
              accept="video/*"
              capture="environment"
              multiple
              class="file-input"
              onchange={handleFileChange}
            />
            <label for="selectMediaFiles" class="file-button ml-4 w-12 h-12">
              <Upload oncontextmenu={disableContextMenu} class="w-6 h-6" />
            </label>
            <input
              id="selectMediaFiles"
              type="file"
              accept="image/*,video/*"
              multiple
              class="file-input"
              onchange={handleFileChange}
            />
          </div>
          {#if $mediaFiles.length > 0}
            <hr class="my-4" />
            <div id="gallery-container" class="ignore-js">
              <div id="gallery" class="ignore-js">
                {#each $mediaFiles as { url, type, deleteFile, handleClick }}
                  <div
                    class={`gallery-item ignore-js select-none relative ${$wiggleModeEnabled ? "wiggle" : ""}`}
                    onclick={handleClick}
                    onkeypress={handleClick}
                    onmousedown={startWiggle}
                    onmouseup={stopWiggle}
                    onmouseleave={() => {
                      clearTimeout($pressTimer);
                      isDragging.set(false);
                    }}
                    ontouchstart={startWiggle}
                    ontouchend={stopWiggle}
                    role="button"
                    tabindex="0"
                  >
                    {#if type.startsWith("image/")}
                      <img
                        src={url}
                        alt="media"
                        class="disableSave ignore-js"
                        draggable="false"
                        oncontextmenu={disableContextMenu}
                      />
                    {:else if type.startsWith("video/")}
                      <video
                        src={url}
                        controls={false}
                        loop={true}
                        autoplay={true}
                        muted={true}
                        class="disableSave ignore-js"
                        draggable="false"
                        oncontextmenu={disableContextMenu}
                      ></video>
                    {/if}
                    <button
                      type="button"
                      class={`delete-button ignore-js select-none ${$wiggleModeEnabled ? "flex" : "hidden"}`}
                      onclick={deleteFile}
                      aria-label="Delete Uploaded Item"
                    >
                      <Trash
                        oncontextmenu={disableContextMenu}
                        class="w-4 h-4 ignore-js"
                      />
                    </button>
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        </div>
        <div
          id="fullscreenViewer"
          bind:this={$fullscreenViewer}
          role="button"
          tabindex="0"
          class="fixed inset-0 bg-black bg-opacity-90 items-center justify-center select-none hidden"
          onclick={closeFullscreen}
          onkeypress={closeFullscreen}
        >
          <button
            id="closeButton"
            type="button"
            onclick={closeFullscreen}
            class="absolute select-none top-4 right-4 text-white text-3xl z-10"
            >×</button
          >
          <div
            role="button"
            tabindex="0"
            onclick={(e) => {
              e.stopPropagation();
              e.preventDefault();
            }}
            onkeypress={(e) => {
              e.stopPropagation();
              e.preventDefault();
            }}
          >
            <img
              id="fullscreenImage"
              bind:this={$fullscreenImage}
              alt=""
              class="max-w-full max-h-full hidden"
              oncontextmenu={disableContextMenu}
            />
            <video
              id="fullscreenVideo"
              bind:this={$fullscreenVideo}
              class="max-w-full max-h-full hidden"
              controls={true}
              loop={true}
              autoplay={true}
              muted={false}
            >
              <track kind="captions" />
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
