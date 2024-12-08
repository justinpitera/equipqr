<script lang="ts">
    import { Drawer, Button, CloseButton } from "flowbite-svelte";
    import { InfoCircleSolid, ArrowRightOutline } from "flowbite-svelte-icons";
    import { disableContextMenu } from "$lib/helpers/basics";
    import {
      loadQRScanner,
      qrScannerStore,
    } from "$lib/helpers/camera";
    const { qrCodeData, showPopup } = qrScannerStore;
    import {
      cancelReportStore,
      transitionParamsTop,
    } from "$lib/helpers/cancel-report";
    import { DEBUG_MODE } from "$lib/config";
    import { langChecker, translations } from "$lib/locales";
    const { closeReportHidden } = cancelReportStore;
    import { homePageStore } from "$lib/helpers/homepage";
    const { selectedLanguage } = homePageStore;
    
    function t(key: string): string {
        const langTranslations = translations[$selectedLanguage];
        langChecker(key);
        return langTranslations[key] || key;
    }

</script>

<Drawer
  id="close-report-ui"
  placement="top"
  width="w-full"
  transitionType="fly"
  transitionParams={transitionParamsTop}
  bind:hidden={$closeReportHidden}
>
  <div class="flex items-center">
    <h5
      id="drawer-label"
      class="inline-flex items-center mb-4 text-base font-semibold text-gray-500 dark:text-gray-400"
    >
      <InfoCircleSolid
        oncontextmenu={disableContextMenu}
        class="w-5 h-5 me-2.5"
      />Cancel Report?
    </h5>
    <CloseButton
      on:click={() => ($closeReportHidden = true)}
      class="mb-4 dark:text-white"
    />
  </div>
  <p class="max-w-lg mb-6 text-sm text-gray-500 dark:text-gray-400">
    Are you sure you want to cancel the report for:<br />{$qrCodeData}?
  </p>
  <Button
    type="button"
    color="light"
    on:click={() => ($closeReportHidden = true)}
    class="p-2 pr-3 pl-3 select-none">No, Let me finish it</Button
  >
  <Button
    type="button"
    on:click={() => {
      $closeReportHidden = true;
      showPopup.set(false);
      document.getElementById("qrScanner")?.classList.remove("hidden");
      if (DEBUG_MODE) {
        homePageStore.startQRScanner.set(false);
      } else {
        loadQRScanner(DEBUG_MODE ? "AHU 00001" : undefined);
      }
    }}
    href="/"
    class="px-4 p-2 pr-3 pl-3 select-none"
    >Yes, Cancel it <ArrowRightOutline
      oncontextmenu={disableContextMenu}
      class="w-5 h-5 ms-2"
    /></Button
  >
</Drawer>
