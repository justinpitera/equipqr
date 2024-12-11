<script lang="ts">
    import { ArrowLeft, Bell, Globe, Sun, Trash2 } from "lucide-svelte";
    import { homePageStore } from "$lib/helpers/homepage";
    import { Button, Drawer } from "flowbite-svelte";
    import { sineIn } from "svelte/easing";
    import { notify } from "$lib/helpers/notify";
    import { langChecker, languages, translations } from "$lib/locales";
    import { defaultLang } from "$lib/config";
    import { setLanguage } from "$lib/helpers/server-requests";
    import { onDestroy } from "svelte";

    const {
        isSettingsHidden,
        notificationsEnabled,
        darkModeEnabled,
        selectedLanguage,
        isLoggedIn,
    } = homePageStore;

    $effect(() => {
        const html = document.querySelector("html");
        if (!html) return;
        const invert = `invert(${$darkModeEnabled ? '1' : '0'})`;
        html.style.filter = invert;
        html.style.background = $darkModeEnabled ? 'white' : '';
        for (const container of document.querySelectorAll('.toast-container')) {
            (container as HTMLElement).style.filter = invert;
        }
    });

    function t(key: string): string {
        const langTranslations = translations[$selectedLanguage];
        langChecker(key);
        return langTranslations?.[key] || key;
    }

    const toggleSettings = () => {
        isSettingsHidden.set(!$isSettingsHidden);
    };

    const resetSettings = () => {
        notificationsEnabled.set(true);
        localStorage.setItem("notificationsEnabled", "true");
        if ($isLoggedIn && $selectedLanguage !== defaultLang)
            setLanguage(defaultLang);
        selectedLanguage.set(defaultLang);
        localStorage.setItem("savedLang", defaultLang);
        notify(
            "Settings Reset",
            "Settings have been reset to defaults.",
            "info",
        );
    };

    let transitionParamsBottom = {
        y: 320,
        duration: 200,
        easing: sineIn,
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
        <h2 class="text-xl font-bold text-gray-800">{t("Settings")}</h2>
    </div>

    <!-- Content -->
    <div class="mt-6 space-y-6">
        <!-- Language Selector -->
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
                <Globe
                    class="h-5 w-5 text-green-500"
                    style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                />
                <label
                    for="language-selector"
                    class="text-gray-800 font-semibold">{t("Language")}</label
                >
            </div>
            <select
                id="language-selector"
                bind:value={$selectedLanguage}
                class="mt-2 p-2 border rounded-md focus:ring-2 focus:ring-blue-400"
                onchange={() => {
                    localStorage.setItem("savedLang", $selectedLanguage);
                    setLanguage($selectedLanguage);
                }}
            >
                {#each languages as { code, label }}
                    <option value={code}>{label}</option>
                {/each}
            </select>
        </div>
        <!-- Notifications Toggle -->
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
                <Bell
                    class="h-5 w-5 text-blue-500"
                    style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                />
                <span class="text-gray-800 font-semibold"
                    >{t("Notifications")}</span
                >
            </div>
            <label
                class="switch"
                style="filter: invert({$darkModeEnabled ? '1' : '0'});"
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
        </div>
        <!-- Darkmode Toggle -->
        <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
                <Sun
                    class="h-5 w-5 text-yellow-500"
                    style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                />
                <span class="text-gray-800 font-semibold">{t("Dark Mode")}</span
                >
            </div>
            <label
                class="switch"
                style="filter: invert({$darkModeEnabled ? '1' : '0'});"
            >
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
            class="flex items-center text-red-600 hover:text-red-800"
            style="filter: invert({$darkModeEnabled ? '1' : '0'});"
        >
            <Trash2 class="h-5 w-5 mr-1" />
            {t("Reset to Defaults")}
        </button>
        <Button
            on:click={toggleSettings}
            class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg"
            style="filter: invert({$darkModeEnabled ? '1' : '0'});"
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
