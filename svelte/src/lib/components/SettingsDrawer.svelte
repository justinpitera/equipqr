<script>
    import { ArrowLeft, Sun, Bell, Globe, Trash2 } from "lucide-svelte";
    import { homePageStore } from "$lib/helpers/homepage";
    import { Button, Drawer } from "flowbite-svelte";
    import { sineIn } from "svelte/easing";
    import { notify } from "$lib/helpers/notify";

    const { isSettingsHidden, darkMode, notificationsEnabled, selectedLanguage } = homePageStore;

    const toggleSettings = () => {
        isSettingsHidden.set(!$isSettingsHidden);
    };

    const languages = [
        { code: "en", label: "English" },
        { code: "da", label: "Dansk" },
        { code: "no", label: "Norsk" },
        { code: "sv", label: "Svenska" },
    ];

    const saveSettings = () => {
        notify("Settings Saved", "Your preferences have been updated.", "success");
    };

    const resetSettings = () => {
        darkMode.set(false);
        notificationsEnabled.set(true);
        selectedLanguage.set("en");
        notify("Settings Reset", "Settings have been reset to defaults.", "info");
    };

    let transitionParamsBottom = {
        y: 320,
        duration: 200,
        easing: sineIn,
    };
</script>

<Drawer
    id="settings-drawer"
    placement="bottom"
    bind:hidden={$isSettingsHidden}
    on:close={() => isSettingsHidden.set(true)}
    backdrop={true}
    class="p-6 md:p-8 bg-gray-100 rounded-lg shadow-lg"
    width="w-full"
    transitionType="fly"
    transitionParams={transitionParamsBottom}
>
    <!-- Header -->
    <div class="flex items-center justify-between">
        <button
            type="button"
            onclick={() => isSettingsHidden.set(true)}
            class="p-2 hover:bg-gray-200 rounded-md"
        >
            <ArrowLeft class="h-6 w-6 text-gray-800" />
        </button>
        <h2 class="text-xl font-bold text-gray-800">Settings</h2>
    </div>

    <!-- Content -->
    <div class="mt-6 space-y-6">
        <!-- Theme Toggle -->
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
                <Sun class="h-5 w-5 text-yellow-500" />
                <span class="text-gray-800 font-semibold">Dark Mode</span>
            </div>
            <label class="switch">
                <input type="checkbox" bind:checked={$darkMode} />
                <span class="slider round"></span>
            </label>
        </div>

        <!-- Notifications Toggle -->
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
                <Bell class="h-5 w-5 text-blue-500" />
                <span class="text-gray-800 font-semibold">Notifications</span>
            </div>
            <label class="switch">
                <input type="checkbox" bind:checked={$notificationsEnabled} />
                <span class="slider round"></span>
            </label>
        </div>

        <!-- Language Selector -->
        <div class="flex flex-col">
            <label for="language-selector" class="text-gray-800 font-semibold">
                <Globe class="inline h-5 w-5 text-green-500" /> Language
            </label>
            <select
                id="language-selector"
                bind:value={$selectedLanguage}
                class="mt-2 p-2 border rounded-md focus:ring-2 focus:ring-blue-400"
            >
                {#each languages as { code, label }}
                    <option value={code}>{label}</option>
                {/each}
            </select>
        </div>
    </div>

    <!-- Footer Buttons -->
    <div class="mt-6 flex justify-between items-center">
        <button
            onclick={resetSettings}
            class="flex items-center text-red-600 hover:text-red-800"
        >
            <Trash2 class="h-5 w-5 mr-1" /> Reset to Defaults
        </button>
        <Button
            on:click={saveSettings}
            class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg"
        >
            Save Changes
        </Button>
    </div>
</Drawer>

<style>
    .switch {
        position: relative;
        display: inline-block;
        width: 34px;
        height: 20px;
    }

    .switch input {
        opacity: 0;
        width: 0;
        height: 0;
    }

    .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #ccc;
        transition: 0.4s;
        border-radius: 20px;
    }

    .slider:before {
        position: absolute;
        content: "";
        height: 14px;
        width: 14px;
        left: 3px;
        bottom: 3px;
        background-color: white;
        transition: 0.4s;
        border-radius: 50%;
    }

    input:checked + .slider {
        background-color: #003965;
    }

    input:checked + .slider:before {
        transform: translateX(14px);
    }
</style>
