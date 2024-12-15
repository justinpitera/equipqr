<script lang="ts">
    import ArrowLeft from "lucide-svelte/icons/arrow-left";
    import Fuel from "lucide-svelte/icons/fuel";
    import BatteryCharging from "lucide-svelte/icons/battery-charging";
    import RefreshCw from "lucide-svelte/icons/refresh-cw";
    import Droplet from "lucide-svelte/icons/droplet";
    import Button from "flowbite-svelte/Button.svelte";
    import Avatar from "flowbite-svelte/Avatar.svelte";
    import Drawer from "flowbite-svelte/Drawer.svelte";
    import Tooltip from "flowbite-svelte/Tooltip.svelte";
    import { homePageStore } from "$lib/helpers/homepage";
    import { equipment } from "$lib/helpers/equipment";
    import { langChecker, translations } from "$lib/locales";
    import { onMount } from "svelte";
    const { selectedLanguage, addVehiclesDrawerHidden, darkModeEnabled } =
        homePageStore;

    function t(key: string): string {
        const langTranslations = translations[$selectedLanguage];
        langChecker(key);
        return langTranslations?.[key] || key;
    }

    let newGSE = {
        gse_type: "",
        manufacturer: "",
        model: "",
        fuel_type: "",
        status: "",
        location: "",
        in_use: false,
        capacity: "",
        last_service_date: "",
        lift_inspection_expiry: "",
    };

    let items: string[] = [
        "New York",
        "Los Angeles",
        "San Francisco",
        "Chicago",
    ]; // Prefilled location options
    let value: string = "";
    let placeholder: string = "Select an item";
    let filteredItems: string[] = [...items];
    let isOpen = false;
    let inputValue = "";
    let selectedIndex = -1;
    let gseTypes: string[] = [];
    let vehicles: {
        id: string;
        gse_type: string;
        manufacturer?: string;
        model?: string;
        image: string;
    }[] = [];

    $: if (inputValue === "") {
        filteredItems = [...items];
    } else {
        filteredItems = items.filter((item) =>
            item.toLowerCase().includes(inputValue.toLowerCase()),
        );
    }

    function handleInput(event: Event) {
        inputValue = (event.target as HTMLInputElement).value;
        isOpen = true;
        selectedIndex = -1;
    }
    function handleBlur() {
        setTimeout(() => {
            if (isOpen) isOpen = false;
        }, 100);
    }

    function handleItemClick(item: string) {
        value = item;
        inputValue = item;
        isOpen = false;
    }

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

    const getStatusNumber = (status: string | undefined): string => {
        const match = status?.match(/^(\d+)/);
        return match ? match[1] : "0"; // Default to "0" if no match is found
    };

    const statusColors: Record<string, string> = {
        "0": "dark", // Scraped
        "1": "red", // Scrap
        "2": "yellow", // Usable
        "3": "indigo", // Okay
        "4": "purple", // Good condition
        "5": "green", // Very good condition
    };

    function setupVehicles() {
        vehicles = Object.entries(equipment).map(([key, image]) => {
            gseTypes.push(key);
            let manufacturer = "";
            if (key.includes("tractor")) {
                manufacturer = "Kalmar";
            } else if (key.includes("unit")) {
                manufacturer = "Guinault";
            } else if (key.includes("loader")) {
                manufacturer = "TLD";
            }
            return {
                id: key,
                gse_type: key,
                manufacturer: manufacturer,
                image: image,
            };
        });
    }

    function handleKeyDown(event: KeyboardEvent) {
        if (event.key === "ArrowDown") {
            event.preventDefault();
            if (selectedIndex < filteredItems.length - 1) {
                selectedIndex++;
            }
        }
        if (event.key === "ArrowUp") {
            event.preventDefault();
            if (selectedIndex > 0) {
                selectedIndex--;
            }
        }
        if (event.key === "Enter" && selectedIndex > -1) {
            event.preventDefault();
            handleItemClick(filteredItems[selectedIndex]);
        }
        if (event.key === "Escape") {
            isOpen = false;
        }
    }

    function setSelectedClass(index: number): string {
        return index === selectedIndex ? "bg-blue-100 dark:bg-gray-600" : "";
    }

    function handleSubmit() {
        console.log(newGSE);
        newGSE = {
            gse_type: "",
            manufacturer: "",
            model: "",
            fuel_type: "",
            status: "",
            location: "",
            in_use: false,
            capacity: "",
            last_service_date: "",
            lift_inspection_expiry: "",
        };
    }

    onMount(() => {
        setupVehicles();
    });
</script>

<Drawer
    id="new-vehicle-drawer"
    placement="bottom"
    bind:hidden={$addVehiclesDrawerHidden}
    backdrop={true}
    class="drawer-box p-0 bg-gray-100 rounded-lg shadow-lg max-w-[600px] m-auto"
    width="w-full"
    transitionType="fly"
    activateClickOutside={false}
    transitionParams={{
        duration: 0,
        easing: undefined,
    }}
