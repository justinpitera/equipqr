<script lang="ts">
  // Svelte lifecycle functions
  import { onDestroy, onMount } from "svelte";
  // Utilities
  import { browser } from "$app/environment";
  import { getAppVersion, getTenantSlug } from "$lib/helpers/server-requests";
  import { registerServiceWorker } from "$lib/service-worker/register-sw";
  // QR Scanner utilities
  import { destroyScanner } from "$lib/helpers/camera";
  // UI Components:
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
  import AdminDrawer from "$lib/components/AdminDrawer.svelte";
  import SignupDrawer from "$lib/components/SignupDrawer.svelte";
  import TenantManagementDrawer from "$lib/components/TenantManagementDrawer.svelte";
  import TenantSelector from "$lib/components/TenantSelector.svelte";

  // True when the user is on the root domain with no tenant subdomain.
  const hasTenant = typeof window !== "undefined" ? !!getTenantSlug() : true;

  onMount(() => {
    if (hasTenant) {
      registerServiceWorker();
      getAppVersion();
    }
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
{:else if !hasTenant}
  <TenantSelector />
{:else}
  <HomePage />
  <FullScreenMediaViewer />
  <MostRecentIssue />
  <PastIssues />
  <NewVehicle />
  <AdminDrawer />
  <SignupDrawer />
  <TenantManagementDrawer />
  <SelectGSEID />
  <PrintDrawer />
  <StatisticsDrawer />
  <IssuesHistoryDrawer />
  <DetailsDrawer />
  <CloseReportUi />
  <ReportUi />
{/if}
