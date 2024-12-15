<script lang="ts">
    import {
        Drawer,
        Dropdown,
        DropdownItem,
        Modal,
        Search,
        Tooltip,
        Datepicker,
        Textarea,
        Label,
        CloseButton,
        Select,
        Button,
        Indicator,
    } from "flowbite-svelte";
    import {
        Trash2,
        Edit,
        ArrowLeft,
        OctagonAlert,
        Cog,
        Loader,
        CircleCheckBig,
        KeyRound,
        RefreshCcw,
        RefreshCcwDot,
        X,
        ArrowRight,
        ArrowUp,
        Plane,
        Clock,
        Image,
        Video,
    } from "lucide-svelte";
    import { homePageStore } from "$lib/helpers/homepage";
    import { langChecker, translations } from "$lib/locales";
    import {
        CheckOutline,
        ChevronDownOutline,
        EnvelopeOpenOutline,
        ExclamationCircleOutline,
        InfoCircleSolid,
        MicrophoneSolid,
    } from "flowbite-svelte-icons";
    import { onDestroy, onMount, tick } from "svelte";
    import { BACKEND_URL, DEBUG_MODE } from "$lib/config";
    import {
        delete_issue,
        getGSEDetails,
        getIssues,
    } from "$lib/helpers/server-requests";
    import { sineIn } from "svelte/easing";
    import { notify } from "$lib/helpers/notify";
    import { qrScannerStore } from "$lib/helpers/camera";
    import { cancelReportStore } from "$lib/helpers/cancel-report";
    // File upload utilities
    import { fileUploadStore } from "$lib/helpers/file-upload";
    const {
        fullscreenViewer,
        fullscreenImage,
        fullscreenVideo,
        isFullScreenMode,
    } = fileUploadStore;
    import { detailsDrawerStore } from "$lib/helpers/details";
    const { selectedLanguage, isIssuesHistoryHidden, darkModeEnabled, issues } =
        homePageStore;

    function t(key: string): string {
        const langTranslations = translations[$selectedLanguage];
        langChecker(key);
        return langTranslations?.[key] || key;
    }

    const statuses: Record<
        string,
        { label: string; color: string; icon: string }
    > = {
        Reported: { label: "Reported", color: "red", icon: "OctagonAlert" }, // Reported
        "In Progress": { label: "In Progress", color: "blue", icon: "Cog" },
        "Waiting for parts": {
            // Waiting for parts
            label: "Waiting for parts",
            color: "yellow",
            icon: "Loader",
        },
        "Ready for pickup": {
            // "Ready for pickup"
            label: "Ready for pickup",
            color: "purple",
            icon: "KeyRound",
        },
        "Back in service": {
            // "Back in service"
            label: "Back in service",
            color: "green",
            icon: "CircleCheckBig",
        },
    };
    const statusKeys = Object.keys(statuses);

    let issuesScroller: HTMLElement;
    let currentPage = $state(1);
    let totalPages = $state(1); // Math.ceil(issues.length / issuesPerPage)
    let totalIssuesCount = $state(0);
    let issuesPerPage = $state(10);
    let isLoading = $state(false);
    let multiSelectMode = $state(false);
    let editIssue = $state("");
    let showScrollUp = $state(false);
    let searchDropdownOpen = $state(false);
    let filterDropdownOpen = $state(false);
    let clickTimer: NodeJS.Timeout | undefined = undefined;

    const search_categories: {
        label: string;
        icon?: string;
        color?: string;
    }[] = [
        {
            label: "All categories",
        },
    ];
    const filter_by_operable_categories: {
        label: string;
        icon?: string;
        color?: string;
    }[] = [
        {
            label: "Operable/Not Operable",
        },
        {
            label: "Not Operable",
            icon: "x",
            color: "red",
        },
        {
            label: "Operable",
            icon: "check",
            color: "green",
        },
    ];
    for (const status in statuses) {
        search_categories.push({
            label: statuses[status].label,
            icon: statuses[status].icon,
            color: statuses[status].color,
        });
    }

    let selectedCategory = $state(search_categories[0]);
    let selectedFilter = $state(filter_by_operable_categories[0]);
    let searchQuery = $state("");
    let isListening = $state(false);
    // @ts-ignore
    let recognition;

    /* Pull to refresh: */
    const resistance = 0.25;
    let startY = 0;
    let currentY = 0;
    let pulling = $state(false);
    let rotateDeg = 0;
    let shouldRefresh = $state(false);
    let isRefreshing = $state(false);
    let translateY = $state(0);

    function resetDrawer() {
        selectedCategory = search_categories[0];
        selectedFilter = filter_by_operable_categories[0];
        searchQuery = "";
        editIssue = "";
        searchDropdownOpen = false;
        filterDropdownOpen = false;
        isListening = false;
        startY = 0;
        currentY = 0;
        // issuesPerPage = 10;
        totalPages = 1;
        totalIssuesCount = 0;
        pulling = false;
        rotateDeg = 0;
        shouldRefresh = false;
        isRefreshing = false;
        translateY = 0;
        issues.set([]);
        currentPage = 1;
        isLoading = false;
        showScrollUp = false;
        multiSelectMode = false;
    }

    async function openDetailsDrawer(issue: HistoryIssue) {
        qrScannerStore.qrCodeData.set(issue.gse_id);
        const gseDetails = await getGSEDetails(issue.gse_id);
        if (gseDetails) {
            qrScannerStore.detectedGSE.set(gseDetails);
            if (gseDetails.error && gseDetails.details) {
                notify(gseDetails.error, gseDetails.details, "error");
                qrScannerStore.qrCodeData.set("");
            } else {
                detailsDrawerStore.hideGSEDetail.set(false);
                if (gseDetails.most_recent_issue)
                    homePageStore.isRecentIssueDrawerHidden.set(false);
            }
        } else {
            qrScannerStore.detectedGSE.set(null);
            cancelReportStore.closeReportHidden.set(false);
            qrScannerStore.qrCodeData.set("");
        }
    }

    async function loadPage(page?: number) {
        const returned_issues = await getIssues(
            page,
            issuesPerPage,
            () => {
                isLoading = true;
            },
            () => {
                isLoading = false;
            },
        );
        console.log("Fetched Issues", returned_issues);
        if (returned_issues?.data && returned_issues.data.length > 0) {
            if (issuesPerPage !== returned_issues.page_size) {
                issuesPerPage = returned_issues.page_size;
                console.warn("Issues per page changed");
            }
            currentPage = returned_issues.page;
            totalPages = Math.ceil(returned_issues.total / issuesPerPage);
            totalIssuesCount = returned_issues.total;
            const new_issues = returned_issues.data.map(
                (returned_issue, index) => {
                    return {
                        id: returned_issue.id, //number
                        gse_id: returned_issue.gse_id, //string
                        name: returned_issue.reported_by || "", //string
                        issue: returned_issue.issue_description, //string
                        operable: "Yes", //returned_issue.operable,//string
                        status: returned_issue.progress, //returned_issue.status//string
                        estimated_date: returned_issue.estimated_time
                            ? new Date(
                                  returned_issue.estimated_time,
                              ).toLocaleDateString()
                            : undefined, //string
                        reported_at: returned_issue.reported_at
                            ? returned_issue.reported_at
                            : undefined, //string
                        // gate_type: returned_issue.gate_type ? returned_issue.gate_type : undefined, //string
                        // gate_name: returned_issue.gate_name ? returned_issue.gate_name : undefined, //string
                        gate_type: "Gate #" + index,
                        gate_name: "Example",
                        attachments: returned_issue.attachments,
                    } as HistoryIssue;
                },
            );
            console.log("UI Issues Generated By Fetched Issues:", new_issues);
            isLoading = false;
            issues.set(new_issues);
            return new_issues;
        } else {
            currentPage = 1;
            totalPages = 1;
            totalIssuesCount = 0;
            notify(
                "Warning",
                "Could not find any past incidents, try again later...",
                "warning",
            );
            isLoading = false;
            return $issues;
        }
    }

    async function changeIssueStatus(issue: HistoryIssue, status: string) {
        if (editIssue !== issue.id.toString()) return;
        issues.set(
            $issues.map((single_issue) => {
                if (issue.id === single_issue.id) {
                    single_issue.status = status;
                }
                return single_issue;
            }),
        );
        console.warn("WIP tell server");
    }

    function simulateLoadingWithFilters() {
        isLoading = true;
        setTimeout(async () => {
            await loadPage();
            if (selectedFilter.label !== "Operable/Not Operable") {
                if (selectedFilter.label === "Operable") {
                    issues.set(
                        $issues.filter((issue) => issue.operable === "Yes"),
                    );
                } else if (selectedFilter.label === "Not Operable") {
                    issues.set(
                        $issues.filter((issue) => issue.operable === "No"),
                    );
                }
            }
            if (selectedCategory.label !== "All categories") {
                issues.set(
                    $issues.filter(
                        (issue) => issue.status === selectedCategory.label,
                    ),
                );
            }
            isLoading = false;
        }, 1200);
    }

    $effect(() => {
        if (!$isIssuesHistoryHidden && currentPage) loadPage(currentPage);
    });

    let deleteIssuePopup = $state(false);
    let leaveCommentDrawerHidden = $state(true);
    let transitionParams = {
        x: -320,
        duration: 200,
        easing: sineIn,
    };

    function changePage(next: boolean, buttonsLocation: "top" | "bottom") {
        if (isLoading) return;
        // setTimeout(() => {
        //     issuesScroller.scrollTo({ top: 0, behavior: "instant" });
        // }, 100);
        isLoading = true;
        if (buttonsLocation === "bottom") {
            // Scroll down after page switch from the bottom pagination buttons
            const clearOnFinishLoading = setInterval(() => {
                if (!isLoading) {
                    issuesScroller.scrollTo({
                        top: issuesScroller.scrollHeight,
                        behavior: "instant",
                    });
                    clearInterval(clearOnFinishLoading);
                }
            }, 250);
        }
        if (next) {
            currentPage = Math.min(totalPages, currentPage + 1);
        } else {
            currentPage = Math.max(1, currentPage - 1);
        }
    }

    const handleSpecificPageChange = () => {
        if (isLoading) return;
        const newPageInput = prompt(
            t('Enter which page you want to load:') + "\n" + t('Please enter a number between 1 and') + " " +
                totalPages,
        );
        if (newPageInput === null) return;
        const newPage = parseInt(newPageInput.trim());
        if (isNaN(newPage) || newPage < 1 || newPage > totalPages) {
            alert(
                t("Invalid page number. Please enter a number between 1 and") + ' ' +
                    totalPages,
            );
            return;
        }
        currentPage = newPage;
    };

    function toggleSelect(issue: HistoryIssue) {
        // console.log("Viewing issue details:", issue);
    }

    function startMultiSelect() {
        if (multiSelectMode) return;
        // stopMultiSelect();
        // clickTimer = setTimeout(() => {
        //     multiSelectMode = true;
        // }, 800);
    }

    function stopMultiSelect() {
        if (multiSelectMode) return;
        // if (clickTimer) {
        //     clearTimeout(clickTimer);
        //     clickTimer = undefined;
        //     multiSelectMode = false;
        // }
    }

    let delete_issue_id_confirm = "";
    function handleDelete(event: Event, issue: HistoryIssue) {
        event.stopPropagation();
        console.log("Delete Issue", issue);
        deleteIssuePopup = true;
        delete_issue_id_confirm = issue.id.toString();
    }

    function handleEdit(event: Event, issue: HistoryIssue) {
        event.stopPropagation();
        console.log("Edit Issue", issue);
        if (editIssue !== "" && editIssue === issue.id.toString()) {
            editIssue = "";
        } else {
            editIssue = issue.id.toString();
        }
    }

    function startVoiceSearch() {
        if ("webkitSpeechRecognition" in window) {
            // @ts-ignore
            recognition = new webkitSpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = "en-US";
            recognition.onstart = () => {
                isListening = true;
            };
            recognition.onend = () => {
                isListening = false;
                const action = searchQuery.toLowerCase().trim();
                let shouldLoadFilters = false;
                let didFindAction = false;
                if (action === "all categories") {
                    selectedCategory = search_categories[0];
                    selectedFilter = filter_by_operable_categories[0];
                    shouldLoadFilters = true;
                    didFindAction = true;
                } else if (action === "reported") {
                    selectedCategory = search_categories.filter(
                        (cat) => cat.label === "Reported",
                    )[0];
                    shouldLoadFilters = true;
                    didFindAction = true;
                } else if (action === "in progress") {
                    selectedCategory = search_categories.filter(
                        (cat) => cat.label === "In Progress",
                    )[0];
                    shouldLoadFilters = true;
                    didFindAction = true;
                } else if (action === "waiting for parts") {
                    selectedCategory = search_categories.filter(
                        (cat) => cat.label === "Waiting for parts",
                    )[0];
                    shouldLoadFilters = true;
                    didFindAction = true;
                } else if (action === "ready for pickup") {
                    selectedCategory = search_categories.filter(
                        (cat) => cat.label === "Ready for pickup",
                    )[0];
                    shouldLoadFilters = true;
                    didFindAction = true;
                } else if (action === "back in service") {
                    selectedCategory = search_categories.filter(
                        (cat) => cat.label === "Back in service",
                    )[0];
                    shouldLoadFilters = true;
                    didFindAction = true;
                } else if (action === "operable") {
                    selectedFilter = filter_by_operable_categories.filter(
                        (cat) => cat.label === "Operable",
                    )[0];
                    shouldLoadFilters = true;
                    didFindAction = true;
                } else if (action === "not operable") {
                    selectedFilter = filter_by_operable_categories.filter(
                        (cat) => cat.label === "Not Operable",
                    )[0];
                    shouldLoadFilters = true;
                    didFindAction = true;
                } else if (action === "previous page") {
                    didFindAction = true;
                    if (isLoading) {
                        alert(t("Page is still loading..."));
                    } else {
                        if (currentPage === 1) {
                            alert(t("Already reached the first page"));
                        } else {
                            changePage(false, "top");
                        }
                    }
                } else if (action === "next page") {
                    didFindAction = true;
                    if (isLoading) {
                        alert(t("Page is still loading..."));
                    } else {
                        if (currentPage * issuesPerPage >= totalIssuesCount) {
                            alert(t("Already reached the final page"));
                        } else {
                            changePage(true, "top");
                        }
                    }
                }
                if (didFindAction) searchQuery = "";
                if (shouldLoadFilters) {
                    searchDropdownOpen = false;
                    simulateLoadingWithFilters();
                }
            };
            // @ts-ignore
            recognition.onresult = (event) => {
                const transcript =
                    event.results[event.resultIndex][0].transcript;
                searchQuery = transcript;
            };
            // @ts-ignore
            recognition.onerror = (event) => {
                console.error("Speech recognition error", event);
                isListening = false;
            };
        }
        // @ts-ignore
        if (recognition) recognition.start();
    }

    function stopVoiceSearch() {
        // @ts-ignore
        if (recognition) {
            recognition.stop();
            recognition = undefined;
        }
    }

    const calculateProgress = (
        currentIndex: number,
        totalSteps: number,
    ): number => {
        if (currentIndex < 0) return 0;
        if (currentIndex >= totalSteps - 1) return 100;
        return Math.round(((currentIndex + 1) / totalSteps) * 100);
    };

    let interval: NodeJS.Timeout;
    let timeAgo: string[] = $state([]);
    function calculateTimeAgo(reportedAt: string): string {
        const now = new Date();
        const reportedDate = new Date(reportedAt);
        const diff = reportedDate.getTime() - now.getTime();
        const isFuture = diff > 0;

        const absoluteDiff = Math.abs(diff);
        const years = Math.floor(absoluteDiff / (1000 * 60 * 60 * 24 * 365));
        const months = Math.floor(
            (absoluteDiff % (1000 * 60 * 60 * 24 * 365)) /
                (1000 * 60 * 60 * 24 * 30),
        );
        const days = Math.floor(
            (absoluteDiff % (1000 * 60 * 60 * 24 * 30)) / (1000 * 60 * 60 * 24),
        );
        const hours = Math.floor(
            (absoluteDiff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60),
        );
        const minutes = Math.floor(
            (absoluteDiff % (1000 * 60 * 60)) / (1000 * 60),
        );
        const seconds = Math.floor((absoluteDiff % (1000 * 60)) / 1000);

        const parts = [
            years > 0 ? `${years}y` : "",
            months > 0 ? `${months}m` : "",
            days > 0 ? `${days}d` : "",
            hours > 0 ? `${hours}h` : "",
            minutes > 0 ? `${minutes}m` : "",
            seconds > 0 ? `${seconds}s` : "",
        ];

        const timeString = parts
            .filter(Boolean)
            .reduce((acc, part, index, array) => {
                if (index === array.length - 1 && array.length > 1) {
                    return `${acc} and ${part}`;
                }
                return acc ? `${acc}, ${part}` : part;
            }, "");

        if (!timeString) {
            return "Calculating...";
        }

        return isFuture ? `${timeString} left` : `${timeString} ago`;
    }

    onMount(() => {
        interval = setInterval(async () => {
            timeAgo = [];
            for (const issue of $issues) {
                if (issue.estimated_date) {
                    timeAgo.push(calculateTimeAgo(issue.estimated_date));
                } else {
                    timeAgo.push("Not Set");
                }
            }
            await tick();
        }, 1000);
        return () => clearInterval(interval);
    });
    onDestroy(() => {
        resetDrawer();
        stopVoiceSearch();
        if (!DEBUG_MODE) isIssuesHistoryHidden.set(true);
    });
