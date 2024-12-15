<script lang="ts">
    import QRScannerUi from "$lib/components/QRScannerUi.svelte";
    import { DEBUG_MODE } from "$lib/config";
    import { loadQRScanner, qrScannerStore } from "$lib/helpers/camera";
    import Camera from "lucide-svelte/icons/camera";
    import Settings from "lucide-svelte/icons/settings";
    import Search from "lucide-svelte/icons/search";
    import LogIn from "lucide-svelte/icons/log-in";
    import FileText from "lucide-svelte/icons/file-text";
    import Clipboard from "lucide-svelte/icons/clipboard";
    import UserCog from "lucide-svelte/icons/user-cog";
    import ChartBarStacked from "lucide-svelte/icons/chart-bar-stacked";
    import User from "lucide-svelte/icons/user";
    import { homePageStore } from "$lib/helpers/homepage";
    import SettingsDrawer from "$lib/components/SettingsDrawer.svelte";
    import AuthDrawer from "$lib/components/AuthDrawer.svelte";
    import { langChecker, translations } from "$lib/locales";
    import { getGSEDetails } from "$lib/helpers/server-requests";
    import { detailsDrawerStore } from "$lib/helpers/details";
    import { notify } from "$lib/helpers/notify";
    import { cancelReportStore } from "$lib/helpers/cancel-report";

    const {
        isLoggedIn,
        isSettingsHidden,
        startQRScanner,
        isAuthDrawerHidden,
        isIssuesHistoryHidden,
        userRole,
        selectedLanguage,
        darkModeEnabled,
        qrPrintDrawerHidden,
        statisticsDrawerHidden,
    } = homePageStore;

    const { isAutoOpenMostRecentIssue, isAutoOpenIssueDetails, showPopup } =
        qrScannerStore;

    function t(key: string): string {
        const langTranslations = translations[$selectedLanguage];
        langChecker(key);
        return langTranslations?.[key] || key;
    }

    const toggleLogin = () => {
        isAuthDrawerHidden.set(false);
    };

    const toggleSettings = () => {
        isSettingsHidden.set(!$isSettingsHidden);
    };

    const checkCodeManual = async () => {
        const result = prompt(t("Check GSE ID"));
        if (result) {
            qrScannerStore.qrCodeData.set(result);
            try {
                const gseDetails = await getGSEDetails(result);
                if (gseDetails?.gse_id) {
                    qrScannerStore.detectedGSE.set(gseDetails);
                    if (gseDetails.error && gseDetails.details) {
                        notify(gseDetails.error, gseDetails.details, "error");
                    } else {
                        detailsDrawerStore.hideGSEDetail.set(false);
                        if (gseDetails.most_recent_issue)
                            homePageStore.isRecentIssueDrawerHidden.set(false);
                    }
                } else {
                    notify(
                        "Error",
                        t("Could not find any information for") + " " + result,
                        "error",
                        5000,
                        true,
                    );
                    qrScannerStore.detectedGSE.set(null);
                }
            } catch (e) {
                qrScannerStore.detectedGSE.set(null);
                cancelReportStore.closeReportHidden.set(false);
            }
        }
    };

    const checkCodeQR = () => {
        loadQRScanner(DEBUG_MODE ? "AHU 00001" : undefined, true);
    };

    const startQRCode = () => {
        loadQRScanner(DEBUG_MODE ? "AHU 00001" : undefined);
    };

    const startManualReport = async () => {
        const result = prompt(t("Enter the GSE ID"));
        if (result) {
            qrScannerStore.qrCodeData.set(result);
            qrScannerStore.showPopup.set(true);
            try {
                const gseDetails = await getGSEDetails(result);
                if (gseDetails?.gse_id) {
                    qrScannerStore.detectedGSE.set(gseDetails);
                    if (gseDetails.error && gseDetails.details) {
                        notify(gseDetails.error, gseDetails.details, "error");
                    } else {
                        if ($isAutoOpenIssueDetails)
                            detailsDrawerStore.hideGSEDetail.set(false);
                        if ($isAutoOpenMostRecentIssue)
                            homePageStore.isRecentIssueDrawerHidden.set(false);
                    }
                } else {
                    notify(
                        "Error",
                        t("Could not find any information for") + " " + result,
                        "error",
                        5000,
                        true,
                    );
                    qrScannerStore.detectedGSE.set(null);
                    if ($showPopup)
                        cancelReportStore.closeReportHidden.set(false);
                }
            } catch (e) {
                qrScannerStore.detectedGSE.set(null);
                cancelReportStore.closeReportHidden.set(false);
            }
        }
    };
</script>

<div class={!$startQRScanner ? "hidden" : ""}>
    <QRScannerUi />
