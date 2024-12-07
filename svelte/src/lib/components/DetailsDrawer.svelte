<script lang="ts">
    // Icons and components
    import {
        ArrowLeft,
        X,
        Fuel,
        BatteryCharging,
        RefreshCw,
        Droplet,
    } from "lucide-svelte";
    import { Button, Badge, Avatar, Drawer, Checkbox } from "flowbite-svelte";
    // Utilities
    // QR Scanner utilities
    import { qrScannerStore } from "$lib/helpers/camera";
    const { qrCodeData, detectedGSE, isAutoOpen } = qrScannerStore;
    // Details Drawer utilities
    import { detailsDrawerStore } from "$lib/helpers/details";
    const { hideGSEDetail } = detailsDrawerStore;
    // Cancel report utilities
    import { CheckOutline } from "flowbite-svelte-icons";
    import { sineIn } from "svelte/easing";

    let transitionParamsBottom = {
        y: 320,
        duration: 200,
        easing: sineIn,
    };

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

    const equipment: Equipment = {
        "Air starter unit (ASU)":
            "https://images.unsplash.com/photo-1547963802-25f153e14080?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxBaXIlMjBzdGFydGVyJTIwdW5pdHxlbnwwfHx8fDE3MzM1NzIzNjh8MA&ixlib=rb-4.0.3&q=80&w=400",
        "Airplane heater unit (AHU)":
            "https://images.unsplash.com/photo-1483375801503-374c5f660610?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxBaXJwbGFuZSUyMGhlYXRlciUyMHVuaXR8ZW58MHx8fHwxNzMzNTcyMzY4fDA&ixlib=rb-4.0.3&q=80&w=400",
        "Baggage cart (BCT)":
            "https://images.unsplash.com/photo-1508053803120-e3e60f3f9674?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxCYWdnYWdlJTIwY2FydHxlbnwwfHx8fDE3MzM1NzIzNjl8MA&ixlib=rb-4.0.3&q=80&w=400",
        "Baggage tractor (EBT)":
            "https://images.unsplash.com/photo-1534483650102-4796c5e8f822?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxCYWdnYWdlJTIwdHJhY3RvcnxlbnwwfHx8fDE3MzM1NzIzNjl8MA&ixlib=rb-4.0.3&q=80&w=400",
        "Belt loader (BLT)":
            "https://images.unsplash.com/photo-1608461864721-b8f50c91c147?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxCZWx0JTIwbG9hZGVyfGVufDB8fHx8MTczMzU3MjM2OXww&ixlib=rb-4.0.3&q=80&w=400",
        "Belt loader snake (BLS)":
            "https://images.unsplash.com/photo-1570741066052-817c6de995c8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxCZWx0JTIwbG9hZGVyJTIwc25ha2V8ZW58MHx8fHwxNzMzNTcyMzY5fDA&ixlib=rb-4.0.3&q=80&w=400",
        "Car (CAR)":
            "https://images.unsplash.com/photo-1515569067071-ec3b51335dd0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxDYXJ8ZW58MHx8fHwxNzMzNTcyMzcwfDA&ixlib=rb-4.0.3&q=80&w=400",
        "Container loader transporter (CLT)":
            "https://images.unsplash.com/photo-1624711076872-ecdbc5ade023?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxDb250YWluZXIlMjBsb2FkZXIlMjB0cmFuc3BvcnRlcnxlbnwwfHx8fDE3MzM1NzIzNzB8MA&ixlib=rb-4.0.3&q=80&w=400",
        "De-icing truck (DIT)":
            "https://images.unsplash.com/photo-1598065412434-6544dc76f81f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxEZS1pY2luZyUyMHRydWNrfGVufDB8fHx8MTczMzU3MjM3MHww&ixlib=rb-4.0.3&q=80&w=400",
        "Dolly trailer (DOT)":
            "https://images.unsplash.com/photo-1488539621750-1e0a7ebf61b8?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxEb2xseSUyMHRyYWlsZXJ8ZW58MHx8fHwxNzMzNTcyMzcwfDA&ixlib=rb-4.0.3&q=80&w=400",
        "Ground power unit (GPU)":
            "https://images.unsplash.com/photo-1466629437334-b4f6603563c5?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxHcm91bmQlMjBwb3dlciUyMHVuaXR8ZW58MHx8fHwxNzMzNTcyMzcxfDA&ixlib=rb-4.0.3&q=80&w=400",
        "High loader (HIL)":
            "https://images.unsplash.com/photo-1500408557204-010688b36731?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxIaWdoJTIwbG9hZGVyfGVufDB8fHx8MTczMzU3MjM3MXww&ixlib=rb-4.0.3&q=80&w=400",
        "Manual passenger stair (MPS)":
            "https://images.unsplash.com/photo-1484176141566-3674cda218f0?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxNYW51YWwlMjBwYXNzZW5nZXIlMjBzdGFpcnxlbnwwfHx8fDE3MzM1NzIzNzJ8MA&ixlib=rb-4.0.3&q=80&w=400",
        "Other equipment (OTH)":
            "https://images.unsplash.com/photo-1486693326701-1ea88c6e2af3?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxPdGhlciUyMGVxdWlwbWVudHxlbnwwfHx8fDE3MzM1NzIzNzJ8MA&ixlib=rb-4.0.3&q=80&w=400",
        "Pallet transporter (TRP)":
            "https://images.unsplash.com/photo-1662749033848-746a76aca892?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxQYWxsZXQlMjB0cmFuc3BvcnRlcnxlbnwwfHx8fDE3MzM1NzIzNzJ8MA&ixlib=rb-4.0.3&q=80&w=400",
        "Push back tractor (PBT)":
            "https://images.unsplash.com/photo-1542850802-8a047a726d4e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxQdXNoJTIwYmFjayUyMHRyYWN0b3J8ZW58MHx8fHwxNzMzNTcyMzczfDA&ixlib=rb-4.0.3&q=80&w=400",
        "Self propelled passenger stair (SPS)":
            "https://images.unsplash.com/photo-1506126613408-eca07ce68773?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxTZWxmJTIwcHJvcGVsbGVkJTIwcGFzc2VuZ2VyJTIwc3RhaXJ8ZW58MHx8fHwxNzMzNTcyMzczfDA&ixlib=rb-4.0.3&q=80&w=400",
        "Toilet service unit (TSU)":
            "https://images.unsplash.com/photo-1414452110837-9dab484a417d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxUb2lsZXQlMjBzZXJ2aWNlJTIwdW5pdHxlbnwwfHx8fDE3MzM1NzIzNzN8MA&ixlib=rb-4.0.3&q=80&w=400",
        "Towbar (TOW)": "https://via.placeholder.com/150",
        "Towbar less tractor (TBL)":
            "https://images.unsplash.com/photo-1599642919995-f7ea5ee6a8c6?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxUb3diYXIlMjBsZXNzJTIwdHJhY3RvcnxlbnwwfHx8fDE3MzM1NzIzNzR8MA&ixlib=rb-4.0.3&q=80&w=400",
        "Water service unit (WSU)":
            "https://images.unsplash.com/photo-1483004406427-6acb078d1f2d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w2ODQwMzJ8MHwxfHNlYXJjaHwxfHxXYXRlciUyMHNlcnZpY2UlMjB1bml0fGVufDB8fHx8MTczMzU3MjM3NHww&ixlib=rb-4.0.3&q=80&w=400",
    };

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

    const toggleAutoOpen = (event: Event) => {
        isAutoOpen.set(((event as CustomEvent<boolean>).target as HTMLInputElement).checked);
        if (typeof window !== "undefined")
            localStorage.setItem("autoOpen", String($isAutoOpen));
    };