</script>

<Drawer
    id="leave-comment-drawer"
    transitionType="fly"
    {transitionParams}
    backdrop={true}
    style="z-index: 60;"
    placement="bottom"
    activateClickOutside={false}
    bind:hidden={leaveCommentDrawerHidden}
    class="drawer-box"
>
    <div class="flex items-center">
        <h5
            id="drawer-label"
            class="inline-flex items-center mb-6 text-base font-semibold text-gray-500 uppercase dark:text-gray-400"
        >
            <InfoCircleSolid class="w-5 h-5 me-2.5" />Leave a comment
        </h5>
        <CloseButton
            on:click={() => (leaveCommentDrawerHidden = true)}
            class="mb-4 dark:text-white"
        />
    </div>
    <form action="#" class="mb-6">
        <div class="mb-6">
            <Label for="message" class="mb-2">Your message</Label>
            <Textarea
                id="message"
                placeholder="Your message..."
                value="This is an example note that was already put here for testing purposes..."
                rows={4}
                name="message"
            />
        </div>
        <Button
            type="submit"
            class="w-full"
            on:click={() => (leaveCommentDrawerHidden = true)}
            >Send message</Button
        >
    </form>
</Drawer>

<Drawer
    id="issue-history-drawer"
    placement="right"
    bind:hidden={$isIssuesHistoryHidden}
    backdrop={true}
    class="drawer-box p-4 md:p-6 md:pt-4 bg-white rounded-lg shadow-lg overflow-y-hidden"
    width="w-full"
    activateClickOutside={false}
    transitionParams={{
        duration: 0,
        easing: undefined,
    }}