</div>

<main
    class="px-4 py-5 pt-2 h-screen overflow-y-auto relative bg-slate-100{$startQRScanner ||
    !$isIssuesHistoryHidden
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
            style="filter: invert({$darkModeEnabled ? '1' : '0'});"
        />
        <h1
            class="text-3xl font-semibold text-gray-800 dark:text-white{!$isLoggedIn
                ? ' hidden'
                : ''}"
        >
            {t("Welcome,")}
            {#if $userRole === "mechanic"}
                {t("Mechanic")}!
            {:else if $userRole === "employee"}
                {t("Employee")}!
            {:else if $userRole === "master"}
                {t("Supervisor")}!
            {:else}
                {t($userRole)}!
            {/if}
        </h1>
        <p
            class="text-lg text-gray-600 dark:text-gray-400 mt-2{!$isLoggedIn
                ? ' hidden'
                : ''}"
        >
            {t("Choose an action below to get started")}
        </p>
    </div>

    <!-- Settings Bubble -->
    <button
        class="absolute top-4 left-4 rounded-full h-10 w-10 bg-gray-200 hover:bg-gray-300 flex items-center justify-center transition-colors duration-200 focus:outline-none p-0"
        onclick={toggleSettings}
        aria-label="Settings"
        style="min-width: auto;"
    >
        <Settings class="h-6 w-6 text-gray-700" />
    </button>
    <button
        class="absolute top-4 right-4 rounded-full h-10 w-10 bg-gray-200 hover:bg-gray-300 flex items-center justify-center transition-colors duration-200 focus:outline-none p-0"
        onclick={toggleLogin}
        aria-label="Account"
        style="min-width: auto;"
    >
        <User class="h-6 w-6 text-gray-700" />
    </button>

    <div class="grid gap-5 md:grid-cols-3 xl:grid-cols-5 justify-items-center">
        {#if $isLoggedIn}
            <!-- Master: Statistics -->
            {#if $userRole === "master"}
                <!-- Statistics Management -->
                <div
                    class="card w-full p-4 pt-3 bg-white rounded-lg shadow-md"
                    onclick={() => statisticsDrawerHidden.set(false)}
                    onkeypress={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                            statisticsDrawerHidden.set(false);
                        }
                    }}
                    tabindex="0"
                    role="button"
                >
                    <div class="card-content">
                        <ChartBarStacked
                            class="w-12 h-12 mx-auto text-indigo-600 dark:text-white"
                            style="filter: invert({$darkModeEnabled
                                ? '1'
                                : '0'});"
                        />
                        <div class="card-title mt-3 text-xl font-semibold">
                            {t("Statistics")}
                        </div>
                        <div
                            class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                        >
                            {t(
                                "View key metrics and performance data. Monitor progress and identify trends.",
                            )}
                        </div>
                    </div>
                </div>
            {/if}

            <!-- Mechanic: View Issues -->
            {#if $userRole === "mechanic" || $userRole === "master"}
                <div
                    class="card w-full p-4 pt-3 bg-white rounded-lg shadow-md"
                    onclick={() => isIssuesHistoryHidden.set(false)}
                    onkeypress={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                            isIssuesHistoryHidden.set(false);
                        }
                    }}
                    tabindex="0"
                    role="button"
                >
                    <div class="card-content">
                        <FileText
                            class="w-12 h-12 mx-auto text-teal-600 dark:text-white"
                            style="filter: invert({$darkModeEnabled
                                ? '1'
                                : '0'});"
                        />
                        <div class="card-title mt-3 text-xl font-semibold">
                            {t("View Issue History")}
                        </div>
                        <div
                            class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                        >
                            {t(
                                "Track and resolve past issues with detailed logs.",
                            )}
                            {#if $userRole === "master"}
                                <b>{" "}{t("(Visible to Mechanics)")}</b>
                            {/if}
                        </div>
                    </div>
                </div>
            {/if}

            {#if $userRole === "mechanic"}
                <!-- Check Code (QR) -->
                <div
                    class="card w-full p-4 pt-3 bg-white rounded-lg shadow-md"
                    onclick={checkCodeQR}
                    onkeypress={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                            checkCodeQR();
                        }
                    }}
                    tabindex="0"
                    role="button"
                >
                    <div class="card-content">
                        <Search
                            class="w-12 h-12 mx-auto text-purple-600 dark:text-white"
                            style="filter: invert({$darkModeEnabled
                                ? '1'
                                : '0'});"
                        />
                        <div class="card-title mt-3 text-xl font-semibold">
                            {t("Check Code (QR)")}
                        </div>
                        <div
                            class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                        >
                            {t(
                                "Scan a QR code to get information about a vehicle or part.",
                            )}
                        </div>
                    </div>
                </div>

                <!-- Check Code (Manual) -->
                <div
                    class="card w-full p-4 pt-3 bg-white rounded-lg shadow-md"
                    onclick={checkCodeManual}
                    onkeypress={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                            checkCodeManual();
                        }
                    }}
                    tabindex="0"
                    role="button"
                >
                    <div class="card-content">
                        <Search
                            class="w-12 h-12 mx-auto text-yellow-600 dark:text-white"
                            style="filter: invert({$darkModeEnabled
                                ? '1'
                                : '0'});"
                        />
                        <div class="card-title mt-3 text-xl font-semibold">
                            {t("Check Code (Manual)")}
                        </div>
                        <div
                            class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                        >
                            {t(
                                "Enter a code manually to get information about a vehicle or part.",
                            )}
                        </div>
                    </div>
                </div>

                <!-- Report QR Failures -->
                <div
                    class="card w-full p-4 pt-3 bg-white rounded-lg shadow-md"
                    onclick={startQRCode}
                    onkeypress={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                            startQRCode();
                        }
                    }}
                    tabindex="0"
                    role="button"
                >
                    <div class="card-content">
                        <Clipboard
                            class="w-12 h-12 mx-auto text-blue-600 dark:text-white"
                            style="filter: invert({$darkModeEnabled
                                ? '1'
                                : '0'});"
                        />
                        <div class="card-title mt-3 text-xl font-semibold">
                            {t("Report Failure (QR)")}
                        </div>
                        <div
                            class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                        >
                            {t(
                                "Scan QR codes and submit issues related to failures or malfunctions.",
                            )}
                        </div>
                    </div>
                </div>

                <!-- Report Manual Failures -->
                <div
                    class="card w-full p-4 pt-3 bg-white rounded-lg shadow-md"
                    onclick={startManualReport}
                    onkeypress={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                            startManualReport();
                        }
                    }}
                    tabindex="0"
                    role="button"
                >
                    <div class="card-content">
                        <Clipboard
                            class="w-12 h-12 mx-auto text-black-600 dark:text-white"
                        />
                        <div class="card-title mt-3 text-xl font-semibold">
                            {t("Report Failure (Manually)")}
                        </div>
                        <div
                            class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                        >
                            {t(
                                "Enter a code manually and submit issues related to failures or malfunctions.",
                            )}
                        </div>
                    </div>
                </div>
            {:else}
                <!-- Report QR Failures -->
                <div
                    class="card w-full p-4 pt-3 bg-white rounded-lg shadow-md"
                    onclick={startQRCode}
                    onkeypress={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                            startQRCode();
                        }
                    }}
                    tabindex="0"
                    role="button"
                >
                    <div class="card-content">
                        <Clipboard
                            class="w-12 h-12 mx-auto text-blue-600 dark:text-white"
                            style="filter: invert({$darkModeEnabled
                                ? '1'
                                : '0'});"
                        />
                        <div class="card-title mt-3 text-xl font-semibold">
                            {t("Report Failure (QR)")}
                        </div>
                        <div
                            class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                        >
                            {t(
                                "Scan QR codes and submit issues related to failures or malfunctions.",
                            )}
                        </div>
                    </div>
                </div>

                <!-- Report Manual Failures -->
                <div
                    class="card w-full p-4 pt-3 bg-white rounded-lg shadow-md"
                    onclick={startManualReport}
                    onkeypress={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                            startManualReport();
                        }
                    }}
                    tabindex="0"
                    role="button"
                >
                    <div class="card-content">
                        <Clipboard
                            class="w-12 h-12 mx-auto text-black-600 dark:text-white"
                        />
                        <div class="card-title mt-3 text-xl font-semibold">
                            {t("Report Failure (Manually)")}
                        </div>
                        <div
                            class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                        >
                            {t(
                                "Enter a code manually and submit issues related to failures or malfunctions.",
                            )}
                        </div>
                    </div>
                </div>

                <!-- Check Code (QR) -->
                <div
                    class="card w-full p-4 pt-3 bg-white rounded-lg shadow-md"
                    onclick={checkCodeQR}
                    onkeypress={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                            checkCodeQR();
                        }
                    }}
                    tabindex="0"
                    role="button"
                >
                    <div class="card-content">
                        <Search
                            class="w-12 h-12 mx-auto text-purple-600 dark:text-white"
                            style="filter: invert({$darkModeEnabled
                                ? '1'
                                : '0'});"
                        />
                        <div class="card-title mt-3 text-xl font-semibold">
                            {t("Check Code (QR)")}
                        </div>
                        <div
                            class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                        >
                            {t(
                                "Scan a QR code to get information about a vehicle or part.",
                            )}
                        </div>
                    </div>
                </div>

                <!-- Check Code (Manual) -->
                <div
                    class="card w-full p-4 pt-3 bg-white rounded-lg shadow-md"
                    onclick={checkCodeManual}
                    onkeypress={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                            checkCodeManual();
                        }
                    }}
                    tabindex="0"
                    role="button"
                >
                    <div class="card-content">
                        <Search
                            class="w-12 h-12 mx-auto text-yellow-600 dark:text-white"
                            style="filter: invert({$darkModeEnabled
                                ? '1'
                                : '0'});"
                        />
                        <div class="card-title mt-3 text-xl font-semibold">
                            {t("Check Code (Manual)")}
                        </div>
                        <div
                            class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                        >
                            {t(
                                "Enter a code manually to get information about a vehicle or part.",
                            )}
                        </div>
                    </div>
                </div>
            {/if}

            <!-- Mechanic: Print QR Codes -->
            {#if $userRole === "mechanic" || $userRole === "master"}
                <div
                    class="card w-full p-4 pt-3 bg-white rounded-lg shadow-md"
                    onclick={() => qrPrintDrawerHidden.set(false)}
                    onkeypress={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                            qrPrintDrawerHidden.set(false);
                        }
                    }}
                    tabindex="0"
                    role="button"
                >
                    <div class="card-content">
                        <Camera
                            class="w-12 h-12 mx-auto text-green-600 dark:text-white"
                            style="filter: invert({$darkModeEnabled
                                ? '1'
                                : '0'});"
                        />
                        <div class="card-title mt-3 text-xl font-semibold">
                            {t("Print QR Codes")}
                        </div>
                        <div
                            class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                        >
                            {t(
                                "View and print QR codes for items to manage their information.",
                            )}
                            {#if $userRole === "master"}
                                <b>{" "}{t("(Visible to Mechanics)")}</b>
                            {/if}
                        </div>
                    </div>
                </div>
            {/if}

            <!-- Master: Account Management -->
            {#if $userRole === "master"}
                <!-- Account Management -->
                <div
                    class="card w-full p-4 pt-3 bg-white rounded-lg shadow-md"
                    onclick={() => alert("WIP")}
                    onkeypress={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                            alert("WIP");
                        }
                    }}
                    tabindex="0"
                    role="button"
                >
                    <div class="card-content">
                        <UserCog
                            class="w-12 h-12 mx-auto text-purple-600 dark:text-white"
                            style="filter: invert({$darkModeEnabled
                                ? '1'
                                : '0'});"
                        />
                        <div class="card-title mt-3 text-xl font-semibold">
                            {t("Account Management")}
                        </div>
                        <div
                            class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                        >
                            {t(
                                "Manage user accounts and assign roles to individuals.",
                            )}
                        </div>
                    </div>
                </div>
            {/if}
        {/if}

        <div
            class="card w-full p-4 pt-3 bg-white rounded-lg shadow-md"
            onclick={toggleSettings}
            onkeypress={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                    toggleSettings();
                }
            }}
            tabindex="0"
            role="button"
        >
            <div class="card-content">
                <Settings
                    class="w-12 h-12 mx-auto text-red-600 dark:text-white"
                    style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                />
                <div class="card-title mt-3 text-xl font-semibold">
                    {t("Settings")}
                </div>
                <div
                    class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                >
                    {t(
                        "Configure your preferences and manage your account settings.",
                    )}
                </div>
            </div>
        </div>

        <!-- Login -->
        <div
            class="card w-full p-4 pt-3 bg-white rounded-lg rounded-br-none rounded-bl-none shadow-md"
            onclick={toggleLogin}
            onkeypress={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                    toggleLogin();
                }
            }}
            tabindex="0"
            role="button"
        >
            <div class="card-content">
                {#if $isLoggedIn}
                    <LogIn
                        class="w-12 h-12 mx-auto text-green-600 dark:text-white"
                        style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                    />
                    <div class="card-title mt-3 text-xl font-semibold">
                        {t("Logged In")}
                    </div>
                    <div
                        class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                    >
                        {t(
                            "You're successfully logged in. Enjoy using the platform.",
                        )}
                    </div>
                {:else}
                    <button
                        class="button"
                        onclick={toggleLogin}
                        style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                        >{t("Login")}</button
                    >
                    <div
                        class="card-description text-sm text-gray-500 dark:text-gray-300 mt-1"
                    >
                        {t("Log in to access personalized features.")}
                    </div>
                {/if}
            </div>
        </div>
    </div>

    <SettingsDrawer />
    <AuthDrawer />
</main>

<style>
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
