<script lang="ts">
  // Icons and components
  import {
    GalleryThumbnails,
    Video,
    Upload,
    Trash,
    ArrowLeft,
    X,
    Fuel,
    BatteryCharging,
    RefreshCw,
    Droplet,
  } from "lucide-svelte";
  import { Button, Badge, Avatar, Drawer } from "flowbite-svelte";
  // Utilities
  import { disableContextMenu, formatNumber } from "$lib/helpers/basics";
  // QR Scanner utilities
  import { qrScannerStore } from "$lib/helpers/camera";
  const { qrCodeData, showPopup, detectedGSE } = qrScannerStore;
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
  import { handleFormSubmit } from "$lib/helpers/submit-report";
  import { writable, type Writable } from "svelte/store";
  import { CheckOutline } from "flowbite-svelte-icons";
  import { sineIn } from "svelte/easing";

  const operable = writable("");
  let hideGSEDetail = true;

  let transitionParamsBottom = {
    y: 320,
    duration: 200,
    easing: sineIn,
  };

  const fuelIcons = {
    diesel: Fuel,
    electric: BatteryCharging,
    hybrid: RefreshCw,
    petrol: Droplet,
  } as const;

  const defaultIcon = Fuel;

  function getResolvedIcon(fuelType: string): typeof Fuel {
    return fuelIcons[(fuelType.split(' ')[0].toLowerCase()) as keyof typeof fuelIcons] || defaultIcon;
  }

  const equipment: Equipment = {
    "Air starter unit (ASU)":
      "https://images.unsplash.com/photo-1547963802-25f153e14080?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxBaXIlMjBzdGFydGVyJTIwdW5pdHxlbnwwfHx8fDE3MzM1NzIzNjh8MA&ixlib=rb-4.0.3&q=80&w=400",
    "Airplane heater unit (AHU)":
      "https://images.unsplash.com/photo-1483375801503-374c5f660610?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxBaXJwbGFuZSUyMGhlYXRlciUyMHVuaXR8ZW58MHx8fHwxNzMzNTcyMzY4fDA&ixlib=rb-4.0.3&q=80&w=400",
    "Baggage cart (BCT)":
      "https://images.unsplash.com/photo-1508053803120-e3e60f3f9674?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxCYWdnYWdlJTIwY2FydHxlbnwwfHx8fDE3MzM1NzIzNjl8MA&ixlib=rb-4.0.3&q=80&w=400",
    "Baggage tractor (EBT)":
      "https://images.unsplash.com/photo-1534483650102-4796c5e8f822?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxCYWdnYWdlJTIwdHJhY3RvcnxlbnwwfHx8fDE3MzM1NzIzNjl8MA&ixlib=rb-4.0.3&q=80&w=400",
    "Belt loader (BLT)":
      "https://images.unsplash.com/photo-1608461864721-b8f50c91c147?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxCZWx0JTIwbG9hZGVyfGVufDB8fHx8MTczMzU3MjM2OXww&ixlib=rb-4.0.3&q=80&w=400",
    "Belt loader snake (BLS)":
      "https://images.unsplash.com/photo-1570741066052-817c6de995c8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxCZWx0JTIwbG9hZGVyJTIwc25ha2V8ZW58MHx8fHwxNzMzNTcyMzY5fDA&ixlib=rb-4.0.3&q=80&w=400",
    "Car (CAR)":
      "https://images.unsplash.com/photo-1515569067071-ec3b51335dd0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxDYXJ8ZW58MHx8fHwxNzMzNTcyMzcwfDA&ixlib=rb-4.0.3&q=80&w=400",
    "Container loader transporter (CLT)":
      "https://images.unsplash.com/photo-1624711076872-ecdbc5ade023?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxDb250YWluZXIlMjBsb2FkZXIlMjB0cmFuc3BvcnRlcnxlbnwwfHx8fDE3MzM1NzIzNzB8MA&ixlib=rb-4.0.3&q=80&w=400",
    "De-icing truck (DIT)":
      "https://images.unsplash.com/photo-1598065412434-6544dc76f81f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxEZS1pY2luZyUyMHRydWNrfGVufDB8fHx8MTczMzU3MjM3MHww&ixlib=rb-4.0.3&q=80&w=400",
    "Dolly trailer (DOT)":
      "https://images.unsplash.com/photo-1488539621750-1e0a7ebf61b8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxEb2xseSUyMHRyYWlsZXJ8ZW58MHx8fHwxNzMzNTcyMzcwfDA&ixlib=rb-4.0.3&q=80&w=400",
    "Ground power unit (GPU)":
      "https://images.unsplash.com/photo-1466629437334-b4f6603563c5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxHcm91bmQlMjBwb3dlciUyMHVuaXR8ZW58MHx8fHwxNzMzNTcyMzcxfDA&ixlib=rb-4.0.3&q=80&w=400",
    "High loader (HIL)":
      "https://images.unsplash.com/photo-1500408557204-010688b36731?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxIaWdoJTIwbG9hZGVyfGVufDB8fHx8MTczMzU3MjM3MXww&ixlib=rb-4.0.3&q=80&w=400",
    "Manual passenger stair (MPS)":
      "https://images.unsplash.com/photo-1484176141566-3674cda218f0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxNYW51YWwlMjBwYXNzZW5nZXIlMjBzdGFpcnxlbnwwfHx8fDE3MzM1NzIzNzJ8MA&ixlib=rb-4.0.3&q=80&w=400",
    "Other equipment (OTH)":
      "https://images.unsplash.com/photo-1486693326701-1ea88c6e2af3?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxPdGhlciUyMGVxdWlwbWVudHxlbnwwfHx8fDE3MzM1NzIzNzJ8MA&ixlib=rb-4.0.3&q=80&w=400",
    "Pallet transporter (TRP)":
      "https://images.unsplash.com/photo-1662749033848-746a76aca892?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxQYWxsZXQlMjB0cmFuc3BvcnRlcnxlbnwwfHx8fDE3MzM1NzIzNzJ8MA&ixlib=rb-4.0.3&q=80&w=400",
    "Push back tractor (PBT)":
      "https://images.unsplash.com/photo-1542850802-8a047a726d4e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxQdXNoJTIwYmFjayUyMHRyYWN0b3J8ZW58MHx8fHwxNzMzNTcyMzczfDA&ixlib=rb-4.0.3&q=80&w=400",
    "Self propelled passenger stair (SPS)":
      "https://images.unsplash.com/photo-1506126613408-eca07ce68773?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxTZWxmJTIwcHJvcGVsbGVkJTIwcGFzc2VuZ2VyJTIwc3RhaXJ8ZW58MHx8fHwxNzMzNTcyMzczfDA&ixlib=rb-4.0.3&q=80&w=400",
    "Toilet service unit (TSU)":
      "https://images.unsplash.com/photo-1414452110837-9dab484a417d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxUb2lsZXQlMjBzZXJ2aWNlJTIwdW5pdHxlbnwwfHx8fDE3MzM1NzIzNzN8MA&ixlib=rb-4.0.3&q=80&w=400",
    "Towbar (TOW)": "https://via.placeholder.com/150",
    "Towbar less tractor (TBL)":
      "https://images.unsplash.com/photo-1599642919995-f7ea5ee6a8c6?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxUb3diYXIlMjBsZXNzJTIwdHJhY3RvcnxlbnwwfHx8fDE3MzM1NzIzNzR8MA&ixlib=rb-4.0.3&q=80&w=400",
    "Water service unit (WSU)":
      "https://images.unsplash.com/photo-1483004406427-6acb078d1f2d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxXYXRlciUyMHNlcnZpY2UlMjB1bml0fGVufDB8fHx8MTczMzU3MjM3NHww&ixlib=rb-4.0.3&q=80&w=400",
  };

  const statusColors: Record<string, string> = {
    "0": "dark", // Scraped
    "1": "red", // Scrap
    "2": "yellow", // Usable
    "3": "indigo", // Okay
    "4": "purple", // Good condition
    "5": "green", // Very good condition
  };

  const getStatusNumber = (status: string | undefined): string => {
    const match = status?.match(/^(\d+)/);
    return match ? match[1] : "0"; // Default to "0" if no match is found
  };

  let statusNumber = getStatusNumber($detectedGSE?.status);
  let color = statusColors[statusNumber];
