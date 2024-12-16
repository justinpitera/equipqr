<script lang="ts">
    import ArrowLeft from "lucide-svelte/icons/arrow-left";
    import X from "lucide-svelte/icons/x";
    import Fuel from "lucide-svelte/icons/fuel";
    import BatteryCharging from "lucide-svelte/icons/battery-charging";
    import RefreshCw from "lucide-svelte/icons/refresh-cw";
    import Droplet from "lucide-svelte/icons/droplet";
    import Button from "flowbite-svelte/Button.svelte";
    import Badge from "flowbite-svelte/Badge.svelte";
    import Avatar from "flowbite-svelte/Avatar.svelte";
    import Drawer from "flowbite-svelte/Drawer.svelte";
    import Checkbox from "flowbite-svelte/Checkbox.svelte";
    import { langChecker, translations } from "$lib/locales";
    import { onDestroy } from "svelte";
    import { equipment } from "$lib/helpers/equipment";
    import { flyTransitionParamsBottom } from "$lib/helpers/fly";
    import CheckOutline from "flowbite-svelte-icons/CheckOutline.svelte";
    import store from "$lib/store";
    const {
        selectedLanguage,
        darkModeEnabled,
        qrCodeData,
        detectedGSE,
        isAutoOpenIssueDetails,
        showPopup,
        hideGSEDetail,
    } = store;

    function t(key: string): string {
        const langTranslations = translations[$selectedLanguage];
        langChecker(key);
        return langTranslations?.[key] || key;
    }

    onDestroy(() => {
        hideGSEDetail.set(true);
    });

    const fuelIcons = {
        diesel: Fuel,
        electric: BatteryCharging,
        hybrid: RefreshCw,
        petrol: Droplet,
    } as const;

    const defaultIcon = Fuel;

    function getResolvedIcon(fuelType: string): typeof Fuel {
        return (
            fuelIcons[
                fuelType.split(" ")[0].toLowerCase() as keyof typeof fuelIcons
            ] || defaultIcon
        );
    }

    const statusColors: Record<string, string> = {
        "0": "dark", // Scraped
        "1": "red", // Scrap
        "2": "yellow", // Usable
        "3": "indigo", // Okay
        "4": "purple", // Good condition
        "5": "green", // Very good condition
    };

    const getStatusNumber = (status: string | undefined): string => {
        const match = status?.match(/^(\d+)/);
        return match ? match[1] : "0"; // Default to "0" if no match is found
    };

    const toggleAutoOpenIssueDetails = (event: Event) => {
        isAutoOpenIssueDetails.set(
            ((event as CustomEvent<boolean>).target as HTMLInputElement)
                .checked,
        );
        if (typeof window !== "undefined")
            localStorage.setItem(
                "autoOpenIssueDetails",
                String($isAutoOpenIssueDetails),
            );
    };
</script>

<!-- activateClickOutside={!$isRecentIssueDrawerHidden ? false : true} -->
<Drawer
    id="gse-details-drawer"
    placement="bottom"
    bind:hidden={$hideGSEDetail}
    backdrop={true}
    class="drawer-box p-6 md:p-8 bg-gray-100 rounded-lg md:rounded-none shadow-lg max-w-[600px] m-auto"
    width="w-full"
    transitionType="fly"
    activateClickOutside={false}
    transitionParams={flyTransitionParamsBottom}
