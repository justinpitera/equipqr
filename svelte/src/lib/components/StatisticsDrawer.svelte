<script lang="ts">
    import Chart from "flowbite-svelte/Chart.svelte";
    import Drawer from "flowbite-svelte/Drawer.svelte";
    import { t } from "$lib/locales";
    import ArrowLeft from "lucide-svelte/icons/arrow-left";
    import store from "$lib/store";
    const { statisticsDrawerHidden, darkModeEnabled } = store;

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

    // --- Issue Tracking Metrics ---
    let issues = [
        { status: "Reported", date: new Date("2024-01-10") },
        { status: "In Progress", date: new Date("2024-01-10") },
        { status: "In Progress", date: new Date("2024-01-10") },
        { status: "Waiting for parts", date: new Date("2024-01-11") },
        { status: "Ready for pickup", date: new Date("2024-01-11") },
        { status: "Back in service", date: new Date("2024-01-12") },
        { status: "Reported", date: new Date("2024-01-12") },
        { status: "In Progress", date: new Date("2024-01-13") },
        { status: "In Progress", date: new Date("2024-01-13") },
        { status: "Waiting for parts", date: new Date("2024-01-14") },
        { status: "Ready for pickup", date: new Date("2024-01-14") },
        { status: "Back in service", date: new Date("2024-01-15") },
        { status: "Back in service", date: new Date("2024-01-15") },
    ];

    const reportedIssues = issues.filter(
        (issue) => issue.status === "Reported",
    ).length;
    const inProgressIssues = issues.filter(
        (issue) => issue.status === "In Progress",
    ).length;
    const waitingForPartsIssues = issues.filter(
        (issue) => issue.status === "Waiting for parts",
    ).length;
    const readyForPickupIssues = issues.filter(
        (issue) => issue.status === "Ready for pickup",
    ).length;
    const backInServiceIssues = issues.filter(
        (issue) => issue.status === "Back in service",
    ).length;

    // -- Issue Colors --
    const issueColors = {
        Reported: "#dc3545", // Red
        "In Progress": "#007bff", // Blue
        "Waiting for parts": "#ffc107", // Yellow / Orange
        "Ready for pickup": "#6f42c1", // Purple
        "Back in service": "#28a745", // Green
    };
    // --- End Issue Tracking Metrics ---

    // -- Issues Over Time Data --

    const today = new Date();
    const oneDayAgo = new Date(today);
    oneDayAgo.setDate(today.getDate() - 1);
    const oneMonthAgo = new Date(today);
    oneMonthAgo.setMonth(today.getMonth() - 1);

    const issuesOverTime = issues.reduce(
        (acc: { [key: string]: number }, issue) => {
            const dateKey = issue.date.toISOString().split("T")[0];
            acc[dateKey] = (acc[dateKey] || 0) + 1;
            return acc;
        },
        {},
    );

    const issueTimelineData = Object.entries(issuesOverTime)
        .sort((a, b) => new Date(a[0]).getTime() - new Date(b[0]).getTime())
        .map(([date, count]) => ({ x: date, y: count }));

    //--Closed/New Issues over time --
    const closedIssuesDay = issues.filter(
        (issue) =>
            issue.status === "Back in service" && issue.date >= oneDayAgo,
    ).length;
    const closedIssuesMonth = issues.filter(
        (issue) =>
            issue.status === "Back in service" && issue.date >= oneMonthAgo,
    ).length;

    const newIssuesDay = issues.filter(
        (issue) => issue.date >= oneDayAgo,
    ).length;
    const newIssuesMonth = issues.filter(
        (issue) => issue.date >= oneMonthAgo,
    ).length;

    // --- Disk Space Example Metric (Dummy Data)---
    const totalDiskSpaceGB = 100;
    const freeDiskSpaceGB = 65;

    function diskSpacePercentage(free: number, total: number): number {
        return (free / total) * 100;
    }

    const diskSpaceUsed = diskSpacePercentage(
        freeDiskSpaceGB,
        totalDiskSpaceGB,
    );

    // --- End Disk Space Example Metric ---
    // --- Employees Example (Dummy Data) ---

    let employees = [
        { role: "Pilot" },
        { role: "Pilot" },
        { role: "Mechanic" },
        { role: "Mechanic" },
        { role: "Mechanic" },
        { role: "Technician" },
        { role: "Technician" },
        { role: "Administrator" },
    ];

    const totalEmployees = employees.length;
    const pilots = employees.filter(
        (employee) => employee.role === "Pilot",
    ).length;
    const mechanics = employees.filter(
        (employee) => employee.role === "Mechanic",
    ).length;
    const technicians = employees.filter(
        (employee) => employee.role === "Technician",
    ).length;
    const administrators = employees.filter(
        (employee) => employee.role === "Administrator",
    ).length;

    // --- End Employees Example ---
