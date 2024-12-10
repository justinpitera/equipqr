<script lang="ts">
  import { onDestroy, onMount, tick } from "svelte";
  // Icons and components
  import {
    Image,
    Video,
    Upload,
    Trash,
    ArrowLeft,
    Plane,
    PlaneLanding,
    PlaneTakeoff,
    Boxes,
    Globe,
  } from "lucide-svelte";
  import {
    Button,
    Badge,
    Avatar,
    Dropdown,
    DropdownItem,
    Select,
    Spinner,
    Tooltip,
  } from "flowbite-svelte";
  // Utilities
  import { disableContextMenu, formatNumber } from "$lib/helpers/basics";
  // QR Scanner utilities
  import { qrScannerStore } from "$lib/helpers/camera";
  const { qrCodeData, showPopup, showLoader, detectedGSE } = qrScannerStore;
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
  // Details Drawer utilities
  import { detailsDrawerStore } from "$lib/helpers/details";
  import { BACKEND_URL, DEBUG_MODE, maxFiles } from "$lib/config";
  import { submitIssue } from "$lib/helpers/server-requests";
  import { ChevronDownOutline } from "flowbite-svelte-icons";
  import { notify } from "$lib/helpers/notify";
  import { homePageStore } from "$lib/helpers/homepage";
  import {
    build_gate_options,
    reportUIStore,
  } from "$lib/helpers/report-ui-store";
  import { langChecker, translations } from "$lib/locales";
  const {
    selectedLanguage,
    isPastIssuesForSpecificIDHidden,
    darkModeEnabled,
    hideTip,
  } = homePageStore;

  function t(key: string): string {
    const langTranslations = translations[$selectedLanguage];
    langChecker(key);
    return langTranslations?.[key] || key;
  }

  const { hideGSEDetail } = detailsDrawerStore;
  const {
    employee_name,
    issue_description,
    operable,
    selected_gate_type,
    selected_gate_name,
    gates,
    is_gate_type_dropdown_open,
  } = reportUIStore;

  async function handleReportFormSubmit(event: Event): Promise<void> {
    event.preventDefault();
    const formData = new FormData();
    const isOperable = $operable === "yes";
    // Validate required fields
    const errors: string[] = [];
    if (!$employee_name.trim()) {
      errors.push("Employee name is required.");
    } else if ($employee_name.trim().length !== 3) {
      errors.push("Employee name must be 3 letters long.");
    }
    if (!$issue_description.trim()) {
      errors.push("Issue description is required.");
    } else if ($employee_name.trim().length < 2) {
      errors.push("Issue description is too short.");
    }
    if ($operable === "") {
      errors.push("Operable status must be selected.");
    } else if ($operable === "no" && $selected_gate_type === "") {
      errors.push("Gate type and name are required if not operable.");
    } else if ($operable === "no" && $selected_gate_name === "") {
      errors.push("Gate name is required if not operable.");
    }
    if ($mediaFiles.length === 0)
      errors.push("At least one photo or video must be uploaded.");
    // Show errors if any
    if (errors.length > 0) {
      let error_count = 0;
      for (const error of errors) {
        error_count += 1;
        notify("Error", error, "error");
        if (error_count !== errors.length)
          await new Promise((resolve) => setTimeout(resolve, 800));
      }
      return;
    }
    formData.append("gse_id", $qrCodeData || "Unknown");
    formData.append("employee_name", $employee_name);
    formData.append("issue_description", $issue_description);
    formData.append("is_operable", String(isOperable));
    if (!isOperable) {
      formData.append("gate_type", String($selected_gate_type));
      formData.append("gate_name", String($selected_gate_name));
    }
    // Append uploaded files
    $mediaFiles.forEach((file) => {
      formData.append("attachments", file.file, file.file.name);
    });
    // Send the data via fetch
    const response = await submitIssue(
      formData,
      () => {
        showLoader.set(true);
      },
      () => {
        showLoader.set(false);
      },
    );
    if (response) {
      notify("Success", "success", "success");
    } else {
      notify("Success", "success", "error");
    }
  }

  const handleWindowClick = (event: MouseEvent) => {
    const target = event.target as HTMLElement;
    if (!target.closest(".ignore-js")) {
      stopWiggle();
      fileUploadStore.wiggleModeEnabled.set(false);
    }
  };

  let interval: NodeJS.Timeout;
  let timeAgo = "";
  function calculateTimeAgo(reportedAt: string): string {
    const now = new Date();
    const reportedDate = new Date(reportedAt);
    const diff = Math.max(0, now.getTime() - reportedDate.getTime());
    const years = Math.floor(diff / (1000 * 60 * 60 * 24 * 365));
    const months = Math.floor(
      (diff % (1000 * 60 * 60 * 24 * 365)) / (1000 * 60 * 60 * 24 * 30),
    );
    const days = Math.floor(
      (diff % (1000 * 60 * 60 * 24 * 30)) / (1000 * 60 * 60 * 24),
    );
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    const parts = [
      years > 0 ? `${years} year${years > 1 ? "s" : ""}` : "",
      months > 0 ? `${months} month${months > 1 ? "s" : ""}` : "",
      days > 0 ? `${days} day${days > 1 ? "s" : ""}` : "",
      hours > 0 ? `${hours} hour${hours > 1 ? "s" : ""}` : "",
      minutes > 0 ? `${minutes} minute${minutes > 1 ? "s" : ""}` : "",
      seconds > 0 ? `${seconds} second${seconds > 1 ? "s" : ""}` : "",
    ];
    const timeAgoOutput = parts.filter(Boolean).join(", ");
    return timeAgoOutput ? `${timeAgoOutput} ago` : "just now";
  }

  $: if ($detectedGSE?.most_recent_issue?.reported_at) {
    timeAgo = calculateTimeAgo($detectedGSE.most_recent_issue.reported_at);
  }

  onMount(() => {
    const tip_times = localStorage.getItem("hideTipNextTime");
    let final_tip_times = 0;
    if (tip_times) {
      const parsedTipTimes = Number.parseInt(tip_times);
      if (parsedTipTimes) final_tip_times = parsedTipTimes;
    }
    if (final_tip_times >= 3) {
      const tooltip1 = document.getElementById("tip-tooltip");
      if (tooltip1) tooltip1.remove();
      hideTip.set(true);
    }
    if (typeof window !== "undefined")
      document.addEventListener("click", handleWindowClick);
    interval = setInterval(async () => {
      if ($detectedGSE?.most_recent_issue?.reported_at) {
        timeAgo = calculateTimeAgo($detectedGSE.most_recent_issue.reported_at);
        await tick();
      } else {
        clearInterval(interval);
      }
    }, 1000);

    return () => clearInterval(interval);
  });
  onDestroy(() => {
    if (typeof window !== "undefined")
      document.removeEventListener("click", handleWindowClick);
  });