>
    <div
        class="flex items-center justify-between p-4 pb-2 md:p-6 md:bg-white"
        style="filter: drop-shadow(0px 1px 3px rgba(0,0,0,0.3));"
    >
        <button
            type="button"
            onclick={() => addVehiclesDrawerHidden.set(true)}
            class="p-2 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 select-none"
        >
            <ArrowLeft />
        </button>
        <div class="flex flex-col items-center">
            <h2 class="font-bold text-center text-sm">
                {t("Add Vehicles and Ground Equipment")}
            </h2>
        </div>
    </div>
    <hr />
    <div
        class="space-y-4 pt-4 pr-2 pl-2 overflow-y-auto max-h-[calc(100svh-135px)]"
    >
        <div>
            <label for="gse_type" class="block text-sm font-medium"
                >GSE Type</label
            >
            <input
                type="text"
                id="gse_type"
                bind:value={newGSE.gse_type}
                class="w-full border border-gray-300 rounded-lg p-2"
                placeholder="Enter GSE type"
            />
        </div>

        <div>
            <label for="manufacturer" class="block text-sm font-medium"
                >Manufacturer</label
            >
            <input
                type="text"
                id="manufacturer"
                bind:value={newGSE.manufacturer}
                class="w-full border border-gray-300 rounded-lg p-2"
                placeholder="Enter Manufacturer"
            />
        </div>

        <div>
            <label for="model" class="block text-sm font-medium">Model</label>
            <input
                type="text"
                id="model"
                bind:value={newGSE.model}
                class="w-full border border-gray-300 rounded-lg p-2"
                placeholder="Enter Model"
            />
        </div>

        <div>
            <label for="fuel_type" class="block text-sm font-medium"
                >Fuel Type</label
            >
            <input
                type="text"
                id="fuel_type"
                bind:value={newGSE.fuel_type}
                class="w-full border border-gray-300 rounded-lg p-2"
                placeholder="Enter Fuel Type"
            />
        </div>

        <div>
            <label for="status" class="block text-sm font-medium">Status</label>
            <input
                type="text"
                id="status"
                bind:value={newGSE.status}
                class="w-full border border-gray-300 rounded-lg p-2"
                placeholder="Enter Status"
            />
        </div>

        <div>
            <label for="location" class="block text-sm font-medium"
                >Location (Check this out)</label
            >
            <input
                type="text"
                id="location"
                bind:value={newGSE.location}
                class="w-full border border-gray-300 rounded-lg p-2"
                placeholder="Enter Location"
                oninput={handleInput}
                list="location-options"
            />
            <datalist id="location-options">
                {#each filteredItems as item}
                    <option value={item}>{item}</option>
                {/each}
            </datalist>
        </div>

        <div>
            <label for="in_use" class="block text-sm font-medium">In Use</label>
            <input
                type="checkbox"
                id="in_use"
                bind:checked={newGSE.in_use}
                class="w-full border border-gray-300 rounded-lg p-2"
            />
        </div>

        <div>
            <label for="capacity" class="block text-sm font-medium"
                >Capacity</label
            >
            <input
                type="text"
                id="capacity"
                bind:value={newGSE.capacity}
                class="w-full border border-gray-300 rounded-lg p-2"
                placeholder="Enter Capacity"
            />
        </div>

        <div>
            <label for="last_service_date" class="block text-sm font-medium"
                >Last Service Date</label
            >
            <input
                type="date"
                id="last_service_date"
                bind:value={newGSE.last_service_date}
                class="w-full border border-gray-300 rounded-lg p-2"
            />
        </div>

        <div>
            <label
                for="lift_inspection_expiry"
                class="block text-sm font-medium">Lift Inspection Expiry</label
            >
            <input
                type="date"
                id="lift_inspection_expiry"
                bind:value={newGSE.lift_inspection_expiry}
                class="w-full border border-gray-300 rounded-lg p-2"
            />
        </div>

        <div class="flex justify-end">
            <Button
                on:click={handleSubmit}
                class="bg-blue-500 hover:bg-blue-600 text-white rounded-full px-6 py-2"
            >
                Add GSE
            </Button>
        </div>
    </div>

    <div class="mt-2 border-t pt-2 flex justify-between pr-4 pl-4 pb-4">
        <Button
            on:click={() => addVehiclesDrawerHidden.set(true)}
            class="bg-blue-500 hover:bg-blue-600 text-white rounded-full px-6 py-2"
            style="filter: invert({$darkModeEnabled ? '1' : '0'});"
        >
            {t("Close")}
        </Button>
    </div>
</Drawer>