>
    <div class="flex items-center justify-between">
        <button
            type="button"
            onclick={() => hideGSEDetail.set(true)}
            class="p-2 hover:bg-gray-200 rounded-md"
        >
            <ArrowLeft class="h-6 w-6 text-gray-800" />
        </button>
        {#if $qrCodeData}
            <div
                class="font-medium inline-flex items-center justify-center px-2.5 py-0.5 text-xs border bg-purple-100 text-purple-800 dark:bg-gray-700 dark:text-purple-400 border-purple-400 dark:border-purple-400 rounded"
                style="filter: invert({$darkModeEnabled ? '1' : '0'});"
            >
                {$qrCodeData}
            </div>
        {/if}
        {#if $detectedGSE && $detectedGSE.old_gse_id}
            <div
                class="font-medium inline-flex items-center justify-center px-2.5 py-0.5 text-xs border bg-red-100 text-red-800 dark:bg-gray-700 dark:text-red-400 border-red-400 dark:border-red-400 rounded"
                style="filter: invert({$darkModeEnabled ? '1' : '0'});"
            >
                {$detectedGSE.old_gse_id}
            </div>
        {/if}
    </div>
    <div class="mt-6">
        {#if $detectedGSE}
            <div class="flex items-center space-x-4">
                <Avatar
                    src={$detectedGSE.gse_type
                        ? equipment[$detectedGSE.gse_type]
                        : undefined}
                    rounded
                    class="w-16 h-16 ring-4 ring-{!$detectedGSE.details &&
                    !$detectedGSE.error
                        ? 'green'
                        : 'red'}-400 dark:ring-red-300"
                    style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                />
                <div class="flex flex-col">
                    <span class="text-xl font-medium text-gray-800"
                        >{$detectedGSE.gse_type}</span
                    >
                    <div class="flex gap-1">
                        {#if $detectedGSE.manufacturer}
                            <Avatar
                                src="/images/kalmar.png"
                                rounded
                                class="w-7 h-7 bg-transparent ring-red-400 dark:ring-red-300"
                                style="filter: invert({$darkModeEnabled
                                    ? '1'
                                    : '0'});"
                            />
                        {/if}
                        <span class="font-semibold text-gray-700"
                            >{$detectedGSE.manufacturer
                                ? $detectedGSE.manufacturer + " - "
                                : ""}{$detectedGSE.model}</span
                        >
                    </div>
                </div>
            </div>

            <div
                class="grid mt-4 grid-cols-2 lg:grid-cols-3 gap-4 text-gray-800"
            >
                <!-- Error Card -->
                {#if $detectedGSE.error}
                    <div
                        class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-red-50"
                    >
                        <p class="font-semibold text-red-600">{t("Error:")}</p>
                        <p>{$detectedGSE.error}</p>
                    </div>
                {/if}

                <!-- Details Card -->
                {#if $detectedGSE.details}
                    <div
                        class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-yellow-50"
                    >
                        <p class="font-semibold text-yellow-600">
                            {t("Details:")}
                        </p>
                        <p>{$detectedGSE.details}</p>
                    </div>
                {/if}

                {#if !$detectedGSE.details && !$detectedGSE.error}
                    {#if $detectedGSE.manufacturer}
                        <!-- Manufacturer Card -->
                        <div
                            class="card p-3 rounded-lg shadow-md bg-white flex items-center gap-2 justify-center"
                        >
                            <div class="text-center">
                                <p class="font-semibold">
                                    {t("Manufacturer:")}
                                </p>
                                <p>{$detectedGSE.manufacturer}</p>
                            </div>
                        </div>
                    {/if}

                    <!-- Model Card -->
                    <div
                        class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-white"
                    >
                        <p class="font-semibold">{t("Model:")}</p>
                        <p>{$detectedGSE.model || t("Unknown")}</p>
                    </div>

                    <!-- Location Card -->
                    <div
                        class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-white"
                    >
                        <p class="font-semibold">{t("Location:")}</p>
                        <p>{$detectedGSE.location || t("Not specified")}</p>
                    </div>

                    <!-- Status Card -->
                    <div
                        class="card flex-col p-3 rounded-lg shadow-md bg-white flex items-center justify-between"
                    >
                        <p class="font-semibold">{t("Status:")}</p>
                        <div
                            class="font-medium inline-flex items-center justify-center px-2.5 py-0.5 text-xs border bg-{statusColors[
                                getStatusNumber($detectedGSE?.status)
                            ]}-100 text-{statusColors[
                                getStatusNumber($detectedGSE?.status)
                            ]}-800 dark:bg-gray-700 dark:text-{statusColors[
                                getStatusNumber($detectedGSE?.status)
                            ]}-400 border-{statusColors[
                                getStatusNumber($detectedGSE?.status)
                            ]}-400 dark:border-{statusColors[
                                getStatusNumber($detectedGSE?.status)
                            ]}-400 rounded"
                            style="filter: invert({$darkModeEnabled
                                ? '1'
                                : '0'});"
                        >
                            {$detectedGSE.status || t("Unavailable")}
                        </div>
                    </div>

                    <!-- Fuel Type Card -->
                    {#if $detectedGSE.type_of_fuel}
                        <div
                            class="card flex-col p-3 rounded-lg shadow-md bg-white flex items-center justify-between"
                        >
                            <p class="font-semibold">{t("Fuel Type:")}</p>
                            <div class="flex items-center gap-2">
                                {$detectedGSE.type_of_fuel || t("Unknown")}
                                {#if $detectedGSE.type_of_fuel}
                                    {@const ResolvedIcon = getResolvedIcon(
                                        $detectedGSE.type_of_fuel,
                                    )}
                                    <ResolvedIcon
                                        style="vertical-align: middle;"
                                    />
                                {/if}
                            </div>
                        </div>
                    {/if}

                    <!-- In Use Card -->
                    <div
                        class="card flex-col p-3 rounded-lg shadow-md bg-white flex items-center justify-between"
                    >
                        <p class="font-semibold">{t("In Use:")}</p>
                        {#if $detectedGSE.in_use}
                            <Badge
                                color="green"
                                rounded
                                large
                                class="!p-1 !font-semibold"
                                style="filter: invert({$darkModeEnabled
                                    ? '1'
                                    : '0'});"
                            >
                                <CheckOutline class="h-4 w-4" />
                            </Badge>
                        {:else}
                            <Badge
                                rounded
                                large
                                class="!p-1 !font-semibold"
                                style="filter: invert({$darkModeEnabled
                                    ? '1'
                                    : '0'});"
                            >
                                <X
                                    class="h-4 w-4 text-primary-800 dark:text-primary-400"
                                />
                            </Badge>
                        {/if}
                    </div>

                    <!-- Last Service Date Card -->
                    {#if $detectedGSE.latest_service_chassi}
                        <div
                            class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-white"
                        >
                            <p class="font-semibold">
                                {t("Last Service Date:")}
                            </p>
                            <p>{$detectedGSE.latest_service_chassi}</p>
                        </div>
                    {/if}

                    <!-- Lift Inspection Expiry Card -->
                    {#if $detectedGSE.lift_inspection_expires}
                        <div
                            class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-white"
                        >
                            <p class="font-semibold">
                                {t("Lift Inspection Expiry:")}
                            </p>
                            <p>
                                {$detectedGSE.lift_inspection_expires}
                            </p>
                        </div>
                    {/if}

                    <!-- Latest Service Unit Card -->
                    {#if $detectedGSE.latest_service_unit}
                        <div
                            class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-white"
                        >
                            <p class="font-semibold">
                                {t("Latest Service Unit:")}
                            </p>
                            <p>{$detectedGSE.latest_service_unit}</p>
                        </div>
                    {/if}

                    <!-- Capacity Card -->
                    {#if $detectedGSE.capacity}
                        <div
                            class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-white"
                        >
                            <p class="font-semibold">{t("Capacity:")}</p>
                            <p>{$detectedGSE.capacity}</p>
                        </div>
                    {/if}
                {/if}
            </div>
        {:else if $qrCodeData}
            <div class="flex flex-col items-center">
                <h2 class="text-base font-bold text-center">
                    {t("Could not find information for GSE ID:")}
                </h2>
                <div
                    class="font-medium mt-3 inline-flex items-center justify-center px-2.5 py-0.5 text-xs border bg-purple-100 text-purple-800 dark:bg-gray-700 dark:text-purple-400 border-purple-400 dark:border-purple-400 rounded"
                    style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                >
                    {$qrCodeData}
                </div>
            </div>
        {:else}
            <div class="flex flex-col items-center">
                <h2 class="text-base font-bold text-center">
                    {t("Could not find information for scanned QR code.")}<br
                    />{t("Please try again...")}
                </h2>
            </div>
        {/if}
    </div>
    <div class="mt-6 flex justify-between">
        <div class="flex items-center space-x-4{$showPopup ? '' : ' hidden'}">
            <label for="toggle" class="text-lg">{t("Auto Open:")}</label>
            <Checkbox
                id="toggle"
                class="mt-1"
                checked={$isAutoOpenIssueDetails}
                on:change={toggleAutoOpenIssueDetails}
                color="blue"
                style="filter: invert({$darkModeEnabled ? '1' : '0'});"
            >
                {#if $isAutoOpenIssueDetails}
                    {t("On")}
                {:else}
                    {t("Off")}
                {/if}
            </Checkbox>
        </div>
        <Button
            on:click={() => hideGSEDetail.set(true)}
            class="bg-blue-500 hover:bg-blue-600 text-white rounded-full px-6 py-2"
            style="filter: invert({$darkModeEnabled ? '1' : '0'});"
        >
            {t("Close")}
        </Button>
    </div>
</Drawer>
