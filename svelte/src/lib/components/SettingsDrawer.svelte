<script>
    import { ArrowLeft } from "lucide-svelte";
    import { homePageStore } from "$lib/helpers/homepage";
    import { Button, Drawer } from "flowbite-svelte";
    import { sineIn } from "svelte/easing";
    const { isSettingsHidden } = homePageStore;

    const toggleSettings = () => {
        isSettingsHidden.set(!$isSettingsHidden);
    };

    let transitionParamsBottom = {
        y: 320,
        duration: 200,
        easing: sineIn,
    };
</script>

<Drawer
        placement="bottom"
        bind:hidden={$isSettingsHidden}
        on:close={() => isSettingsHidden.set(true)}
        backdrop={true}
        class="p-6 md:p-8 bg-gray-100 rounded-lg shadow-lg"
        width="w-full"
        transitionType="fly"
        transitionParams={transitionParamsBottom}
    >
        <div class="flex items-center justify-between">
            <button
                type="button"
                onclick={() => isSettingsHidden.set(true)}
                class="p-2 hover:bg-gray-200 rounded-md"
            >
                <ArrowLeft class="h-6 w-6 text-gray-800" />
            </button>
        </div>

        <div class="mt-6">
            <div class="flex flex-col items-center">
                <div class="mt-2 bg-white p-6 rounded-lg shadow-lg">
                    <h2 class="text-2xl font-semibold text-gray-800">
                        Account Settings
                    </h2>
                    <div class="mt-4">
                        <button class="button w-full" onclick={toggleSettings}
                            >Close Settings</button
                        >
                    </div>
                </div>
            </div>
        </div>

        <div class="mt-6 flex">
            <Button
                on:click={() => isSettingsHidden.set(true)}
                class="bg-blue-500 hover:bg-blue-600 text-white rounded-full px-6 py-2"
            >
                Close
            </Button>
        </div>
    </Drawer>