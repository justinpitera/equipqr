<script>
    import QRScannerUi from "$lib/components/QRScannerUi.svelte";
    import { DEBUG_MODE } from "$lib/config";
    import { loadQRScanner } from "$lib/helpers/camera";
    import { Camera, Settings, LogIn, FileText } from "lucide-svelte";
    import { homePageStore } from "$lib/helpers/homepage";
    import SettingsDrawer from "$lib/components/SettingsDrawer.svelte";
    import AuthDrawer from "$lib/components/AuthDrawer.svelte";
    import IssuesHistoryDrawer from "$lib/components/IssuesHistoryDrawer.svelte";

    const {
        isLoggedIn,
        isSettingsHidden,
        startQRScanner,
        isAuthDrawerHidden,
        isIssuesHistoryHidden,
    } = homePageStore;

    const toggleLogin = () => {
        isAuthDrawerHidden.set(false);
    };

    const toggleSettings = () => {
        isSettingsHidden.set(!$isSettingsHidden);
    };

    const startQRCode = () => {
        loadQRScanner(DEBUG_MODE ? "AHU 00001" : undefined); // Debug by adding an ID here
    };
</script>

<IssuesHistoryDrawer />

<div class={!$startQRScanner ? "hidden" : ""}>
    <QRScannerUi />
</div>

<main
    class="container px-4 py-5 pt-2 min-h-screen bg-slate-100{$startQRScanner
        ? ' hidden'
        : ''}"
>
    <div class="text-center mb-4">
        <img
            src="/Fejlemingsapp_logo.png"
            alt="logo"
            width="128"
            height="auto"
            class="m-auto mt-2"
        />
        <h1 class="text-3xl font-semibold text-gray-800 dark:text-white">
            Welcome, User!
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400 mt-2">
            Choose an action below to get started
        </p>
    </div>

    <div class="grid gap-5 md:grid-cols-3">
        <!-- Start QR Code Scanner -->
        <div class="card p-4 pt-3 bg-white rounded-lg shadow-md">
            <div
                class="card-content"
                onclick={startQRCode}
                onkeydown={startQRCode}
                tabindex="0"
                role="button"
            >
                <Camera
                    class="w-12 h-12 mx-auto text-blue-600 dark:text-white"
                />
                <div class="card-title mt-3 text-xl font-semibold">
                    Scan QR Code
                </div>
                <div
                    class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                >
                    Use your camera to scan QR codes and retrieve information
                    instantly.
                </div>
            </div>
        </div>

        <!-- Settings -->
        <div class="card p-4 pt-3 bg-white rounded-lg shadow-md">
            <div
                class="card-content"
                onclick={toggleSettings}
                onkeydown={toggleSettings}
                tabindex="0"
                role="button"
            >
                <Settings
                    class="w-12 h-12 mx-auto text-yellow-600 dark:text-white"
                />
                <div class="card-title mt-3 text-xl font-semibold">
                    Settings
                </div>
                <div
                    class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                >
                    Configure your preferences and manage your account settings.
                </div>
            </div>
        </div>

        <!-- View Issues History -->
        <div
            class="card p-4 pt-3 bg-white rounded-lg shadow-md"
            onclick={() => isIssuesHistoryHidden.set(false)}
            onkeydown={() => isIssuesHistoryHidden.set(false)}
            tabindex="0"
            role="button"
        >
            <div class="card-content">
                <FileText
                    class="w-12 h-12 mx-auto text-teal-600 dark:text-white"
                />
                <div class="card-title mt-3 text-xl font-semibold">
                    View Issues History
                </div>
                <div
                    class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                >
                    Check past issues and keep track of changes to troubleshoot
                    effectively.
                </div>
            </div>
        </div>

        <!-- Login/Logout -->
        <div class="card p-4 pt-3 bg-white rounded-lg shadow-md">
            <div class="card-content">
                {#if $isLoggedIn}
                    <LogIn
                        class="w-12 h-12 mx-auto text-green-600 dark:text-white"
                    />
                    <div class="card-title mt-3 text-xl font-semibold">
                        Logged In
                    </div>
                    <div
                        class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                    >
                        You're successfully logged in. Enjoy using the platform.
                    </div>
                {:else}
                    <button class="button" onclick={toggleLogin}>Login</button>
                    <div
                        class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                    >
                        Log in to access personalized features.
                    </div>
                {/if}
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
        background-color: #f1f5f9;
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
        padding: 0.75rem 1.5rem;
        border-radius: 0.375rem;
        background-color: #2563eb;
        color: #fff;
        border: none;
        font-size: 1rem;
        cursor: pointer;
        transition: background-color 0.3s ease;
        width: 100%;
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
