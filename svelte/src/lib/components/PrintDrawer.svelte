<script lang="ts">
    import { onMount } from "svelte";
    import ArrowLeft from "lucide-svelte/icons/arrow-left";
    import Check from "lucide-svelte/icons/check";
    import X from "lucide-svelte/icons/x";
    import Table from "flowbite-svelte/Table.svelte";
    import TableBody from "flowbite-svelte/TableBody.svelte";
    import TableBodyCell from "flowbite-svelte/TableBodyCell.svelte";
    import TableBodyRow from "flowbite-svelte/TableBodyRow.svelte";
    import TableHead from "flowbite-svelte/TableHead.svelte";
    import TableHeadCell from "flowbite-svelte/TableHeadCell.svelte";
    import Drawer from "flowbite-svelte/Drawer.svelte";
    import Button from "flowbite-svelte/Button.svelte";
    import Badge from "flowbite-svelte/Badge.svelte";
    import Card from "flowbite-svelte/Card.svelte";
    import Checkbox from "flowbite-svelte/Checkbox.svelte";
    import { equipment } from "$lib/helpers/equipment";
    import { t } from "$lib/locales";
    import store from "$lib/store";
    const { qrPrintDrawerHidden } = store;

    let vehicles = [
        {
            id: 1,
            name: "Baggage cart (BCT)",
            manufacturer: "Acme",
            model: "V2",
            location: "BBP",
            status: "Needs Maintenance",
            fuelType: "Electric",
            inUse: false,
        },
        {
            id: 2,
            name: "Ground power unit (GPU)",
            manufacturer: "Delta",
            model: "D3",
            location: "CCP",
            status: "Okay",
            fuelType: "Gasoline",
            inUse: true,
        },
        {
            id: 3,
            name: "Manual passenger stair (MPS)",
            manufacturer: "Beta",
            model: "B4",
            location: "DDP",
            status: "Faulty",
            fuelType: "Diesel",
            inUse: false,
        },
        {
            id: 4,
            name: "High loader (HIL)",
            manufacturer: "Polar",
            model: "GSH-1",
            location: "AAP",
            status: "Okay",
            fuelType: "Diesel",
            inUse: true,
        },
        {
            id: 5,
            name: "Baggage cart (BCT)",
            manufacturer: "Acme",
            model: "V2",
            location: "BBP",
            status: "Needs Maintenance",
            fuelType: "Electric",
            inUse: false,
        },
    ];

    const getRandomImage = (vehicleName: string) => {
        const matchingImage = equipment[vehicleName];
        return matchingImage || "https://via.placeholder.com/150";
    };

    let selectedVehicles = $state(new Set<number>());
    let printQueue: {
        id: number;
        name: string;
        status: "pending" | "printing";
    }[] = $state([]);

    const toggleSelection = (id: number) => {
        if (selectedVehicles.has(id)) {
            selectedVehicles.delete(id);
        } else {
            selectedVehicles.add(id);
        }
        selectedVehicles = new Set(selectedVehicles); // Trigger reactivity
    };

    const selectAll = () => {
        vehicles.forEach((vehicle) => selectedVehicles.add(vehicle.id));
        selectedVehicles = new Set(selectedVehicles); // Trigger reactivity
    };

    const deselectAll = () => {
        selectedVehicles.clear();
        selectedVehicles = new Set(selectedVehicles); // Trigger reactivity
    };

    const printNow = () => {
        vehicles.forEach((vehicle) => {
            if (selectedVehicles.has(vehicle.id)) {
                printQueue.push({
                    id: vehicle.id,
                    name: vehicle.name,
                    status: "pending",
                });
            }
        });
        selectedVehicles.clear();
        selectedVehicles = new Set(selectedVehicles); // Trigger reactivity
    };

    const cancelPrint = (id: number) => {
        printQueue = printQueue.filter((item) => item.id !== id);
    };

    const exampleImageUrls = [
        "/images/example_qr.png",
        "/images/example_qr.png",
        "/images/example_qr.png",
        "/images/example_qr.png",
    ];

    let printEcoFriendly = $state(true);

    const printImage = (url: string) => {
        const printWindow = window.open("about:blank", "_new");
        printWindow?.document.open();
        printWindow?.document.write(
            `<html><head><title>Print</title></head><body onload="window.print();" onafterprint="window.close()">
        <img src="${url}" style="width:100%;height:auto;" />
        </body></html>`,
        );
        printWindow?.document.close();
    };

    const printImages = (
        pendingItems: {
            id: number;
            name: string;
            status: "pending" | "printing";
        }[],
    ) => {
        const printWindow = window.open("about:blank", "_new");
        printWindow?.document.open();
        let printBody =
            '<html><head><title>Print</title></head><body onload="window.print();" onafterprint="window.close()">';
        for (const pendingItem of pendingItems) {
            pendingItem.status = "printing";
            const imageUrl =
                exampleImageUrls[pendingItem.id % exampleImageUrls.length];
            printBody += `<img src="${imageUrl}" style="width:100%;height:auto;display:block;" />`;
        }
        printBody += "</body></html>";
        printWindow?.document.write(printBody);
        printWindow?.document.close();
    };

    onMount(() => {
        const interval = setInterval(() => {
            if (printQueue.length === 0) return;
            if (printEcoFriendly) {
                printImages(printQueue);
                printQueue = [];
            } else {
                const pendingItem = printQueue.find(
                    (item) => item.status === "pending",
                );
                if (pendingItem) {
                    pendingItem.status = "printing";
                    const imageUrl =
                        exampleImageUrls[
                            pendingItem.id % exampleImageUrls.length
                        ];
                    printImage(imageUrl);
                    printQueue = printQueue.filter(
                        (item) => item.id !== pendingItem.id,
                    );
                }
            }
        }, 1000);

        return () => clearInterval(interval);
    });
