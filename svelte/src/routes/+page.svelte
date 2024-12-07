<script lang="ts">
  // Svelte lifecycle functions
  import { onDestroy, onMount } from "svelte";
  // Utilities
  import { browser } from "$app/environment";
  import { getAppVersion } from "$lib/helpers/server-requests";
  import { registerServiceWorker } from "$lib/helpers/register-sw";
  // Configuration
  import { DEBUG_MODE } from "$lib/config";
  // QR Scanner utilities
  import {
    destroyScanner,
    loadQRScanner,
  } from "$lib/helpers/camera";
  // UI Components:
  import NotifyUi from "$lib/components/NotifyUi.svelte";
  import CloseReportUi from "$lib/components/CloseReportUi.svelte";
  import QRScannerUi from "$lib/components/QRScannerUi.svelte";
  import ReportUi from "$lib/components/ReportUi.svelte";
  import DetailsDrawer from "$lib/components/DetailsDrawer.svelte";

  onMount(() => {
    // loadQRScanner(DEBUG_MODE ? "AHU 00001" : undefined); // Debug by adding an ID here
    registerServiceWorker();
    getAppVersion();
    // Cleanup
    return () => {};
  });

  onDestroy(() => {
    if (browser) destroyScanner();
  });
</script>

<DetailsDrawer />
<NotifyUi />
<QRScannerUi />
<CloseReportUi />
<ReportUi />