>
    <Modal bind:open={deleteIssuePopup} size="xs" autoclose>
        <div class="text-center">
            <ExclamationCircleOutline
                class="mx-auto mb-4 text-gray-400 w-12 h-12 dark:text-gray-200"
                style="filter: invert({$darkModeEnabled ? '1' : '0'});"
            />
            <h3
                class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400"
            >
                Are you sure you want to delete this issue?
            </h3>
            <Button
                onclick={async () => {
                    isLoading = true;
                    deleteIssuePopup = false;
                    await delete_issue([delete_issue_id_confirm]);
                    issues.set(
                        $issues.filter(
                            (single_issue) =>
                                single_issue.id.toString() !==
                                delete_issue_id_confirm,
                        ),
                    );
                    isLoading = false;
                    delete_issue_id_confirm = "";
                }}
                color="red"
                class="me-2"
                style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                >Yes, I'm sure</Button
            >
            <Button
                onclick={() => {
                    delete_issue_id_confirm = "";
                    deleteIssuePopup = false;
                }}
                color="alternative"
                style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                >No, cancel</Button
            >
        </div>
    </Modal>

    <div
        class="flex items-center justify-between mb-2"
        style="filter: drop-shadow(0px 1px 3px rgba(0,0,0,0.3));"
    >
        <button
            type="button"
            onclick={() => {
                resetDrawer();
                isIssuesHistoryHidden.set(true);
            }}
            class="p-2 hover:bg-gray-200 rounded-md"
        >
            <ArrowLeft class="h-6 w-6 text-gray-800" />
        </button>
        <h2 class="text-xl font-bold text-gray-800 mr-2">
            {t("Issue History")}
        </h2>
    </div>
    <hr />
    {#if showScrollUp}
        <button
            onclick={() => {
                issuesScroller.scrollTo({ top: 0, behavior: "instant" });
            }}
            class="scroll_up"
            title="Scroll up"
        >
            <ArrowUp />
        </button>
    {/if}

    <div
        ontouchstart={(event) => {
            if (isRefreshing) return;
            startY = event.touches[0].clientY;
        }}
        ontouchmove={(event) => {
            if (isRefreshing) return;
            currentY = event.touches[0].clientY;
            if (currentY - startY < 20 || currentY - startY > 20) {
                stopMultiSelect();
            }
            if (currentY - startY > 20) {
                pulling = true;
                rotateDeg = (currentY - startY) * 1;
                translateY = (currentY - startY) * resistance;
                if (rotateDeg > 234) {
                    shouldRefresh = true;
                } else {
                    shouldRefresh = false;
                }
            } else {
                pulling = false;
            }
        }}
        ontouchend={async () => {
            if (isRefreshing) return;
            if (shouldRefresh && issuesScroller.scrollTop === 0) {
                rotateDeg = 0;
                translateY = 90;
                isRefreshing = true;
                await loadPage();
                translateY = 0;
                pulling = false;
                shouldRefresh = false;
                isRefreshing = false;
            } else {
                translateY = 0;
                pulling = false;
                shouldRefresh = false;
            }
        }}
        class="overflow-y-auto h-[calc(100svh-24px-40px-10px)] relative"
        bind:this={issuesScroller}
        onscroll={() => {
            if (issuesScroller.scrollTop > 200) {
                showScrollUp = true;
            } else {
                showScrollUp = false;
            }
        }}
    >
        {#if pulling}
            <div class="indicator">
                {#if shouldRefresh}
                    {#if isRefreshing}
                        <div
                            class="absolute text-sm font-bold top-[50px] left-0 right-0 w-fit m-auto"
                        >
                            Loading...
                        </div>
                        <div
                            class="icon"
                            style="animation-play-state: running; animation-duration: 1s"
                        ></div>
                    {:else}
                        <div
                            class="absolute text-sm font-thin top-1 left-0 right-0 w-fit m-auto"
                        >
                            Release to Refresh
                            <RefreshCcwDot class="m-auto mt-1" />
                        </div>
                    {/if}
                {:else}
                    <div
                        class="absolute text-sm font-thin top-1 left-0 right-0 w-fit m-auto"
                    >
                        Pull to Refresh
                        <RefreshCcw class="m-auto mt-1" />
                    </div>
                {/if}
            </div>
        {/if}
        <div
            class="content-wrapper relative p-1{isLoading
                ? ' opacity-55 pointer-events-none'
                : ''}"
            style="transform: translateY({translateY}px); 
            background: rgb(247, 247, 247);"
        >
            <!-- Search -->
            <form class="pr-[5px] pl-[5px] pt-2 max-w-[400px] m-auto md:mb-2">
                <div class="flex gap-2">
                    <Label for="per-page-select" class="sr-only"
                        >Issues Per Page</Label
                    >
                    <Select
                        id="per-page-select"
                        underline
                        class="max-w-[108px]"
                        value={issuesPerPage.toString()}
                        onchange={(e) => {
                            issuesPerPage = Number.parseInt(
                                (e.target as HTMLSelectElement).value,
                            );
                            currentPage = 1;
                            loadPage(currentPage);
                        }}
                        items={[
                            { value: "1", name: "1 Per Page" },
                            { value: "5", name: "5 Per Page" },
                            { value: "10", name: "10 Per Page" },
                            { value: "15", name: "15 Per Page" },
                            { value: "20", name: "20 Per Page" },
                            { value: "25", name: "25 Per Page" },
                            { value: "30", name: "30 Per Page" },
                            { value: "35", name: "35 Per Page" },
                            { value: "40", name: "40 Per Page" },
                            { value: "45", name: "45 Per Page" },
                            { value: "50", name: "50 Per Page" },
                            { value: "55", name: "55 Per Page" },
                            { value: "60", name: "60 Per Page" },
                            { value: "65", name: "65 Per Page" },
                            { value: "70", name: "70 Per Page" },
                            { value: "75", name: "75 Per Page" },
                            { value: "80", name: "80 Per Page" },
                            { value: "85", name: "85 Per Page" },
                            { value: "90", name: "90 Per Page" },
                            { value: "95", name: "95 Per Page" },
                            { value: "100", name: "100 Per Page" },
                        ]}
                    />
                    <Search
                        size="md"
                        class="rounded-none py-2.5"
                        placeholder="Search Issues..."
                        bind:value={searchQuery}
                    >
                        <button
                            id="speech-btn"
                            type="button"
                            onclick={isListening
                                ? stopVoiceSearch
                                : startVoiceSearch}
                            class="outline-none{isListening ? ' text-red' : ''}"
                        >
                            <MicrophoneSolid class="w-5 h-5 me-2" />
                        </button>
                    </Search>
                    <Tooltip
                        id="speech-tip-tooltip"
                        class="z-20 max-w-[300px] w-full"
                        type="light"
                        triggeredBy="#speech-btn"
                        placement="bottom"
                        open={isListening}
                        >{t(
                            "Tip: You can trigger the following voice commands: 'Operable', 'Not Operable', 'Next Page', 'Previous Page', 'All Categories', 'Reported', 'In Progress', 'Waiting for parts', 'Ready for pickup', 'Back in service'",
                        )}</Tooltip
                    >
                </div>
                <div class="md:flex md:gap-2 md:justify-between">
                    <!-- Categories: -->
                    <div class="relative w-full md:w-fit">
                        <Button
                            class="category-select mt-2 whitespace-nowrap border w-full border-primary-700"
                            style="filter: invert({$darkModeEnabled
                                ? '1'
                                : '0'});"
                        >
                            <div class="flex items-center mt-0">
                                {#if selectedCategory.icon === "OctagonAlert"}
                                    <OctagonAlert class="h-5 w-5 mr-2" />
                                {:else if selectedCategory.icon === "Cog"}
                                    <Cog class="h-5 w-5 mr-2" />
                                {:else if selectedCategory.icon === "Loader"}
                                    <Loader class="h-5 w-5 mr-2" />
                                {:else if selectedCategory.icon === "KeyRound"}
                                    <KeyRound class="h-5 w-5 mr-2" />
                                {:else if selectedCategory.icon === "CircleCheckBig"}
                                    <CircleCheckBig class="h-5 w-5 mr-2" />
                                {/if}
                                <span class="font-semibold">
                                    {selectedCategory.label}
                                </span>
                            </div>
                            <ChevronDownOutline class="w-4 h-4 ms-1" />
                        </Button>
                        <Dropdown
                            triggeredBy=".category-select"
                            classContainer="w-80"
                            bind:open={searchDropdownOpen}
                        >
                            {#each search_categories as category, index}
                                <DropdownItem
                                    onclick={() => {
                                        selectedCategory = category;
                                        searchDropdownOpen = false;
                                        simulateLoadingWithFilters();
                                    }}
                                    class={selectedCategory.label ===
                                    category.label
                                        ? "underline"
                                        : ""}
                                >
                                    <div
                                        class="flex items-center mt-0"
                                        style="filter: invert({index > 0 &&
                                        $darkModeEnabled
                                            ? '1'
                                            : '0'});"
                                    >
                                        {#if category.icon === "OctagonAlert"}
                                            <OctagonAlert
                                                class="h-5 w-5 mr-2 text-{statuses[
                                                    category.label
                                                ].color}-600"
                                            />
                                        {:else if category.icon === "Cog"}
                                            <Cog
                                                class="h-5 w-5 mr-2 animate-spin-slow text-{statuses[
                                                    category.label
                                                ].color}-600"
                                            />
                                        {:else if category.icon === "Loader"}
                                            <Loader
                                                class="h-5 w-5 mr-2 animate-spin-slow text-{statuses[
                                                    category.label
                                                ].color}-600"
                                            />
                                        {:else if category.icon === "KeyRound"}
                                            <KeyRound
                                                class="h-5 w-5 mr-2 text-{statuses[
                                                    category.label
                                                ].color}-600"
                                            />
                                        {:else if category.icon === "CircleCheckBig"}
                                            <CircleCheckBig
                                                class="h-5 w-5 mr-2 text-{statuses[
                                                    category.label
                                                ].color}-600"
                                            />
                                        {/if}
                                        <span
                                            class="text-{category.color}-600 font-semibold"
                                        >
                                            {category.label}
                                        </span>
                                    </div>
                                </DropdownItem>
                            {/each}
                        </Dropdown>
                    </div>
                    <!-- Filter by Operable: -->
                    <div class="relative w-full md:w-fit">
                        <Button
                            class="filter-by-operable mt-2 whitespace-nowrap border w-full border-primary-700"
                            style="filter: invert({$darkModeEnabled
                                ? '1'
                                : '0'});"
                        >
                            <div class="flex items-center mt-0">
                                {#if selectedFilter.icon === "check"}
                                    <CheckOutline
                                        class="h-5 w-5 mr-2 text-green-500"
                                    />
                                {:else if selectedFilter.icon === "x"}
                                    <X class="h-5 w-5 mr-2 text-red-500" />
                                {/if}
                                <span class="font-semibold">
                                    {selectedFilter.label}
                                </span>
                            </div>
                            <ChevronDownOutline class="w-4 h-4 ms-1" />
                        </Button>
                        <Dropdown
                            triggeredBy=".filter-by-operable"
                            classContainer="w-80"
                            bind:open={filterDropdownOpen}
                        >
                            {#each filter_by_operable_categories as filter, index}
                                <DropdownItem
                                    onclick={() => {
                                        selectedFilter = filter;
                                        filterDropdownOpen = false;
                                        simulateLoadingWithFilters();
                                    }}
                                    class={selectedFilter.label === filter.label
                                        ? "underline"
                                        : ""}
                                >
                                    <div
                                        class="flex items-center mt-0"
                                        style="filter: invert({index > 0 &&
                                        $darkModeEnabled
                                            ? '1'
                                            : '0'});"
                                    >
                                        {#if filter.icon === "check"}
                                            <CheckOutline
                                                class="h-5 w-5 mr-2 text-green-500"
                                            />
                                        {:else if filter.icon === "x"}
                                            <X
                                                class="h-5 w-5 mr-2 text-red-500"
                                            />
                                        {/if}
                                        <span
                                            class="text-{filter.color}-600 font-semibold"
                                        >
                                            {filter.label}
                                        </span>
                                    </div>
                                </DropdownItem>
                            {/each}
                        </Dropdown>
                    </div>
                </div>
            </form>
            <!-- Page Buttons Top -->
            <div
                class="pt-2 flex justify-between p-2 pr-3 pl-3 items-center border-b md:border-none md:absolute top-0 left-0 right-0 z-[-1]"
            >
                {#if isLoading}
                    <div
                        class="icon big-loader"
                        style="animation-play-state: running; animation-duration: 1s"
                    ></div>
                {:else}
                    <span
                        class="inline-block text-center px-3 py-1 bg-gray-200 text-gray-700 text-sm font-medium border border-gray-300 rounded cursor-pointer hover:bg-gray-300 hover:text-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 active:bg-gray-400"
                        tabindex="0"
                        role="button"
                        onclick={handleSpecificPageChange}
                        onkeypress={(event) => {
                            if (event.key === "Enter" || event.key === " ") {
                                handleSpecificPageChange();
                            }
                        }}
                    >
                        {t("Page")}
                        {currentPage}
                        {t("of")}
                        {totalPages}
                        <br />
                        {$issues.length}
                        {t("Results")}
                        <br />
                        {Math.min(
                            issuesPerPage * (currentPage - 1) + 1,
                            totalIssuesCount,
                        )}{" "}
                        -{" "}
                        {Math.min(
                            issuesPerPage * currentPage,
                            totalIssuesCount,
                        )}{" "}
                        {t("of")}
                        {totalIssuesCount}
                    </span>
                {/if}
                <div class="flex gap-2">
                    <Button
                        onclick={() => changePage(false, "top")}
                        disabled={isLoading || currentPage === 1}
                        class="btn"
                        style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                    >
                        <ArrowLeft class="h-5 w-5" />
                    </Button>
                    <Button
                        onclick={() => changePage(true, "top")}
                        disabled={isLoading ||
                            currentPage * issuesPerPage >= totalIssuesCount}
                        class="btn"
                        style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                    >
                        <ArrowRight class="h-5 w-5" />
                    </Button>
                </div>
            </div>
            <!-- Issues Loop -->
            <div
                class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
            >
                {#if $issues}
                    {#each $issues as issue, issue_number}
                        <div
                            class="p-4 flex flex-col justify-between items-start issue-item select-none {editIssue ===
                            issue.id.toString()
                                ? 'bg-blue-50'
                                : 'relative bg-gray-100'} rounded-md border-b-4"
                            class:multiSelectMode
                            role="button"
                            tabindex="0"
                            onclick={() => toggleSelect(issue)}
                            style="max-height: fit-content;"
                            onkeypress={(event) => {
                                if (
                                    event.key === "Enter" ||
                                    event.key === " "
                                ) {
                                    toggleSelect(issue);
                                }
                            }}
                            onmousedown={startMultiSelect}
                            onmouseup={stopMultiSelect}
                            ontouchstart={startMultiSelect}
                            ontouchend={stopMultiSelect}
                        >
                            <div class="w-full">
                                <!-- ID Tag -->
                                {#if issue.gse_id}
                                    <div
                                        class="font-medium h-fit inline-flex items-center justify-center px-2.5 py-0.5 text-xs border bg-purple-100 text-purple-800 dark:bg-gray-700 dark:text-purple-400 border-purple-400 dark:border-purple-400 rounded"
                                        style="filter: invert({$darkModeEnabled
                                            ? '1'
                                            : '0'});"
                                        onclick={() => openDetailsDrawer(issue)}
                                        onkeypress={(event) => {
                                            if (
                                                event.key === "Enter" ||
                                                event.key === " "
                                            ) {
                                                openDetailsDrawer(issue);
                                            }
                                        }}
                                        role="button"
                                        tabindex="0"
                                    >
                                        {issue.gse_id}
                                    </div>
                                {/if}
                                <!-- Gate: -->
                                {#if issue.gate_type && issue.gate_name}
                                    <div
                                        class="flex absolute top-2 right-2 items-center bg-yellow-300 border-2 border-navy-800 rounded-md px-2 py-1 ml-3 text-navy-900 shadow-sm"
                                        style="width: fit-content; min-width: fit-content;filter: invert({$darkModeEnabled
                                            ? '1'
                                            : '0'});"
                                    >
                                        <!-- Airplane Icon -->
                                        <div
                                            class="flex-shrink-0 rounded-md bg-yellow-400 p-1"
                                        >
                                            <Plane
                                                class="h-3 w-3 text-navy-800"
                                            />
                                        </div>
                                        <!-- Gate Info -->
                                        <div
                                            class="ml-2 text-xs font-bold text-black"
                                        >
                                            <p>{issue.gate_type}</p>
                                            <p>{issue.gate_name}</p>
                                        </div>
                                    </div>
                                {/if}
                                <div class="flex gap-1 mt-2">
                                    <p class="text-sm font-bold">
                                        {t("Employee Name:")}
                                    </p>
                                    <p class="text-sm">{issue.name}</p>
                                </div>
                                <!-- Operable -->
                                <div class="text-sm flex items-center">
                                    <p class="text-sm font-bold">
                                        {t("Operable:")}
                                    </p>
                                    {#if issue.operable.toLowerCase() === "yes"}
                                        <CheckOutline
                                            class="ml-2 h-4 w-4 text-green-500"
                                            style="filter: invert({$darkModeEnabled
                                                ? '1'
                                                : '0'});"
                                        />
                                    {:else}
                                        <X
                                            class="ml-2 h-4 w-4 text-red-500"
                                            style="filter: invert({$darkModeEnabled
                                                ? '1'
                                                : '0'});"
                                        />
                                    {/if}
                                </div>
                                <!-- Description: -->
                                <p class="text-sm font-bold">
                                    {t("Issue Description:")}
                                </p>
                                <p class="text-sm max-w-[80%]">{issue.issue}</p>
                                <!-- Attachments: -->
                                {#if issue.attachments && issue.attachments.length > 0}
                                    <!-- Spacer -->
                                    <hr class="mb-2 mt-2 w-[80%] m-auto" />
                                    <div
                                        class="text-sm font-bold relative text-center m-auto w-fit"
                                    >
                                        <p
                                            class="text-sm font-bold text-gray-700 mb-1 ml-4"
                                        >
                                            {t("Issue Attachments:")}
                                        </p>
                                        <Indicator
                                            color="blue"
                                            border
                                            size="xl"
                                            placement="top-left"
                                            class="text-xs text-white font-bold"
                                            >{issue.attachments
                                                .length}</Indicator
                                        >
                                    </div>
                                    <div
                                        class="flex justify-center gap-3 mb-[25px] flex-wrap"
                                    >
                                        {#each issue.attachments as attachment}
                                            <Button
                                                class="relative text-sm max-w-[80%]"
                                                size="sm"
                                                onclick={() => {
                                                    if (
                                                        !$fullscreenVideo ||
                                                        !$fullscreenImage ||
                                                        !$fullscreenViewer
                                                    )
                                                        return;
                                                    $fullscreenViewer.classList.remove(
                                                        "hidden",
                                                    );
                                                    $fullscreenViewer.classList.add(
                                                        "flex",
                                                    );
                                                    isFullScreenMode.set(true);
                                                    const attachmentURL = `${BACKEND_URL}/api/media/attachment?id=${attachment.id}`;
                                                    if (
                                                        attachment.file_type.includes(
                                                            "image",
                                                        )
                                                    ) {
                                                        $fullscreenImage.src =
                                                            attachmentURL;
                                                        $fullscreenImage.classList.remove(
                                                            "hidden",
                                                        );
                                                        $fullscreenVideo.classList.add(
                                                            "hidden",
                                                        );
                                                    } else {
                                                        //if (attachment.file_type === "video") {
                                                        $fullscreenVideo.src =
                                                            attachmentURL;
                                                        $fullscreenVideo.classList.remove(
                                                            "hidden",
                                                        );
                                                        $fullscreenImage.classList.add(
                                                            "hidden",
                                                        );
                                                    }
                                                }}
                                            >
                                                {#if attachment.file_type.includes("image")}
                                                    <Image
                                                        class="text-white dark:text-white"
                                                    />
                                                {:else}
                                                    <Video
                                                        class="text-white dark:text-white"
                                                    />
                                                {/if}
                                                <span class="sr-only"
                                                    >{issue.attachments.length} Attachments</span
                                                >
                                            </Button>
                                        {/each}
                                    </div>
                                {/if}
                                <!-- Progress bar -->
                                <div class="mt-2 mb-1">
                                    <div class="relative">
                                        <div class="flex justify-between">
                                            <div
                                                class="text-sm font-bold relative left-0 top-[2px]{issue.status ===
                                                'Back in service'
                                                    ? ' hidden'
                                                    : ''}"
                                            >
                                                Estimated Time:
                                            </div>
                                            <span
                                                class="text-xs font-bold absolute right-0 top-[-20px] border-b pb-1{issue.status ===
                                                'Back in service'
                                                    ? ' hidden'
                                                    : ''}"
                                                >{issue.estimated_date
                                                    ? issue.estimated_date
                                                    : ""}</span
                                            >
                                            <span
                                                class="text-xs font-bold relative right-0 top-[3px]{issue.status ===
                                                'Back in service'
                                                    ? ' hidden'
                                                    : ''}"
                                                >{timeAgo[issue_number]
                                                    ? timeAgo[issue_number]
                                                    : "Calculating..."}</span
                                            >
                                        </div>
                                        <div class="flex">
                                            {#each statusKeys as status, index}
                                                <div
                                                    class={`flex-1 relative ${!(index === statusKeys.length - 1) ? "mr-1" : ""}`}
                                                >
                                                    <div
                                                        class={`h-3 transform skew-x-12 transition-all duration-300 ${
                                                            index ===
                                                                statusKeys.indexOf(
                                                                    issue.status,
                                                                ) ||
                                                            index <
                                                                statusKeys.indexOf(
                                                                    issue.status,
                                                                )
                                                                ? `bg-${statuses[status].color}-500`
                                                                : "bg-gray-200"
                                                        }`}
                                                        style="filter: invert({(index ===
                                                            statusKeys.indexOf(
                                                                issue.status,
                                                            ) ||
                                                            index <
                                                                statusKeys.indexOf(
                                                                    issue.status,
                                                                )) &&
                                                        $darkModeEnabled
                                                            ? '1'
                                                            : '0'});"
                                                    ></div>
                                                    <div
                                                        class="mt-4 flex flex-col items-center"
                                                    >
                                                        <div
                                                            id="issue-{issue.id}-icon-{index}"
                                                            class={`p-3 rounded-full transition-all duration-300 ${
                                                                index ===
                                                                    statusKeys.indexOf(
                                                                        issue.status,
                                                                    ) ||
                                                                index <
                                                                    statusKeys.indexOf(
                                                                        issue.status,
                                                                    )
                                                                    ? `bg-${statuses[status].color}-500 text-white`
                                                                    : "bg-gray-200 text-gray-500"
                                                            }`}
                                                            style="filter: invert({(index ===
                                                                statusKeys.indexOf(
                                                                    issue.status,
                                                                ) ||
                                                                index <
                                                                    statusKeys.indexOf(
                                                                        issue.status,
                                                                    )) &&
                                                            $darkModeEnabled
                                                                ? '1'
                                                                : '0'});"
                                                            onclick={() =>
                                                                changeIssueStatus(
                                                                    issue,
                                                                    status,
                                                                )}
                                                            onkeypress={(
                                                                event,
                                                            ) => {
                                                                if (
                                                                    event.key ===
                                                                        "Enter" ||
                                                                    event.key ===
                                                                        " "
                                                                ) {
                                                                    changeIssueStatus(
                                                                        issue,
                                                                        status,
                                                                    );
                                                                }
                                                            }}
                                                            tabindex="0"
                                                            role="button"
                                                        >
                                                            {#if statuses[status].icon === "OctagonAlert"}
                                                                <OctagonAlert
                                                                    class="h-5 w-5 mr-2-600"
                                                                />
                                                            {:else if statuses[status].icon === "Cog"}
                                                                <Cog
                                                                    class="h-5 w-5 mr-2-600"
                                                                />
                                                            {:else if statuses[status].icon === "Loader"}
                                                                <Loader
                                                                    class="h-5 w-5 mr-2-600"
                                                                />
                                                            {:else if statuses[status].icon === "KeyRound"}
                                                                <KeyRound
                                                                    class="h-5 w-5 mr-2-600"
                                                                />
                                                            {:else if statuses[status].icon === "CircleCheckBig"}
                                                                <CircleCheckBig
                                                                    class="h-5 w-5 mr-2-600"
                                                                />
                                                            {/if}
                                                        </div>
                                                        <Tooltip
                                                            class="z-20"
                                                            type="light"
                                                            triggeredBy="#issue-{issue.id}-icon-{index}"
                                                            placement="top"
                                                            trigger="click"
                                                            >{statuses[status]
                                                                .label}</Tooltip
                                                        >
                                                    </div>
                                                </div>
                                            {/each}
                                        </div>
                                        <div
                                            class="flex m-auto w-fit text-center items-center mt-2"
                                            style="filter: invert({$darkModeEnabled
                                                ? '1'
                                                : '0'});"
                                        >
                                            {#if statuses[issue.status].icon === "OctagonAlert"}
                                                <OctagonAlert
                                                    class="h-5 w-5 mr-2 text-{statuses[
                                                        issue.status
                                                    ].color}-600"
                                                />
                                            {:else if statuses[issue.status].icon === "Cog"}
                                                <Cog
                                                    class="h-5 w-5 mr-2 text-{statuses[
                                                        issue.status
                                                    ].color}-600"
                                                />
                                            {:else if statuses[issue.status].icon === "Loader"}
                                                <Loader
                                                    class="h-5 w-5 mr-2 text-{statuses[
                                                        issue.status
                                                    ].color}-600"
                                                />
                                            {:else if statuses[issue.status].icon === "KeyRound"}
                                                <KeyRound
                                                    class="h-5 w-5 mr-2 text-{statuses[
                                                        issue.status
                                                    ].color}-600"
                                                />
                                            {:else if statuses[issue.status].icon === "CircleCheckBig"}
                                                <CircleCheckBig
                                                    class="h-5 w-5 mr-2 text-{statuses[
                                                        issue.status
                                                    ].color}-600"
                                                />
                                            {/if}
                                            <span
                                                class={`text-lg font-semibold text-${statusKeys.indexOf(issue.status) >= 0 ? statuses[issue.status].color : "gray"}-500`}
                                            >
                                                {statuses[issue.status].label} -
                                                {calculateProgress(
                                                    statusKeys.indexOf(
                                                        issue.status,
                                                    ),
                                                    statusKeys.length,
                                                )}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="w-full">
                                <!-- Spacer -->
                                <hr class="mb-2 mt-2 w-[80%] m-auto" />
                                <!-- Date Picker -->
                                {#if issue.status !== "Back in service" && editIssue === issue.id.toString()}
                                    <div class="flex justify-between mb-1 p-2">
                                        <Button
                                            class="bg-green-600 hover:bg-green-800"
                                            onclick={(event: Event) => {
                                                issues.set(
                                                    $issues.map(
                                                        (single_issue) => {
                                                            if (
                                                                issue.id ===
                                                                single_issue.id
                                                            ) {
                                                                single_issue.estimated_date =
                                                                    new Date().toLocaleDateString();
                                                            }
                                                            return single_issue;
                                                        },
                                                    ),
                                                );
                                                editIssue = "";
                                                requestAnimationFrame(() => {
                                                    editIssue =
                                                        issue.id.toString();
                                                });
                                            }}
                                            style="filter: invert({$darkModeEnabled
                                                ? '1'
                                                : '0'});"
                                        >
                                            <Clock class="h-5 w-5 mr-2" />
                                            Today
                                        </Button>
                                        <Button
                                            class="bg-red-600 hover:bg-red-800"
                                            onclick={(event: Event) => {
                                                issues.set(
                                                    $issues.map(
                                                        (single_issue) => {
                                                            if (
                                                                issue.id ===
                                                                single_issue.id
                                                            ) {
                                                                single_issue.estimated_date =
                                                                    undefined;
                                                            }
                                                            return single_issue;
                                                        },
                                                    ),
                                                );
                                                editIssue = "";
                                                requestAnimationFrame(() => {
                                                    editIssue =
                                                        issue.id.toString();
                                                });
                                            }}
                                            style="filter: invert({$darkModeEnabled
                                                ? '1'
                                                : '0'});"
                                        >
                                            <X class="h-5 w-5 mr-2" />
                                            Clear
                                        </Button>
                                    </div>
                                    <div
                                        class="text-black mb-2 flex date-picker"
                                    >
                                        <Datepicker
                                            inline
                                            autohide={false}
                                            value={issue.estimated_date
                                                ? new Date(issue.estimated_date)
                                                : undefined}
                                            on:clear={() => {}}
                                            on:select={(event) => {
                                                issues.set(
                                                    $issues.map(
                                                        (single_issue) => {
                                                            if (
                                                                issue.id ===
                                                                single_issue.id
                                                            ) {
                                                                single_issue.estimated_date =
                                                                    event.detail
                                                                        ? event.detail.toLocaleDateString()
                                                                        : undefined;
                                                            }
                                                            return single_issue;
                                                        },
                                                    ),
                                                );
                                            }}
                                            on:apply={(event) => {
                                                issues.set(
                                                    $issues.map(
                                                        (single_issue) => {
                                                            if (
                                                                issue.id ===
                                                                single_issue.id
                                                            ) {
                                                                single_issue.estimated_date =
                                                                    event.detail
                                                                        ? event.detail.toLocaleDateString()
                                                                        : undefined;
                                                            }
                                                            return single_issue;
                                                        },
                                                    ),
                                                );
                                                console.warn("WIP tell server");
                                                editIssue = "";
                                            }}
                                            color="blue"
                                            dateFormat={{
                                                year: "numeric",
                                                month: "short",
                                                day: "2-digit",
                                            }}
                                        />
                                    </div>
                                {/if}
                                <Button
                                    class="bg-blue-600 w-full"
                                    onclick={(event: Event) =>
                                        handleEdit(event, issue)}
                                    style="filter: invert({$darkModeEnabled
                                        ? '1'
                                        : '0'});"
                                >
                                    <Edit class="h-5 w-5 mr-2" />
                                    {#if editIssue === issue.id.toString()}
                                        Exit Edit Mode
                                    {:else}
                                        Edit
                                    {/if}
                                </Button>
                                <Button
                                    class="bg-green-600 hover:bg-green-800 w-full mt-2"
                                    onclick={(event: Event) => {
                                        leaveCommentDrawerHidden = false;
                                    }}
                                    style="filter: invert({$darkModeEnabled
                                        ? '1'
                                        : '0'});"
                                >
                                    <EnvelopeOpenOutline class="h-5 w-5 mr-2" />
                                    Comment
                                </Button>
                                {#if issue.status === "Back in service"}
                                    <Button
                                        class="bg-red-600 hover:bg-red-800 w-full mt-2"
                                        onclick={(event: Event) =>
                                            handleDelete(event, issue)}
                                        style="filter: invert({$darkModeEnabled
                                            ? '1'
                                            : '0'});"
                                    >
                                        <Trash2 class="h-5 w-5 mr-2" />
                                        Close Case
                                    </Button>
                                {/if}
                                <div
                                    class="text-xs text-center font-bold text-gray-500 m-auto mt-2 w-fit"
                                >
                                    {t("Reported at")}
                                    {issue.reported_at
                                        ? new Date(
                                              issue.reported_at,
                                          ).toLocaleDateString() +
                                          " - " +
                                          new Date(
                                              issue.reported_at,
                                          ).toLocaleTimeString()
                                        : ""}
                                </div>
                            </div>
                        </div>
                    {/each}
                {/if}
            </div>
            <!-- Page Buttons Bottom -->
            <div
                class="mt-4 flex justify-between p-5 pr-3 pl-3 pt-0 items-center{!isLoading &&
                $issues.length > 2
                    ? ''
                    : ' hidden'}"
            >
                <span
                    class="inline-block text-center px-3 py-1 bg-gray-200 text-gray-700 text-sm font-medium border border-gray-300 rounded cursor-pointer hover:bg-gray-300 hover:text-gray-800 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 active:bg-gray-400"
                    tabindex="0"
                    role="button"
                    onclick={handleSpecificPageChange}
                    onkeypress={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                            handleSpecificPageChange();
                        }
                    }}
                >
                    {t("Page")}
                    {currentPage}
                    {t("of")}
                    {totalPages}
                    <br />
                    {$issues.length}
                    {t("Results")}
                    <br />
                    {Math.min(
                        issuesPerPage * (currentPage - 1) + 1,
                        totalIssuesCount,
                    )}{" "}
                    -{" "}
                    {Math.min(
                        issuesPerPage * currentPage,
                        totalIssuesCount,
                    )}{" "}
                    {t("of")}
                    {totalIssuesCount}
                </span>
                <div class="flex gap-2">
                    <Button
                        onclick={() => changePage(false, "bottom")}
                        disabled={isLoading || currentPage === 1}
                        class="btn"
                        style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                    >
                        <ArrowLeft class="h-5 w-5" />
                    </Button>
                    <Button
                        onclick={() => changePage(true, "bottom")}
                        disabled={isLoading ||
                            currentPage * issuesPerPage >= totalIssuesCount}
                        class="btn"
                        style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                    >
                        <ArrowRight class="h-5 w-5" />
                    </Button>
                </div>
            </div>
        </div>
    </div>