</script>

<Drawer
    id="qr-print-drawer"
    placement="bottom"
    backdrop={true}
    class="drawer-box p-6 bg-gray-100 dark:bg-gray-900 fixed inset-0 z-50"
    width="100"
    bind:hidden={$qrPrintDrawerHidden}
    activateClickOutside={false}
    transitionParams={{
        duration: 0,
        easing: undefined,
    }}
>
    {#if printQueue.length > 0}
        <h3 class="font-semibold mb-2">{t("Print Queue")}</h3>
        <Table>
            <TableHead>
                <TableHeadCell>ID</TableHeadCell>
                <TableHeadCell>{t("Name")}</TableHeadCell>
                <TableHeadCell>{t("Status")}</TableHeadCell>
                <TableHeadCell>{t("Actions")}</TableHeadCell>
            </TableHead>
            <TableBody tableBodyClass="divide-y">
                {#each printQueue as item}
                    <TableBodyRow>
                        <TableBodyCell>{item.id}</TableBodyCell>
                        <TableBodyCell>{item.name}</TableBodyCell>
                        <TableBodyCell>
                            {#if item.status === "printing"}
                                <Badge color="green">{t("Printing")}</Badge>
                            {:else}
                                <Badge color="yellow">{"Pending"}</Badge>
                            {/if}
                        </TableBodyCell>
                        <TableBodyCell>
                            <Button
                                color="red"
                                size="xs"
                                onclick={() => cancelPrint(item.id)}
                            >
                                <X class="w-4 h-4" />
                            </Button>
                        </TableBodyCell>
                    </TableBodyRow>
                {/each}
            </TableBody>
        </Table>
    {:else}
        <div
            class="flex items-center justify-between mb-2"
            style="filter: drop-shadow(0px 1px 3px rgba(0,0,0,0.3));"
        >
            <button
                type="button"
                onclick={() => {
                    qrPrintDrawerHidden.set(true);
                }}
                class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-md"
            >
                <ArrowLeft class="h-6 w-6 text-gray-800 dark:text-white" />
            </button>
            <h2 class="text-xl font-bold text-gray-800 dark:text-white mr-2">
                {t("QR Code Printing")}
            </h2>
        </div>
        <hr />

        <div class="mb-4 mt-2">
            <div
                class="h-[calc(100svh-185px)] overflow-y-auto overflow-x-hidden pb-3"
            >
                <div
                    class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 justify-items-center gap-6"
                >
                    {#each vehicles as vehicle}
                        <Card
                            class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg transition-all hover:shadow-xl p-6"
                        >
                            <div
                                class="flex items-center relative w-fit m-auto"
                            >
                                <Checkbox
                                    inline
                                    disabled
                                    class="border-2 border-blue-500 rounded-md absolute top-0 left-0"
                                    checked={selectedVehicles.has(vehicle.id)}
                                ></Checkbox>
                                <img
                                    src={getRandomImage(vehicle.name)}
                                    alt={vehicle.name}
                                    height="150"
                                    width="150"
                                    class="rounded-lg object-cover"
                                />
                            </div>
                            <h4
                                class="font-bold text-2xl text-gray-800 dark:text-white mb-2 text-center"
                            >
                                {vehicle.name}
                            </h4>
                            <div
                                class="space-y-2 text-sm text-gray-600 dark:text-gray-300 text-center"
                            >
                                <p>
                                    <strong>{t("Manufacturer:")}</strong>
                                    {vehicle.manufacturer}
                                </p>
                                <p>
                                    <strong>{t("Model:")}</strong>
                                    {vehicle.model}
                                </p>
                                <p>
                                    <strong>{t("Location:")}</strong>
                                    {vehicle.location}
                                </p>
                                <p>
                                    <strong>{t("Status:")}</strong>
                                    {vehicle.status}
                                </p>
                                <p>
                                    <strong>{t("Fuel Type:")}</strong>
                                    {vehicle.fuelType}
                                </p>
                            </div>
                            <div
                                class="flex items-center mt-1 space-x-2 text-gray-600 text-center w-fit m-auto"
                            >
                                <strong class="text-sm"
                                    >{t("Operational:")}</strong
                                >
                                {#if vehicle.inUse}
                                    <Check class="text-green-500" />
                                {:else}
                                    <X class="text-red-500" />
                                {/if}
                            </div>
                            <Button
                                color="blue"
                                size="xs"
                                class="mt-4 w-full py-2 rounded-lg text-white font-semibold hover:bg-blue-600 transition-colors"
                                onclick={() => toggleSelection(vehicle.id)}
                            >
                                {selectedVehicles.has(vehicle.id)
                                    ? t("Deselect")
                                    : t("Select")}
                            </Button>
                        </Card>
                    {/each}
                </div>
            </div>
        </div>

        <div
            class="fixed bottom-0 left-0 right-0 bg-gray-200 p-4 text-center pb-4"
        >
            <div class="max-w-[768px] m-auto">
                <Button
                    color="green"
                    size="sm"
                    onclick={selectAll}
                    class="px-4 py-2 rounded-full">{t("Select All")}</Button
                >
                <Button
                    color="red"
                    size="sm"
                    onclick={deselectAll}
                    class="px-4 py-2 rounded-full">{t("Deselect All")}</Button
                >
                <Button
                    color="blue"
                    size="sm"
                    onclick={printNow}
                    class="px-4 py-2 rounded-full">{t("Print Now")}</Button
                >
            </div>
            <div
                class="flex justify-between items-center mt-2 max-w-[768px] m-auto"
            >
                <span class="text-lg font-semibold text-blue-600"
                    >{selectedVehicles.size} {t("selected")}</span
                >
                <Checkbox inline class="me-2" bind:checked={printEcoFriendly}
                    >{t("Eco Friendly")}</Checkbox
                >
            </div>
        </div>
    {/if}
</Drawer>
