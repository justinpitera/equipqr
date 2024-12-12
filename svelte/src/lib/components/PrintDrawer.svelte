<script lang="ts">
    import { Drawer, Checkbox, Button, Badge } from "flowbite-svelte";
    import { onMount } from "svelte";
    import { X } from "lucide-svelte";
    import {
        Table,
        TableBody,
        TableBodyCell,
        TableBodyRow,
        TableHead,
        TableHeadCell,
    } from "flowbite-svelte";
    import { homePageStore } from "$lib/helpers/homepage";
    const { qrPrintDrawerHidden } = homePageStore;

    let vehicles = [
        { id: 1, name: "Vehicle 1" },
        { id: 2, name: "Vehicle 2" },
        { id: 3, name: "Vehicle 3" },
        { id: 4, name: "Vehicle 4" },
    ];

    let selectedVehicles = new Set<number>();
    let printQueue: {
        id: number;
        name: string;
        status: "pending" | "printing";
    }[] = [];

    const toggleSelection = (id: number) => {
        if (selectedVehicles.has(id)) {
            selectedVehicles.delete(id);
        } else {
            selectedVehicles.add(id);
        }
    };

    const selectAll = () => {
        vehicles.forEach((vehicle) => selectedVehicles.add(vehicle.id));
    };

    const deselectAll = () => {
        selectedVehicles.clear();
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
    };

    const cancelPrint = (id: number) => {
        printQueue = printQueue.filter((item) => item.id !== id);
    };

    onMount(() => {
        const interval = setInterval(() => {
            const pendingItem = printQueue.find(
                (item) => item.status === "pending",
            );
            if (pendingItem) {
                pendingItem.status = "printing";
                setTimeout(() => {
                    printQueue = printQueue.filter(
                        (item) => item.id !== pendingItem.id,
                    );
                }, 1000);
            }
        }, 1000);

        return () => clearInterval(interval);
    });
</script>

<Drawer
    id="qr-print-drawer"
    placement="bottom"
    backdrop={true}
    style="z-index: 60;"
    class="drawer-box p-6 bg-gray-100"
    bind:hidden={$qrPrintDrawerHidden}
>
    <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-bold">QR Code Printing</h2>
        <Button
            color="red"
            size="sm"
            onclick={() => qrPrintDrawerHidden.set(true)}>Close</Button
        >
    </div>

    <div class="mb-4">
        <h3 class="font-semibold mb-2">Vehicles</h3>
        <div class="grid grid-cols-2 gap-4">
            {#each vehicles as vehicle}
                <Checkbox
                    id={`vehicle-${vehicle.id}`}
                    value={vehicle.id}
                    checked={selectedVehicles.has(vehicle.id)}
                    onchange={() => toggleSelection(vehicle.id)}
                >
                    {vehicle.name}
                </Checkbox>
            {/each}
        </div>
    </div>

    <div class="flex items-center justify-between mb-4">
        <span>{selectedVehicles.size} selected</span>
        <div class="space-x-2">
            <Button color="green" size="sm" onclick={selectAll}
                >Select All</Button
            >
            <Button color="red" size="sm" onclick={deselectAll}
                >Deselect All</Button
            >
            <Button color="blue" size="sm" onclick={printNow}>Print Now</Button>
        </div>
    </div>

    <h3 class="font-semibold mb-2">Print Queue</h3>
    <Table>
        <TableHead>
            <TableHeadCell>ID</TableHeadCell>
            <TableHeadCell>Name</TableHeadCell>
            <TableHeadCell>Status</TableHeadCell>
            <TableHeadCell>Actions</TableHeadCell>
        </TableHead>
        <TableBody tableBodyClass="divide-y">
            {#each printQueue as item}
                <TableBodyRow>
                    <TableBodyCell>{item.id}</TableBodyCell>
                    <TableBodyCell>{item.name}</TableBodyCell>
                    <TableBodyCell>
                        {#if item.status === "printing"}
                            <Badge color="green">Printing</Badge>
                        {:else}
                            <Badge color="yellow">Pending</Badge>
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
</Drawer>