</script>

{#if !$statisticsDrawerHidden}
    <Drawer
        id="statistics-drawer"
        placement="bottom"
        backdrop={true}
        class="drawer-box p-6 bg-gray-100 dark:bg-gray-900 dark:text-white fixed inset-0 z-50"
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
                class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-md"
            >
                <ArrowLeft class="h-6 w-6 text-gray-800 dark:text-white" />
            </button>
            <h2
                class="text-xl font-bold text-gray-800 dark:text-white mr-2"
            >
                {t("Statistics")}
            </h2>
        </div>
        <hr />

        <div class="mb-4">
            <div
                class="h-[calc(100svh-72px-25px)] overflow-y-auto overflow-x-hidden pb-3 grid gap-4 grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4"
            >
                <div class="mt-2">
                    <h3 class="text-xl font-semibold mb-4 text-center">
                        {t("Vehicle Usage")}
                    </h3>
                    <Chart
                        options={{
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
                                                    const sum =
                                                        w.globals.seriesTotals.reduce(
                                                            (
                                                                a: number,
                                                                b: number,
                                                            ) => a + b,
                                                            0,
                                                        );
                                                    return `${sum} ${t("vehicles")}`;
                                                },
                                            },
                                            value: {
                                                show: true,
                                                formatter: function (
                                                    value: string,
                                                ) {
                                                    return (
                                                        value +
                                                        " " +
                                                        t("vehicles")
                                                    );
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
                        } as ApexCharts.ApexOptions}
                    />
                    <hr class="mt-2 mb-2" />
                </div>
                <div class="mt-2">
                    <h3 class="text-xl font-semibold mb-4 text-center">
                        {t("Issue Tracking")}
                    </h3>
                    <Chart
                        options={{
                            series: [
                                {
                                    name: "Issues",
                                    data: [
                                        reportedIssues,
                                        inProgressIssues,
                                        waitingForPartsIssues,
                                        readyForPickupIssues,
                                        backInServiceIssues,
                                    ],
                                },
                            ],
                            labels: [
                                t("Reported"),
                                t("In Progress"),
                                t("Waiting for parts"),
                                t("Ready for pickup"),
                                t("Back in service"),
                            ],
                            colors: [
                                issueColors["Reported"],
                                issueColors["In Progress"],
                                issueColors["Waiting for parts"],
                                issueColors["Ready for pickup"],
                                issueColors["Back in service"],
                            ],
                            chart: {
                                type: "bar",
                                height: "350px",
                                fontFamily: "Inter, sans-serif",
                                toolbar: {
                                    show: false,
                                },
                            },
                            plotOptions: {
                                bar: {
                                    horizontal: false,
                                    columnWidth: "70%",
                                    borderRadiusApplication: "end",
                                    borderRadius: 8,
                                    dataLabels: {
                                        position: "top",
                                    },
                                },
                            },
                            tooltip: {
                                shared: true,
                                intersect: false,
                                style: {
                                    fontFamily: "Inter, sans-serif",
                                },
                            },
                            states: {
                                hover: {
                                    filter: {
                                        type: "darken",
                                        value: 1,
                                    },
                                },
                            },
                            stroke: {
                                show: true,
                                width: 0,
                                colors: ["transparent"],
                            },
                            grid: {
                                show: false,
                                strokeDashArray: 4,
                                padding: {
                                    left: 2,
                                    right: 2,
                                    top: -14,
                                },
                            },
                            dataLabels: {
                                enabled: true,
                                style: {
                                    colors: ["#000000"],
                                    fontFamily: "Inter, sans-serif",
                                },
                                offsetY: -20,
                            },
                            legend: {
                                show: false,
                            },
                            xaxis: {
                                floating: false,
                                labels: {
                                    show: true,
                                    style: {
                                        fontFamily: "Inter, sans-serif",
                                        cssClass:
                                            "text-xs font-normal fill-gray-500 dark:fill-gray-400",
                                    },
                                },
                                axisBorder: {
                                    show: false,
                                },
                                axisTicks: {
                                    show: false,
                                },
                            },
                            yaxis: {
                                show: false,
                            },
                            fill: {
                                opacity: 1,
                            },
                        } as ApexCharts.ApexOptions}
                    />
                </div>
                <div class="mt-2">
                    <h3 class="text-xl font-semibold mb-4 text-center">
                        {t("Issues Over Time")}
                    </h3>
                    <Chart
                        options={{
                            series: [
                                {
                                    name: "Issues",
                                    data: issueTimelineData,
                                },
                            ],
                            chart: {
                                type: "line",
                                height: "350px",
                                fontFamily: "Inter, sans-serif",
                                toolbar: {
                                    show: false,
                                },
                            },
                            stroke: {
                                curve: "smooth",
                            },
                            tooltip: {
                                enabled: true,
                                x: {
                                    show: true,
                                },
                            },
                            grid: {
                                show: true,
                                strokeDashArray: 4,
                                padding: {
                                    left: 2,
                                    right: 2,
                                    top: -26,
                                },
                            },
                            xaxis: {
                                type: "datetime",
                            },
                            yaxis: {
                                show: false,
                            },
                        } as ApexCharts.ApexOptions}
                    />
                    <hr class="mt-2 mb-2" />
                </div>
                <div class="mt-2">
                    <h3 class="text-xl font-semibold mb-4 text-center">
                        {t("Disk Space")}
                    </h3>
                    <Chart
                        options={{
                            series: [diskSpaceUsed],
                            labels: [t("Disk Space Used")],
                            chart: {
                                height: "200px",
                                type: "radialBar",
                            },
                            plotOptions: {
                                radialBar: {
                                    hollow: {
                                        size: "70%",
                                    },
                                    dataLabels: {
                                        show: true,
                                        value: {
                                            formatter: (val) => {
                                                return val.toFixed(2) + "%";
                                            },
                                        },
                                        name: {
                                            show: true,
                                            offsetY: 10,
                                        },
                                    },
                                },
                            },
                            tooltip: {
                                enabled: false,
                            },
                            legend: {
                                show: false,
                            },
                        } as ApexCharts.ApexOptions}
                    />
                    <p class="text-center">
                        {t("Free Disk Space")}: {freeDiskSpaceGB} GB / {totalDiskSpaceGB}
                        GB
                    </p>
                    <hr class="mt-2 mb-2" />
                </div>
                <div class="mt-2">
                    <h3 class="text-xl font-semibold mb-4 text-center">
                        {t("Employees")}
                    </h3>
                    <Chart
                        options={{
                            series: [
                                pilots,
                                mechanics,
                                technicians,
                                administrators,
                            ],
                            labels: [
                                t("Pilots"),
                                t("Mechanics"),
                                t("Technicians"),
                                t("Administrators"),
                            ],
                            chart: {
                                height: 320,
                                width: "100%",
                                type: "pie",
                            },
                            stroke: {
                                colors: ["white"],
                                lineCap: "round",
                            },
                            plotOptions: {
                                pie: {
                                    labels: {
                                        show: true,
                                    },
                                    size: "100%",
                                    dataLabels: {
                                        offset: -25,
                                    },
                                },
                            },
                            dataLabels: {
                                enabled: true,
                                style: {
                                    fontFamily: "Inter, sans-serif",
                                },
                            },
                            legend: {
                                position: "bottom",
                                fontFamily: "Inter, sans-serif",
                            },
                            yaxis: {
                                labels: {
                                    formatter: function (value) {
                                        return value + " " + t("employees");
                                    },
                                },
                            },
                            xaxis: {
                                labels: {
                                    formatter: function (value) {
                                        return value + " " + t("employees");
                                    },
                                },
                                axisTicks: {
                                    show: false,
                                },
                                axisBorder: {
                                    show: false,
                                },
                            },
                        } as ApexCharts.ApexOptions}
                    />
                    <p class="text-center">
                        {t("Total Employees")}: {totalEmployees}
                    </p>
                </div>
                <div class="mt-2">
                    <h3 class="text-xl font-semibold mb-4 text-center">
                        {t("Issue Analysis")}
                    </h3>
                    <p class="text-center">
                        {t("Closed Issues Today")}: {closedIssuesDay}
                    </p>
                    <p class="text-center">
                        {t("Closed Issues This Month")}: {closedIssuesMonth}
                    </p>
                    <p class="text-center">
                        {t("New Issues Today")}: {newIssuesDay}
                    </p>
                    <p class="text-center">
                        {t("New Issues This Month")}: {newIssuesMonth}
                    </p>
                </div>
            </div>
        </div>
    </Drawer>
{/if}
