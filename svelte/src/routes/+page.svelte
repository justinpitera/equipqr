<script lang="ts">
  // Svelte lifecycle functions
  import { onDestroy, onMount } from "svelte";
  // Utilities
  import { browser } from "$app/environment";
  import { getAppVersion } from "$lib/helpers/server-requests";
  import { registerServiceWorker } from "$lib/service-worker/register-sw";
  // QR Scanner utilities
  import { destroyScanner } from "$lib/helpers/camera";
  // UI Components:
  import NotifyUi from "$lib/components/NotifyUi.svelte";
  import CloseReportUi from "$lib/components/CloseReportUi.svelte";
  import ReportUi from "$lib/components/ReportUi.svelte";
  import DetailsDrawer from "$lib/components/DetailsDrawer.svelte";
  import HomePage from "$lib/components/HomePage.svelte";
  import PastIssues from "$lib/components/PastIssues.svelte";
  import Spinner from "flowbite-svelte/Spinner.svelte";
  import PrintDrawer from "$lib/components/PrintDrawer.svelte";
  import StatisticsDrawer from "$lib/components/StatisticsDrawer.svelte";
  import SelectGSEID from "$lib/components/SelectGSEID.svelte";
  import MostRecentIssue from "$lib/components/MostRecentIssue.svelte";
  import IssuesHistoryDrawer from "$lib/components/IssuesHistoryDrawer.svelte";
  import FullScreenMediaViewer from "$lib/components/FullScreenMediaViewer.svelte";
  import NewVehicle from "$lib/components/NewVehicle.svelte";

  onMount(() => {
    registerServiceWorker();
    getAppVersion();
    // Cleanup
    return () => {};
  });

  onDestroy(() => {
    if (browser) destroyScanner();
  });
</script>

{#if typeof window === "undefined"}
  <main class="px-4 py-5 pt-2 min-h-screen bg-slate-100">
    <div class="fixed inset-0 flex items-center justify-center z-50">
      <Spinner color="blue" class="w-12 h-12" />
    </div>
  </main>
{:else}
  <HomePage />
  <FullScreenMediaViewer />
  <MostRecentIssue />
  <PastIssues />
  <NewVehicle />
  <SelectGSEID />
  <PrintDrawer />
  <StatisticsDrawer />
  <IssuesHistoryDrawer />
  <DetailsDrawer />
  <NotifyUi />
  <CloseReportUi />
  <ReportUi />
{/if}
