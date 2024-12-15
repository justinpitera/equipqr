<script lang="ts">
  import Drawer from "flowbite-svelte/Drawer.svelte";
  import Button from "flowbite-svelte/Button.svelte";
  import CloseButton from "flowbite-svelte/CloseButton.svelte";
  import InfoCircleSolid from "flowbite-svelte-icons/InfoCircleSolid.svelte";
  import ArrowRightOutline from "flowbite-svelte-icons/ArrowRightOutline.svelte";
  import { disableContextMenu } from "$lib/helpers/basics";
  import { loadQRScanner, qrScannerStore } from "$lib/helpers/camera";
  const { qrCodeData, showPopup } = qrScannerStore;
  import {
    cancelReportStore,
    transitionParamsTop,
  } from "$lib/helpers/cancel-report";
  import { DEBUG_MODE } from "$lib/config";
  import { langChecker, translations } from "$lib/locales";
  const { closeReportHidden } = cancelReportStore;
  import { homePageStore } from "$lib/helpers/homepage";
  import { onDestroy } from "svelte";
  const { selectedLanguage, darkModeEnabled, startQRScanner } = homePageStore;

  function t(key: string): string {
    const langTranslations = translations[$selectedLanguage];
    langChecker(key);
    return langTranslations?.[key] || key;
  }

  onDestroy(() => {
    closeReportHidden.set(true);
  });
</script>

<Drawer
  id="close-report-ui"
  placement="top"
  width="w-full"
  transitionType="fly"
  activateClickOutside={false}
  transitionParams={transitionParamsTop}
  bind:hidden={$closeReportHidden}
  class="drawer-box max-w-[600px] m-auto"
>
  <div class="flex items-center">
    <h5
      id="drawer-label"
      class="inline-flex items-center mb-4 text-base font-semibold text-gray-500 dark:text-gray-400"
    >
      <InfoCircleSolid
        oncontextmenu={disableContextMenu}
        class="w-5 h-5 me-2.5"
      />{t("Cancel Report?")}
    </h5>
    <CloseButton
      on:click={() => ($closeReportHidden = true)}
      class="mb-4 dark:text-white"
    />
  </div>
  <p class="max-w-lg mb-6 text-sm text-gray-500 dark:text-gray-400">
    {t("Are you sure you want to cancel the report for:")}<br />{$qrCodeData}?
  </p>
  <Button
    type="button"
    color="light"
    on:click={() => ($closeReportHidden = true)}
    class="p-2 pr-3 pl-3 select-none">{t("No, Let me finish it")}</Button
  >
  <Button
    type="button"
    on:click={() => {
      $closeReportHidden = true;
      showPopup.set(false);
      document.getElementById("qrScanner")?.classList.remove("hidden");
      if (DEBUG_MODE) {
        homePageStore.startQRScanner.set(false);
      } else if ($startQRScanner) {
        loadQRScanner(DEBUG_MODE ? "AHU 00001" : undefined);
      }
    }}
    href="/"
    class="px-4 p-2 pr-3 pl-3 select-none bg-red-500 hover:bg-red-600"
    style="filter: invert({$darkModeEnabled ? '1' : '0'});"
    >{t("Yes, Cancel it")}
    <ArrowRightOutline
      oncontextmenu={disableContextMenu}
      class="w-5 h-5 ms-2"
    /></Button
  >
</Drawer>
