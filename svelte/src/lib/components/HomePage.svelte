<script>
    import QRScannerUi from "$lib/components/QRScannerUi.svelte";
    import { DEBUG_MODE } from "$lib/config";
    import { loadQRScanner } from "$lib/helpers/camera";
    import {
        Camera,
        Settings,
        LogIn,
        FileText,
        Clipboard,
        Edit,
        UserPlus,
        UserCog,
    } from "lucide-svelte";
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
        userRole,
    } = homePageStore;

    const toggleLogin = () => {
        isAuthDrawerHidden.set(false);
    };

    const toggleSettings = () => {
        isSettingsHidden.set(!$isSettingsHidden);
    };

    const startQRCode = () => {
        loadQRScanner(DEBUG_MODE ? "AHU 00001" : undefined);
    };
</script>

<IssuesHistoryDrawer />

<div class={!$startQRScanner ? "hidden" : ""}>
    <QRScannerUi />
</div>

<main
    class="container px-4 py-5 pt-2 min-h-screen bg-slate-100{$startQRScanner
        ? ' hidden'
        : ''} "
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
            Welcome, {$userRole}!
        </h1>
        <p class="text-lg text-gray-600 dark:text-gray-400 mt-2">
            Choose an action below to get started
        </p>
    </div>

    <div class="grid gap-5 md:grid-cols-3">
        {#if $userRole === "employee"}
            <!-- Employee: Report Failures -->
            <div
                class="card p-4 pt-3 bg-white rounded-lg shadow-md"
                onclick={startQRCode}
                onkeydown={startQRCode}
                tabindex="0"
                role="button"
            >
                <div class="card-content">
                    <Clipboard
                        class="w-12 h-12 mx-auto text-blue-600 dark:text-white"
                    />
                    <div class="card-title mt-3 text-xl font-semibold">
                        Report Failure or Malfunction
                    </div>
                    <div
                        class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                    >
                        Scan QR codes and submit issues related to failures or
                        malfunctions.
                    </div>
                </div>
            </div>
        {/if}

        {#if $userRole === "mechanic"}
            <!-- Mechanic: View & Edit Items, View Issues, Print QR Codes -->
            <div
                class="card p-4 pt-3 bg-white rounded-lg shadow-md"
                onclick={startQRCode}
                onkeydown={startQRCode}
                tabindex="0"
                role="button"
            >
                <div class="card-content">
                    <Camera
                        class="w-12 h-12 mx-auto text-green-600 dark:text-white"
                    />
                    <div class="card-title mt-3 text-xl font-semibold">
                        Print QR Codes
                    </div>
                    <div
                        class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                    >
                        View and print QR codes for items to manage their
                        information.
                    </div>
                </div>
            </div>

            <div class="card p-4 pt-3 bg-white rounded-lg shadow-md">
                <div class="card-content">
                    <Edit
                        class="w-12 h-12 mx-auto text-orange-600 dark:text-white"
                    />
                    <div class="card-title mt-3 text-xl font-semibold">
                        View & Edit Items
                    </div>
                    <div
                        class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                    >
                        Add new items, edit existing ones, and view item
                        details.
                    </div>
                </div>
            </div>

            <div class="card p-4 pt-3 bg-white rounded-lg shadow-md">
                <div
                    class="card-content"
                    onclick={() => isIssuesHistoryHidden.set(false)}
                    onkeydown={() => isIssuesHistoryHidden.set(false)}
                    tabindex="0"
                    role="button"
                >
                    <FileText
                        class="w-12 h-12 mx-auto text-teal-600 dark:text-white"
                    />
                    <div class="card-title mt-3 text-xl font-semibold">
                        View Issues History
                    </div>
                    <div
                        class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                    >
                        Track and resolve past issues with detailed logs.
                    </div>
                </div>
            </div>
        {/if}

        {#if $userRole === "master"}
            <!-- Master: Account Management & Role Assignment -->
            <div
                class="card p-4 pt-3 bg-white rounded-lg shadow-md"
                onclick={toggleSettings}
                onkeydown={toggleSettings}
                tabindex="0"
                role="button"
            >
                <div class="card-content">
                    <UserCog
                        class="w-12 h-12 mx-auto text-purple-600 dark:text-white"
                    />
                    <div class="card-title mt-3 text-xl font-semibold">
                        Account Management
                    </div>
                    <div
                        class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                    >
                        Manage user accounts and assign roles to individuals.
                    </div>
                </div>
            </div>

            <div class="card p-4 pt-3 bg-white rounded-lg shadow-md">
                <div class="card-content">
                    <UserPlus
                        class="w-12 h-12 mx-auto text-indigo-600 dark:text-white"
                    />
                    <div class="card-title mt-3 text-xl font-semibold">
                        Assign Roles
                    </div>
                    <div
                        class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                    >
                        Assign different roles to users: employee, mechanic, or
                        other.
                    </div>
                </div>
            </div>
        {/if}

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

        <!-- Login/Logout -->
        <div
            class="card p-4 pt-3 bg-white rounded-lg rounded-br-none rounded-bl-none shadow-md md:absolute md:bottom-0 md:right-0 md:left-0"
        >
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
        background-color: #003965;
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
