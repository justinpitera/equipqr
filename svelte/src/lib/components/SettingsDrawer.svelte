<script lang="ts">
    import ArrowLeft from "lucide-svelte/icons/arrow-left";
    import Globe from "lucide-svelte/icons/globe";
    import Sun from "lucide-svelte/icons/sun";
    import Trash2 from "lucide-svelte/icons/trash-2";
    import Button from "flowbite-svelte/Button.svelte";
    import Drawer from "flowbite-svelte/Drawer.svelte";
    import { notify } from "$lib/helpers/notify";
    import { t, languages } from "$lib/locales";
    import { defaultLang } from "$lib/config";
    import { onDestroy } from "svelte";
    import { flyTransitionParamsBottom } from "$lib/helpers/fly";
    import store from "$lib/store";
    const {
        isSettingsHidden,
        notificationsEnabled,
        darkModeEnabled,
        selectedLanguage,
    } = store;

    $effect(() => {
        document.documentElement.classList.toggle("dark", $darkModeEnabled);
    });

    const toggleSettings = () => {
        isSettingsHidden.set(!$isSettingsHidden);
    };

    const resetSettings = () => {
        notificationsEnabled.set(true);
        localStorage.setItem("notificationsEnabled", "true");
        localStorage.setItem("savedLang", defaultLang);
        if ($selectedLanguage !== defaultLang) {
            selectedLanguage.set(defaultLang);
            location.reload();
        }
        notify(
            "Settings Reset",
            "Settings have been reset to defaults.",
            "info",
        );
    };
    onDestroy(() => {
        isSettingsHidden.set(true);
    });
</script>

<Drawer
    id="settings-drawer"
    placement="bottom"
    bind:hidden={$isSettingsHidden}
    backdrop={true}
    class="drawer-box p-6 md:p-8 bg-gray-100 dark:bg-gray-900 rounded-lg shadow-lg max-w-[600px] m-auto"
    width="w-full"
    transitionType="fly"
    transitionParams={flyTransitionParamsBottom}
    activateClickOutside={false}
>
    <!-- Header -->
    <div class="flex items-center justify-between">
        <button
            type="button"
            onclick={() => isSettingsHidden.set(true)}
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-md"
        >
            <ArrowLeft class="h-6 w-6 text-gray-800 dark:text-white" />
        </button>
        <h2 class="text-xl font-bold text-gray-800 dark:text-white">{t("Settings")}</h2>
    </div>

    <!-- Content -->
    <div class="mt-6 space-y-6">
        <!-- Language Selector -->
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
                <Globe
                    class="h-5 w-5 text-green-500"
                />
                <label
                    for="language-selector"
                    class="text-gray-800 dark:text-gray-200 font-semibold">{t("Language")}</label
                >
            </div>
            <select
                id="language-selector"
                bind:value={$selectedLanguage}
                class="mt-2 p-2 border rounded-md focus:ring-2 focus:ring-blue-400 dark:bg-gray-800 dark:text-white dark:border-gray-600"
                onchange={() => {
                    localStorage.setItem("savedLang", $selectedLanguage);
                    location.reload();
                }}
            >
                {#each languages as { code, label }}
                    <option value={code}>{label}</option>
                {/each}
            </select>
        </div>
        <!-- Notifications Toggle
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
                <Bell
                    class="h-5 w-5 text-blue-500"
                />
                <span class="text-gray-800 font-semibold"
                    >{t("Notifications")}</span
                >
            </div>
            <label
                class="switch"
            >
                <input
                    type="checkbox"
                    bind:checked={$notificationsEnabled}
                    onchange={() => {
                        localStorage.setItem(
                            "notificationsEnabled",
                            $notificationsEnabled ? "true" : "false",
                        );
                    }}
                />
                <span class="slider round"></span>
            </label>
        </div> -->
        <!-- Darkmode Toggle -->
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
                <Sun
                    class="h-5 w-5 text-yellow-500"
                />
                <span class="text-gray-800 dark:text-gray-200 font-semibold">{t("Dark Mode")}</span
                >
            </div>
            <label class="switch">
                <input
                    type="checkbox"
                    bind:checked={$darkModeEnabled}
                    onchange={() => {
                        localStorage.setItem(
                            "darkModeEnabled",
                            $darkModeEnabled ? "true" : "false",
                        );
                    }}
                />
                <span class="slider round"></span>
            </label>
        </div>
    </div>

    <!-- Footer Buttons -->
    <div class="mt-6 flex justify-between items-center">
        <button
            onclick={resetSettings}
            class="flex items-center text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
        >
            <Trash2 class="h-5 w-5 mr-1" />
            {t("Reset to Defaults")}
        </button>
        <Button
            on:click={toggleSettings}
            class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg"
        >
            {t("Close")}
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