</script>

<Drawer
  placement="bottom"
  bind:hidden={hideGSEDetail}
  on:close={() => (hideGSEDetail = true)}
  backdrop={true}
  class="p-6 md:p-8 bg-gray-100 rounded-lg shadow-lg"
  width="w-full"
  transitionType="fly"
  transitionParams={transitionParamsBottom}
>
  <div class="flex items-center justify-between">
    <button
      type="button"
      onclick={() => (hideGSEDetail = true)}
      class="p-2 hover:bg-gray-200 rounded-md"
    >
      <ArrowLeft class="h-6 w-6 text-gray-800" />
    </button>
    <div
      class="font-medium inline-flex items-center justify-center px-2.5 py-0.5 text-xs border bg-purple-100 text-purple-800 dark:bg-gray-700 dark:text-purple-400 border-purple-400 dark:border-purple-400 rounded"
    >
      {$qrCodeData}
    </div>
  </div>

  <div class="mt-6">
    {#if $detectedGSE}
      <div class="flex items-center space-x-4">
        <Avatar
          src={equipment[$detectedGSE.gse_type]}
          rounded
          class="w-16 h-16 ring-4 ring-green-400 dark:ring-red-300"
        />
        <div class="flex flex-col">
          <span class="text-xl font-medium text-gray-800"
            >{$detectedGSE.gse_type}</span
          >
          <span class="font-semibold text-gray-700"
            >{$detectedGSE.model} - {$detectedGSE.manufacturer}</span
          >
        </div>
      </div>

      <div class="grid mt-4 grid-cols-2 lg:grid-cols-3 gap-4 text-gray-800">
        <!-- Manufacturer Card -->
        <div
          class="card p-3 rounded-lg shadow-md bg-white flex items-center gap-2"
        >
          <Avatar
            src="/images/kalmar.png"
            rounded
            class="w-8 h-8 bg-transparent ring-red-400 dark:ring-red-300"
          />
          <div>
            <p class="font-semibold">Manufacturer:</p>
            <p>{$detectedGSE.manufacturer || "Unknown"}</p>
          </div>
        </div>

        <!-- Error Card -->
        {#if $detectedGSE.error}
          <div
            class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-red-50"
          >
            <p class="font-semibold text-red-600">Error:</p>
            <p>{$detectedGSE.error}</p>
          </div>
        {/if}

        <!-- Details Card -->
        {#if $detectedGSE.details}
          <div
            class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-yellow-50"
          >
            <p class="font-semibold text-yellow-600">Details:</p>
            <p>{$detectedGSE.details}</p>
          </div>
        {/if}

        {#if !$detectedGSE.details && !$detectedGSE.error}
          <!-- Model Card -->
          <div
            class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-white"
          >
            <p class="font-semibold">Model:</p>
            <p>{$detectedGSE.model || "Unknown"}</p>
          </div>

          <!-- Location Card -->
          <div
            class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-white"
          >
            <p class="font-semibold">Location:</p>
            <p>{$detectedGSE.location || "Not specified"}</p>
          </div>

          <!-- Status Card -->
          <div
            class="card flex-col p-3 rounded-lg shadow-md bg-white flex items-center justify-between"
          >
            <p class="font-semibold">Status:</p>
            <div
              class="font-medium inline-flex items-center justify-center px-2.5 py-0.5 text-xs border bg-{color}-100 text-{color}-800 dark:bg-gray-700 dark:text-{color}-400 border-{color}-400 dark:border-{color}-400 rounded"
            >
              {$detectedGSE.status || "Unavailable"}
            </div>
          </div>

          <!-- Fuel Type Card -->
          <div
            class="card flex-col p-3 rounded-lg shadow-md bg-white flex items-center justify-between"
          >
            <p class="font-semibold">Fuel Type:</p>
            <div class="flex items-center gap-2">
              {$detectedGSE.type_of_fuel || "Unknown"}
              {#if $detectedGSE.type_of_fuel}
                {@const ResolvedIcon = getResolvedIcon(
                  $detectedGSE.type_of_fuel,
                )}
                <ResolvedIcon style="vertical-align: middle;" />
              {/if}
            </div>
          </div>

          <!-- In Use Card -->
          <div
            class="card flex-col p-3 rounded-lg shadow-md bg-white flex items-center justify-between"
          >
            <p class="font-semibold">In Use:</p>
            {#if $detectedGSE.in_use}
              <Badge color="green" rounded large class="!p-1 !font-semibold">
                <CheckOutline class="h-4 w-4" />
              </Badge>
            {:else}
              <Badge rounded large class="!p-1 !font-semibold">
                <X class="h-4 w-4 text-primary-800 dark:text-primary-400" />
              </Badge>
            {/if}
          </div>

          <!-- Last Service Date Card -->
          {#if $detectedGSE.latest_service_chassi}
            <div
              class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-white"
            >
              <p class="font-semibold">Last Service Date:</p>
              <p>{$detectedGSE.latest_service_chassi}</p>
            </div>
          {/if}

          <!-- Lift Inspection Expiry Card -->
          {#if $detectedGSE.lift_inspection_expires}
            <div
              class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-white"
            >
              <p class="font-semibold">Lift Inspection Expiry:</p>
              <p>
                {$detectedGSE.lift_inspection_expires}
              </p>
            </div>
          {/if}

          <!-- Latest Service Unit Card -->
          {#if $detectedGSE.latest_service_unit}
            <div
              class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-white"
            >
              <p class="font-semibold">Latest Service Unit:</p>
              <p>{$detectedGSE.latest_service_unit}</p>
            </div>
          {/if}

          <!-- Capacity Card -->
          {#if $detectedGSE.capacity}
            <div
              class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-white"
            >
              <p class="font-semibold">Capacity:</p>
              <p>{$detectedGSE.capacity}</p>
            </div>
          {/if}
        {/if}
      </div>
    {:else}
      <div class="flex flex-col items-center">
        <h2 class="text-base font-bold text-center">
          Could not find information for vehicle with GSE id:
        </h2>
        <div
          class="font-medium inline-flex items-center justify-center px-2.5 py-0.5 text-xs border bg-purple-100 text-purple-800 dark:bg-gray-700 dark:text-purple-400 border-purple-400 dark:border-purple-400 rounded"
        >
          {$qrCodeData}
        </div>
      </div>
    {/if}
  </div>

  <div class="mt-6 flex justify-end">
    <Button
      on:click={() => (hideGSEDetail = true)}
      class="bg-blue-500 hover:bg-blue-600 text-white rounded-full px-6 py-2"
    >
      Close
    </Button>
  </div>
</Drawer>

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
          onclick={() => (hideGSEDetail = false)}
          onkeydown={() => (hideGSEDetail = false)}
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
            Upload up to 4 files
          </p>
          <div class="flex justify-center">
            <label for="takePicture" class="file-button w-12 h-12">
              <GalleryThumbnails
                oncontextmenu={disableContextMenu}
                class="w-6 h-6"
              />
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
            <div id="gallery-container">
              <div id="gallery">
                {#each $mediaFiles as { url, type, deleteFile, handleClick }}
                  <div
                    class={`gallery-item select-none relative ${$wiggleModeEnabled ? "wiggle" : ""}`}
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
                        class="disableSave"
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
                        class="disableSave"
                        draggable="false"
                        oncontextmenu={disableContextMenu}
                      ></video>
                    {/if}
                    <button
                      type="button"
                      class={`delete-button select-none ${$wiggleModeEnabled ? "flex" : "hidden"}`}
                      onclick={deleteFile}
                      aria-label="Delete Uploaded Item"
                    >
                      <Trash
                        oncontextmenu={disableContextMenu}
                        class="w-4 h-4"
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
