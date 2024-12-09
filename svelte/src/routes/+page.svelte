<script lang="ts">
  // Svelte lifecycle functions
  import { onDestroy, onMount } from "svelte";
  // Utilities
  import { browser } from "$app/environment";
  import { getAppVersion } from "$lib/helpers/server-requests";
  import { registerServiceWorker } from "$lib/helpers/register-sw";
  // QR Scanner utilities
  import { destroyScanner } from "$lib/helpers/camera";
  // UI Components:
  import NotifyUi from "$lib/components/NotifyUi.svelte";
  import CloseReportUi from "$lib/components/CloseReportUi.svelte";
  import ReportUi from "$lib/components/ReportUi.svelte";
  import DetailsDrawer from "$lib/components/DetailsDrawer.svelte";
  import HomePage from "$lib/components/HomePage.svelte";
  import PastIssues from "$lib/components/PastIssues.svelte";
  import { Spinner } from "flowbite-svelte";

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
  <main class="container px-4 py-5 pt-2 min-h-screen bg-slate-100">
    <div class="text-center mb-4">
      <img
        src="/Fejlemingsapp_logo.png"
        alt="logo"
        width="128"
        height="auto"
        class="m-auto mt-2"
      />
    </div>
    <div
      class="fixed inset-0 flex items-center justify-center bg-white dark:bg-gray-900 z-50"
    >
      <Spinner />
    </div>
  </main>
{:else}
  <HomePage />
  <PastIssues />
  <DetailsDrawer />
  <NotifyUi />
  <CloseReportUi />
  <ReportUi />
{/if}