</Drawer>

<style>
    /*
    .issue-item.multiSelectMode {
        background-color: rgba(0, 123, 255, 0.1);
    }
    .issue-item:active,
    .issue-item.active {
        background-color: rgba(0, 123, 255, 0.3);
    }
    */
    .btn {
        transition: background-color 0.3s;
    }
    .btn:disabled {
        background-color: #e5e7eb;
        cursor: not-allowed;
        pointer-events: none;
    }
    .btn:hover:not(:disabled) {
        background-color: #e5e7eb;
    }

    .scroll_up {
        position: fixed;
        left: 1rem;
        bottom: 1rem;
        cursor: pointer;
        color: #999;
        border-radius: 0.15rem;
        transition-duration: 300ms;
        z-index: 999;
        background: none;
        border: none;
        padding: 0;
    }
    .scroll_up:hover {
        transform: translateY(-10px);
    }

    .indicator {
        left: 0;
        position: fixed;
        right: 0;
        top: 75px;
    }

    .icon {
        animation: spin 1s linear infinite;
        border: 2px solid transparent;
        border-radius: 50%;
        border-top-color: #0087ff;
        height: 35px;
        width: 35px;
        margin: auto;
    }

    .big-loader {
        height: 70px !important;
        width: 70px !important;
        margin: 0 !important;
    }

    .content-wrapper {
        background-color: #fff;
        transition: transform 0.5s cubic-bezier(0.2, 0.8, 0.2, 1);
    }

    @keyframes spin {
        100% {
            transform: rotate(360deg);
        }
    }
</style>
