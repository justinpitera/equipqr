<script lang="ts">
  import Drawer from "flowbite-svelte/Drawer.svelte";
  import Button from "flowbite-svelte/Button.svelte";
  import CloseButton from "flowbite-svelte/CloseButton.svelte";
  import InfoCircleSolid from "flowbite-svelte-icons/InfoCircleSolid.svelte";
  import ArrowRightOutline from "flowbite-svelte-icons/ArrowRightOutline.svelte";
  import { disableContextMenu } from "$lib/helpers/basics";
  import { t } from "$lib/locales";
  import { onDestroy, onMount } from "svelte";
  import { getAllGSEs } from "$lib/helpers/server-requests";
  import { flyTransitionParamsTop } from "$lib/helpers/fly";
  import store from "$lib/store";
  const { darkModeEnabled, selectGSEIDDrawerHidden, gseAction } = store;

  let selectedGSEID: string = $state("");
  let gseIDS: string[] = $state([]);

  async function populateGSEIDs() {
    const response = await getAllGSEs();
    if (response?.gse_id) gseIDS = response.gse_id;
  }

  onMount(() => {
    populateGSEIDs();
  });
  onDestroy(() => {
    selectGSEIDDrawerHidden.set(true);
  });
</script>

<Drawer
  id="select-gse-id-drawer"
  placement="top"
  width="w-full"
  transitionType="fly"
  activateClickOutside={false}
  transitionParams={flyTransitionParamsTop}
  bind:hidden={$selectGSEIDDrawerHidden}
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
      />{t("Select GSE ID")}
    </h5>
    <CloseButton
      on:click={() => ($selectGSEIDDrawerHidden = true)}
      class="mb-4 dark:text-white"
    />
  </div>
  <div class="mb-2">
    <label for="selected-gse-id" class="block text-sm font-medium"
      >{t("Enter the GSE ID")}</label
    >
    {#if gseIDS.length > 0}
      <input
        type="text"
        id="selected-gse-id"
        bind:value={selectedGSEID}
        class="w-full border border-gray-300 rounded-lg p-2"
        placeholder={t("Enter the GSE ID")}
        list="selected-gse-id-options"
      />
      <datalist id="selected-gse-id-options">
        {#each gseIDS as item}
          <option value={item}>{item}</option>
        {/each}
      </datalist>
    {/if}
  </div>
  <div class="flex justify-between">
    <Button
      type="button"
      color="light"
      on:click={() => ($selectGSEIDDrawerHidden = true)}
      class="p-2 pr-3 pl-3 select-none">{t("Cancel")}</Button
    >
    <Button
      type="button"
      on:click={() => {
        $selectGSEIDDrawerHidden = true;
        $gseAction?.(selectedGSEID);
      }}
      href="/"
      class="px-4 p-2 pr-3 pl-3 select-none bg-green-500 hover:bg-green-600"
      >{t("Find")}
      <ArrowRightOutline
        oncontextmenu={disableContextMenu}
        class="w-5 h-5 ms-2"
      /></Button
    >
  </div>
</Drawer>