</script>

<Drawer
    placement="bottom"
    bind:hidden={$hideGSEDetail}
    on:close={() => hideGSEDetail.set(true)}
    backdrop={true}
    class="p-6 md:p-8 bg-gray-100 rounded-lg shadow-lg"
    width="w-full"
    transitionType="fly"
    transitionParams={transitionParamsBottom}
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
            >
                {$qrCodeData}
            </div>
        {/if}
    </div>

    <div class="mt-6">
        {#if $detectedGSE}
            <div class="flex items-center space-x-4">
                <Avatar
                    src={equipment[$detectedGSE.gse_type]}
                    rounded
                    class="w-16 h-16 ring-4 ring-{!$detectedGSE.details &&
                    !$detectedGSE.error
                        ? 'green'
                        : 'red'}-400 dark:ring-red-300"
                />
                <div class="flex flex-col">
                    <span class="text-xl font-medium text-gray-800"
                        >{$detectedGSE.gse_type}</span
                    >
                    <span class="font-semibold text-gray-700"
                        >{$detectedGSE.model}{$detectedGSE.manufacturer
                            ? " - " + $detectedGSE.manufacturer
                            : ""}</span
                    >
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
                        <p class="font-semibold text-red-600">Error:</p>
                        <p>{$detectedGSE.error}</p>
                    </div>
                {/if}

                <!-- Details Card -->
                {#if $detectedGSE.details}
                    <div
                        class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-yellow-50"
                    >
                        <p class="font-semibold text-yellow-600">Details:</p>
                        <p>{$detectedGSE.details}</p>
                    </div>
                {/if}

                {#if !$detectedGSE.details && !$detectedGSE.error}
                    {#if $detectedGSE.manufacturer}
                        <!-- Manufacturer Card -->
                        <div
                            class="card p-3 rounded-lg shadow-md bg-white flex items-center gap-2"
                        >
                            <Avatar
                                src="/images/kalmar.png"
                                rounded
                                class="w-8 h-8 bg-transparent ring-red-400 dark:ring-red-300"
                            />
                            <div>
                                <p class="font-semibold">Manufacturer:</p>
                                <p>{$detectedGSE.manufacturer}</p>
                            </div>
                        </div>
                    {/if}

                    <!-- Model Card -->
                    <div
                        class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-white"
                    >
                        <p class="font-semibold">Model:</p>
                        <p>{$detectedGSE.model || "Unknown"}</p>
                    </div>

                    <!-- Location Card -->
                    <div
                        class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-white"
                    >
                        <p class="font-semibold">Location:</p>
                        <p>{$detectedGSE.location || "Not specified"}</p>
                    </div>

                    <!-- Status Card -->
                    <div
                        class="card flex-col p-3 rounded-lg shadow-md bg-white flex items-center justify-between"
                    >
                        <p class="font-semibold">Status:</p>
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
                        >
                            {$detectedGSE.status || "Unavailable"}
                        </div>
                    </div>

                    <!-- Fuel Type Card -->
                    {#if $detectedGSE.type_of_fuel}
                        <div
                            class="card flex-col p-3 rounded-lg shadow-md bg-white flex items-center justify-between"
                        >
                            <p class="font-semibold">Fuel Type:</p>
                            <div class="flex items-center gap-2">
                                {$detectedGSE.type_of_fuel || "Unknown"}
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
                        <p class="font-semibold">In Use:</p>
                        {#if $detectedGSE.in_use}
                            <Badge
                                color="green"
                                rounded
                                large
                                class="!p-1 !font-semibold"
                            >
                                <CheckOutline class="h-4 w-4" />
                            </Badge>
                        {:else}
                            <Badge rounded large class="!p-1 !font-semibold">
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
                            <p class="font-semibold">Last Service Date:</p>
                            <p>{$detectedGSE.latest_service_chassi}</p>
                        </div>
                    {/if}

                    <!-- Lift Inspection Expiry Card -->
                    {#if $detectedGSE.lift_inspection_expires}
                        <div
                            class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-white"
                        >
                            <p class="font-semibold">Lift Inspection Expiry:</p>
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
                            <p class="font-semibold">Latest Service Unit:</p>
                            <p>{$detectedGSE.latest_service_unit}</p>
                        </div>
                    {/if}

                    <!-- Capacity Card -->
                    {#if $detectedGSE.capacity}
                        <div
                            class="card flex-col items-center text-center p-3 rounded-lg shadow-md bg-white"
                        >
                            <p class="font-semibold">Capacity:</p>
                            <p>{$detectedGSE.capacity}</p>
                        </div>
                    {/if}
                {/if}
            </div>
        {:else if $qrCodeData}
            <div class="flex flex-col items-center">
                <h2 class="text-base font-bold text-center">
                    Could not find information for vehicle with GSE id:
                </h2>
                <div
                    class="font-medium inline-flex items-center justify-center px-2.5 py-0.5 text-xs border bg-purple-100 text-purple-800 dark:bg-gray-700 dark:text-purple-400 border-purple-400 dark:border-purple-400 rounded"
                >
                    {$qrCodeData}
                </div>
            </div>
        {:else}
            <div class="flex flex-col items-center">
                <h2 class="text-base font-bold text-center">
                    Could not find information for vehicle, please try again..
                </h2>
            </div>
        {/if}
    </div>

    <div class="mt-6 flex justify-between">
        <div class="flex items-center space-x-4">
            <label for="toggle" class="text-lg">Auto Open:</label>
            <Checkbox
                id="toggle"
                class="mt-1"
                checked={$isAutoOpen}
                on:change={toggleAutoOpen}
                color="blue"
            >
                {#if $isAutoOpen}
                    On
                {:else}
                    Off
                {/if}
            </Checkbox>
        </div>
        <Button
            on:click={() => hideGSEDetail.set(true)}
            class="bg-blue-500 hover:bg-blue-600 text-white rounded-full px-6 py-2"
        >
            Close
        </Button>
    </div>
</Drawer>