</script>

<div
  class="popup-backdrop fixed inset-0 bg-gray-800 bg-opacity-50 items-center justify-center {$showPopup
    ? 'flex'
    : 'hidden'}"
>
  <div class="popup-content bg-white w-full h-full">
    <div class="flex items-center justify-between p-4 md:p-6">
      <button
        type="button"
        onclick={() => {
          if ($showLoader) return;
          $closeReportHidden = false;
        }}
        class="p-2 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 select-none {$showLoader
          ? 'opacity-0'
          : ''}"
      >
        <ArrowLeft />
      </button>
      <div
        class="flex flex-col items-center"
        onclick={() => {
          hideGSEDetail.set(false);
          const tooltip1 = document.getElementById("tip-tooltip");
          if (tooltip1) {
            tooltip1.remove();
            const tip_times = localStorage.getItem("hideTipNextTime");
            let final_tip_times = 0;
            if (tip_times) {
              const parsedTipTimes = Number.parseInt(tip_times);
              if (parsedTipTimes) final_tip_times = parsedTipTimes;
            }
            if (final_tip_times <= 3) {
              final_tip_times += 1;
              localStorage.setItem(
                "hideTipNextTime",
                final_tip_times.toString(),
              );
            }
          }
        }}
        onkeydown={() => {
          hideGSEDetail.set(false);
          const tooltip1 = document.getElementById("tip-tooltip");
          if (tooltip1) tooltip1.remove();
        }}
        role="button"
        tabindex="0"
        id="header-label"
      >
        <h2 class="text-base font-bold text-center">
          {t("Issue Details for:")}
        </h2>
        <div class="flex gap-2">
          <div
            class="font-medium inline-flex items-center justify-center px-2.5 py-0.5 text-xs border bg-purple-100 text-purple-800 dark:bg-gray-700 dark:text-purple-400 border-purple-400 dark:border-purple-400 rounded"
            style="filter: invert({$darkModeEnabled ? '1' : '0'});"
          >
            {$qrCodeData}
          </div>
          {#if $detectedGSE && $detectedGSE.old_gse_id}
            <div
              class="font-medium inline-flex items-center justify-center px-2.5 py-0.5 text-xs border bg-red-100 text-red-800 dark:bg-gray-700 dark:text-red-400 border-red-400 dark:border-red-400 rounded"
              style="filter: invert({$darkModeEnabled ? '1' : '0'});"
            >
              {$detectedGSE.old_gse_id}
            </div>
          {/if}
        </div>
      </div>
      {#if !$hideTip}
        <Tooltip
          id="tip-tooltip"
          class="z-20 max-w-[300px]"
          type="dark"
          triggeredBy="#header-label"
          placement="bottom"
          open={true}
          >{t(
            "Tip: Click here to view more information about the scanned unit",
          )}</Tooltip
        >
      {/if}
      <Avatar
        id="manu-logo"
        src="/images/kalmar.png"
        rounded
        class="bg-transparent ring-red-400 dark:ring-red-300"
        style="filter: invert({$darkModeEnabled ? '1' : '0'});"
      />
      <Tooltip
        class="z-20"
        type="dark"
        triggeredBy="#manu-logo"
        placement="left"
        trigger="click">Kalmar</Tooltip
      >
    </div>
    <hr
      class="mt-2"
      style="filter: drop-shadow(0px 1px 3px rgba(0,0,0,0.4));"
    />
    {#if $showLoader}
      <div
        class="report-form-bg flex justify-center space-y-4 p-4 pt-5 md:p-6 md:pt-7"
      >
        <Spinner color="blue" class="w-14 h-14 mt-[calc(50vh-78px-29px-4px)]" />
      </div>
    {/if}
    <form
      class="report-form-bg space-y-4 mt-0 p-4 pt-5 md:p-6 md:pt-7 {$showLoader
        ? 'hidden'
        : ''}"
      id="malfunction-report-form"
      onsubmit={handleReportFormSubmit}
    >
      <!-- Most recent issues: -->
      <div class="mt-6 p-4 bg-gray-100 rounded-lg shadow-md dark:bg-gray-800">
        <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100">
          {t("Most Recent Issue")}
        </h3>
        {#if $detectedGSE && $detectedGSE.most_recent_issue}
          <div class="mt-4 space-y-2">
            {#if DEBUG_MODE}
              <p class="text-sm text-gray-700 dark:text-gray-300">
                <strong>{t("Issue ID:")}</strong>
                {$detectedGSE.most_recent_issue.id}
              </p>
            {/if}
            <p class="text-sm text-gray-700 dark:text-gray-300">
              <strong>{t("Description:")}</strong>
              {$detectedGSE.most_recent_issue.issue_description}
            </p>
            <p class="text-sm text-gray-700 dark:text-gray-300">
              <strong>{t("Reported At:")}</strong>
              {new Date(
                $detectedGSE.most_recent_issue.reported_at,
              ).toLocaleString()}
              <span>({timeAgo})</span>
            </p>
            {#if $detectedGSE.most_recent_issue.attachments}
              <hr class="my-4" />
              <div class="mt-2">
                <strong class="text-sm text-gray-700 dark:text-gray-300"
                  >{t("Attachments:")}</strong
                >
                {#each $detectedGSE.most_recent_issue.attachments.split(", ") as attachment, index}
                  <a
                    href={`${BACKEND_URL}/api/media/attachment?id=${attachment}`}
                    target="_blank"
                    class="text-blue-500 hover:underline"
                  >
                    {t("View Attachment")}
                    {index + 1}
                  </a>
                  {#if index < $detectedGSE.most_recent_issue.attachments.length - 1}
                    ,
                  {/if}
                {/each}
                <div
                  id="gallery-container"
                  class="ignore-js"
                  style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                >
                  <div id="gallery" class="ignore-js">
                    {#each $detectedGSE.most_recent_issue.attachments.split(", ") as attachment, index}
                      <div
                        role="button"
                        tabindex="0"
                        class="gallery-item ignore-js select-none relative"
                      >
                        <img
                          src={`${BACKEND_URL}/api/media/attachment?id=${attachment}`}
                          alt="media"
                          class="disableSave ignore-js"
                          draggable="false"
                          oncontextmenu={disableContextMenu}
                        />
                      </div>
                    {/each}
                    {#each $detectedGSE.most_recent_issue.attachments.split(", ") as attachment, index}
                      <div
                        role="button"
                        tabindex="0"
                        class="gallery-item ignore-js select-none relative"
                      >
                        <img
                          src={`${BACKEND_URL}/api/media/attachment?id=${attachment}`}
                          alt="media"
                          class="disableSave ignore-js"
                          draggable="false"
                          oncontextmenu={disableContextMenu}
                        />
                      </div>
                    {/each}
                    {#each $detectedGSE.most_recent_issue.attachments.split(", ") as attachment, index}
                      <div
                        role="button"
                        tabindex="0"
                        class="gallery-item ignore-js select-none relative"
                      >
                        <img
                          src={`${BACKEND_URL}/api/media/attachment?id=${attachment}`}
                          alt="media"
                          class="disableSave ignore-js"
                          draggable="false"
                          oncontextmenu={disableContextMenu}
                        />
                      </div>
                    {/each}
                  </div>
                </div>
              </div>
            {/if}
          </div>
        {:else}
          <p class="mt-4 text-sm text-gray-500 dark:text-gray-400">
            {t("No recent issues found for this GSE.")}
          </p>
        {/if}
      </div>
      <!-- Employee Name: -->
      <label
        for="employee-name"
        class="block text-sm font-medium text-gray-700 mb-1"
      >
        {t("Employee Name")}
      </label>
      <input
        bind:value={$employee_name}
        id="employee-name"
        class="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder={t("Enter your 3-letters name")}
        maxlength="3"
        required
      />
      <!-- Describe the issue: -->
      <div class="flex items-center justify-between mb-1 mt-2">
        <label
          for="issue-description"
          class="block text-sm font-medium text-gray-700"
        >
          {t("Describe the Issue")}
        </label>
        <Button
          class="p-1 pr-3 pl-3 flex items-center"
          onclick={() => {
            isPastIssuesForSpecificIDHidden.set(false);
          }}
          style="filter: invert({$darkModeEnabled ? '1' : '0'});"
        >
          {t("Past Issues")}
          <Badge
            rounded
            class="w-6 h-6 ms-2 p-0 font-semibold text-primary-800 bg-white dark:text-primary-800 dark:bg-white"
          >
            {$detectedGSE?.issue_count
              ? formatNumber(parseInt($detectedGSE.issue_count))
              : "0"}
          </Badge>
        </Button>
      </div>
      <textarea
        bind:value={$issue_description}
        id="issue-description"
        rows="2"
        class="w-full border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder={t("Provide a detailed explanation of the issue")}
      ></textarea>
      <!-- Operable: -->
      <div style="margin-top: 0.5rem;">
        <label
          for="product-operable"
          class="block text-sm font-medium text-gray-700"
          >{t("Is it operable?")}</label
        >
        <div class="flex space-x-4 mt-2">
          <button
            type="button"
            class="w-1/2 text-center py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-400 select-none"
            class:active={$operable === "yes"}
            class:bg-green-500={$operable === "yes"}
            class:text-white={!$darkModeEnabled && $operable === "yes"}
            class:text-black={$operable !== "yes"}
            onclick={() => ($operable = "yes")}
            style="filter: invert({$darkModeEnabled ? '1' : '0'});"
          >
            <span style="filter: invert({$darkModeEnabled ? '1' : '0'});"
              >{t("Yes")}</span
            >
          </button>
          <button
            type="button"
            class="w-1/2 text-center py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-red-400 select-none"
            class:active={$operable === "no"}
            class:bg-red-500={$operable === "no"}
            class:text-white={!$darkModeEnabled && $operable === "no"}
            class:text-black={$operable !== "no"}
            onclick={() => ($operable = "no")}
            style="filter: invert({$darkModeEnabled ? '1' : '0'});"
          >
            <span style="filter: invert({$darkModeEnabled ? '1' : '0'});"
              >{t("No")}</span
            >
          </button>
        </div>
      </div>
      <!-- Select Gate: -->
      <div class="flex {$operable === 'no' ? '' : 'hidden'}">
        <button
          id="gates-button"
          class="flex-shrink-0 z-10 inline-flex items-center py-2.5 px-4 text-sm font-medium text-center text-gray-500 bg-gray-100 border border-gray-300 rounded-s-lg hover:bg-gray-200 focus:ring-4 focus:outline-none focus:ring-gray-100 dark:bg-gray-700 dark:hover:bg-gray-600 dark:focus:ring-gray-700 dark:text-white dark:border-gray-600"
          type="button"
        >
          {#if $selected_gate_type === ""}
            <Plane class="mr-1" />
            {t("Gate Type")}
          {/if}
          {#if $selected_gate_type === "cargo"}
            <Boxes class="mr-1" />
            Cargo
          {/if}
          {#if $selected_gate_type === "none"}
            <PlaneLanding class="mr-1" />
            None
          {/if}
          {#if $selected_gate_type === "airline"}
            <PlaneTakeoff class="mr-1" />
            Airline
          {/if}
          {#if $selected_gate_type === "ga"}
            <Globe class="mr-1" />
            GA
          {/if}
          <ChevronDownOutline class="w-6 h-6 ms-2" />
        </button>
        <Dropdown
          triggeredBy="#gates-button"
          bind:open={$is_gate_type_dropdown_open}
        >
          <DropdownItem
            class="flex items-center"
            onclick={() => {
              build_gate_options("cargo");
            }}
          >
            <Boxes class="mr-1" />
            Cargo
          </DropdownItem>
          <DropdownItem
            class="flex items-center"
            onclick={() => {
              build_gate_options("none");
            }}
          >
            <PlaneLanding class="mr-1" />
            None
          </DropdownItem>
          <DropdownItem
            class="flex items-center"
            onclick={() => {
              build_gate_options("airline");
            }}
          >
            <PlaneTakeoff class="mr-1" />
            Airline
          </DropdownItem>
          <DropdownItem
            class="flex items-center"
            onclick={() => {
              build_gate_options("ga");
            }}
          >
            <Globe class="mr-1" />
            GA
          </DropdownItem>
        </Dropdown>
        <Select
          bind:value={$selected_gate_name}
          id="select-gate-name"
          items={$gates}
          placeholder={t(
            `Choose a Gate ${$selected_gate_type === "" ? "Type" : "Name"}`,
          )}
          class="!rounded-s-none"
        />
      </div>
      <!-- Upload Media: -->
      <div>
        <label for="attachments" class="block text-sm font-medium text-gray-700"
          >{t("Add Photos or Videos")}</label
        >
        <div
          class="w-full mt-1 border border-gray-300 rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
          id="custom-file-upload"
        >
          <p class="text-center text-sm text-gray-600 mb-2">
            {t(`Upload up to ${maxFiles} files`)}
          </p>
          <div class="flex justify-center">
            <label
              for="takePicture"
              class="file-button w-12 h-12"
              style="filter: invert({$darkModeEnabled ? '1' : '0'});"
            >
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
            <label
              for="captureVideo"
              class="file-button ml-4 w-12 h-12"
              style="filter: invert({$darkModeEnabled ? '1' : '0'});"
            >
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
            <label
              for="selectMediaFiles"
              class="file-button ml-4 w-12 h-12"
              style="filter: invert({$darkModeEnabled ? '1' : '0'});"
            >
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
            <div
              id="gallery-container"
              class="ignore-js"
              style="filter: invert({$darkModeEnabled ? '1' : '0'});"
            >
              <div id="gallery" class="ignore-js">
                {#each $mediaFiles as { url, type, deleteFile, handleClick }}
                  <div
                    class="gallery-item ignore-js select-none relative {$wiggleModeEnabled
                      ? 'wiggle'
                      : ''}"
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
                      class="delete-button ignore-js select-none {$wiggleModeEnabled
                        ? 'flex'
                        : 'hidden'}"
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
        style="filter: invert({$darkModeEnabled ? '1' : '0'});"
      >
        {t("Submit Issue")}
      </button>
    </form>
  </div>
</div>
