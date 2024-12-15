<script lang="ts">
    import Chart from "flowbite-svelte/Chart.svelte";
    import Drawer from "flowbite-svelte/Drawer.svelte";
    import { homePageStore } from "$lib/helpers/homepage";
    import { langChecker, translations } from "$lib/locales";
    import ArrowLeft from "lucide-svelte/icons/arrow-left";
    const { statisticsDrawerHidden, selectedLanguage } = homePageStore;

    function t(key: string): string {
        const langTranslations = translations[$selectedLanguage];
        langChecker(key);
        return langTranslations?.[key] || key;
    }

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
    const inUseCount = vehicles.filter((vehicle) => vehicle.inUse).length;
</script>

{#if !$statisticsDrawerHidden}
    <Drawer
        id="statistics-drawer"
        placement="bottom"
        backdrop={true}
        class="drawer-box p-6 bg-gray-100 fixed inset-0 z-50"
        width="100"
        bind:hidden={$statisticsDrawerHidden}
        activateClickOutside={false}
        transitionParams={{
            duration: 0,
            easing: undefined,
        }}
    >
        <div
            class="flex items-center justify-between mb-2"
            style="filter: drop-shadow(0px 1px 3px rgba(0,0,0,0.3));"
        >
            <button
                type="button"
                onclick={() => {
                    statisticsDrawerHidden.set(true);
                }}
                class="p-2 hover:bg-gray-200 rounded-md"
            >
                <ArrowLeft class="h-6 w-6 text-gray-800" />
            </button>
            <h2 class="text-xl font-bold text-gray-800 mr-2">
                {t("Statistics")}
            </h2>
        </div>
        <hr />

        <div class="mb-4">
            <div
                class="h-[calc(100svh-(104px+36px+16px+24px+24px+8px))] overflow-y-auto overflow-x-hidden pb-3"
            >
                <div class="mt-2">
                    <h3 class="text-xl font-semibold mb-4 text-center">
                        {t("Vehicle Usage")}
                    </h3>
                    <Chart options={{
                        series: [inUseCount, vehicles.length - inUseCount],
                        labels: [t("Operational"), t("Not Operational")],
                        colors: ["#28a745", "#dc3545"], // Green and Red
                        chart: {
                            height: 320,
                            type: "donut",
                        },
                        stroke: {
                            colors: ["transparent"],
                        },
                        plotOptions: {
                            pie: {
                                donut: {
                                    labels: {
                                        show: true,
                                        name: {
                                            show: true,
                                        },
                                        total: {
                                            showAlways: true,
                                            show: true,
                                            label: t("Total Vehicles"),
                                            fontFamily: "Inter, sans-serif",
                                            fontSize: "18px",
                                            fontWeight: 600,
                                            formatter: function (w) {
                                                const sum = w.globals.seriesTotals.reduce(
                                                    (a: number, b: number) => a + b,
                                                    0,
                                                );
                                                return `${sum} ${t("vehicles")}`;
                                            },
                                        },
                                        value: {
                                            show: true,
                                            formatter: function (value: string) {
                                                return value + " " + t("vehicles");
                                            },
                                        },
                                    },
                                },
                            },
                        },
                        tooltip: {
                            enabled: true,
                            y: {
                                formatter: function (value) {
                                    return `${value} ${t("vehicles")}`;
                                },
                            },
                        },
                        legend: {
                            position: "bottom",
                            labels: {
                                useSeriesColors: true,
                            },
                            itemMargin: {
                                horizontal: 10,
                                vertical: 5,
                            },
                            fontFamily: "Inter, sans-serif",
                        },
                    } as ApexCharts.ApexOptions} />
                    <hr class="mt-2 mb-2" />
                </div>
            </div>
        </div>
    </Drawer>
{/if}
