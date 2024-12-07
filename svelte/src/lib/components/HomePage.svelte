<script>
    import QRScannerUi from "$lib/components/QRScannerUi.svelte";
    import { DEBUG_MODE } from "$lib/config";
    import { loadQRScanner } from "$lib/helpers/camera";
    import { LightbulbOff } from "lucide-svelte";
    import { homePageStore } from "$lib/helpers/homepage";
    import SettingsDrawer from "$lib/components/SettingsDrawer.svelte";
    import AuthDrawer from "$lib/components/AuthDrawer.svelte";
    const { isLoggedIn, isSettingsHidden, startQRScanner, isAuthDrawerHidden } =
        homePageStore;

    const toggleLogin = () => {
        isAuthDrawerHidden.set(false);
        isLoggedIn.set(!$isLoggedIn);
    };

    const toggleSettings = () => {
        isSettingsHidden.set(!$isSettingsHidden);
    };

    const startQRCode = () => {
        startQRScanner.set(!$startQRScanner);
        loadQRScanner(DEBUG_MODE ? "AHU 00001" : undefined); // Debug by adding an ID here
    };
</script>

<div class={!$startQRScanner ? "hidden" : ""}>
    <QRScannerUi />
</div>

<main
    class="container px-1 py-1 bg-slate-100{$startQRScanner ? ' hidden' : ''}"
>
    <div class="text-center mb-4">
        <img
            src="/Fejlemingsapp_logo.png"
            alt="logo"
            width="128"
            height="auto"
            class="m-auto mt-1"
        />
        <h1 class="text-3xl font-semibold text-gray-800 dark:text-white">
            Welcome, User!
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400 mt-2">
            Choose an action below to get started
        </p>
    </div>
    <div class="grid gap-3 md:grid-cols-3">
        <!-- Start QR Code Scanner -->
        <div class="card p-5 bg-white rounded-lg shadow-md">
            <div
                class="card-content"
                onclick={startQRCode}
                onkeydown={startQRCode}
                tabindex="0"
                role="button"
            >
                <LightbulbOff
                    class="w-10 h-10 mx-auto text-blue-600 dark:text-white"
                />
                <div class="card-title mt-3">Start QR Code Scanner</div>
                <div
                    class="card-description text-sm text-gray-500 dark:text-gray-300"
                >
                    Scan QR codes using your camera to decode information.
                </div>
            </div>
        </div>

        <!-- Settings -->
        <div class="card p-5 bg-white rounded-lg shadow-md">
            <div
                class="card-content"
                onclick={toggleSettings}
                onkeydown={toggleSettings}
                tabindex="0"
                role="button"
            >
                <LightbulbOff
                    class="w-10 h-10 mx-auto text-yellow-600 dark:text-white"
                />
                <div class="card-title mt-3">Settings</div>
                <div
                    class="card-description text-sm text-gray-500 dark:text-gray-300"
                >
                    Configure your preferences and manage your account settings.
                </div>
            </div>
        </div>

        <!-- Login/Logout -->
        <div class="card p-5 bg-white rounded-lg shadow-md">
            <div class="card-content">
                <LightbulbOff
                    class="w-10 h-10 mx-auto text-green-600 dark:text-white"
                />
                <div class="card-title mt-3">
                    {#if $isLoggedIn}
                        <span class="text-green-500">Logged in</span>
                    {:else}
                        <button class="button" onclick={toggleLogin}
                            >Login</button
                        >
                    {/if}
                </div>
                <div
                    class="card-description text-sm text-gray-500 dark:text-gray-300"
                >
                    {#if $isLoggedIn}
                        You're successfully logged in.
                    {:else}
                        Please log in to access more features.
                    {/if}
                </div>
            </div>
        </div>
    </div>
    <SettingsDrawer />
    <AuthDrawer />
</main>

<style>
    .container {
        max-width: 1200px;
        margin: 0 auto;
    }

    .card {
        transition: all 0.3s ease;
    }

    .card:hover {
        background-color: #e3e3e3;
        cursor: pointer;
    }

    .card-content {
        text-align: center;
    }

    .card-title {
        font-size: 1.25rem;
        font-weight: bold;
        color: #1e293b;
    }

    .card-description {
        color: #4b5563;
    }

    .button {
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        background-color: #2563eb;
        color: #fff;
        border: none;
        font-size: 1rem;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }

    .button:hover {
        background-color: #1d4ed8;
    }

    *:focus:not(:focus-visible) {
        outline: none;
    }

    :focus-visible {
        outline-color: lightgreen;
    }
</style>
