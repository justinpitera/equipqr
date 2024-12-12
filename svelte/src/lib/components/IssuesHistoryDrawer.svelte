<script lang="ts">
    import {
        Button,
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
    import { DEBUG_MODE } from "$lib/config";
    import { delete_issue, getIssues } from "$lib/helpers/server-requests";
    import { gate_types } from "$lib/helpers/report-ui-store";
    import { sineIn } from "svelte/easing";
    import { notify } from "$lib/helpers/notify";
    const { selectedLanguage, isIssuesHistoryHidden, darkModeEnabled } =
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
        Reported: { label: "Reported", color: "red", icon: "OctagonAlert" },
        "In Progress": { label: "In Progress", color: "blue", icon: "Cog" },
        "Waiting for Spare Parts": {
            label: "Waiting for Spare Parts",
            color: "yellow",
            icon: "Loader",
        },
        "Ready for Pickup": {
            label: "Ready for Pickup",
            color: "purple",
            icon: "KeyRound",
        },
        "Back in Service": {
            label: "Back in Service",
            color: "green",
            icon: "CircleCheckBig",
        },
    };
    const statusKeys = Object.keys(statuses);

    type Status = keyof typeof statuses;

    let issuesScroller: HTMLElement;
    let issues: HistoryIssue[] = $state([]);
    let currentPage = $state(1);
    let totalPages = $state(1); // Math.ceil(issues.length / issuesPerPage)
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
        issuesPerPage = 10;
        totalPages = 1;
        pulling = false;
        rotateDeg = 0;
        shouldRefresh = false;
        isRefreshing = false;
        translateY = 0;
        issues = [];
        currentPage = 1;
        isLoading = false;
        showScrollUp = false;
        multiSelectMode = false;
    }

    function generateIssues(count: number): HistoryIssue[] {
        const randomNames = ["John", "Jane", "Alex", "Chris", "Taylor"];
        const randomIssues = [
            "Broken screen",
            "Battery not charging",
            "Overheating",
            "Software crash",
            "Unresponsive buttons",
            "Broken screen Broken screen Broken screen Broken screen",
            "Battery not charging Battery not charging Battery not charging Battery not charging Battery not charging",
        ];
        const randomGSEIDs = [
            "AH 10001",
            "CH 20005",
            "BH 50006",
            "DH 40004",
            "RH 60003",
        ];
        const randomStatuses = Object.keys(statuses) as Status[];

        return Array.from({ length: count }, (_, i) => {
            const operable = Math.random() > 0.5 ? "Yes" : "No";
            const show_gate = operable === "No";
            const gate_keys = show_gate ? Object.keys(gate_types) : [];
            const selected_gate_type = show_gate
                ? gate_keys[Math.floor(Math.random() * gate_keys.length)]
                : "";
            return {
                id: (i + 1).toString(),
                gse_id: randomGSEIDs[
                    Math.floor(Math.random() * randomGSEIDs.length)
                ],
                name: randomNames[
                    Math.floor(Math.random() * randomNames.length)
                ],
                issue: randomIssues[
                    Math.floor(Math.random() * randomIssues.length)
                ],
                operable,
                estimated_date:
                    Math.random() * 1000 > 500
                        ? new Date(Date.now() - 78000).toLocaleDateString()
                        : undefined,
                gate_type: show_gate ? selected_gate_type : undefined,
                gate_name: show_gate
                    ? gate_types[selected_gate_type][
                          Math.floor(
                              Math.random() *
                                  gate_types[selected_gate_type].length,
                          )
                      ]
                    : undefined,
                status: randomStatuses[
                    Math.floor(Math.random() * randomStatuses.length)
                ],
            };
        });
    }

    async function loadPage(page?: number) {
        const returned_issues = await getIssues(
            () => {
                isLoading = true;
            },
            () => {
                isLoading = false;
            },
        );
        console.log("returned_issues", returned_issues);
        if (returned_issues?.data && returned_issues.data.length > 0) {
            issuesPerPage = returned_issues.page_size;
            currentPage = returned_issues.page;
            totalPages = Math.ceil(returned_issues.total / issuesPerPage);
            issues = returned_issues.data.map((returned_issue) => {
                return {
                    id: returned_issue.id, //number
                    gse_id: returned_issue.gse_id, //string
                    name: returned_issue.reported_by || "", //string
                    issue: returned_issue.issue_description, //string
                    operable: "Yes", //returned_issue.operable,//string
                    status: "Reported", //returned_issue.status//string
                    estimated_date: returned_issue.reported_at
                        ? new Date(
                              returned_issue.reported_at,
                          ).toLocaleDateString()
                        : undefined, //string
                    // gate_type: returned_issue.gate_type ? returned_issue.gate_type : undefined, //string
                    // gate_name: returned_issue.gate_name ? returned_issue.gate_name : undefined, //string
                } as HistoryIssue;
            });
        } else {
            issues = generateIssues(44);
            notify(
                "Warning",
                "Could not find any past incidents, try again later...",
                "warning",
            );
        }
        isLoading = false;
        return issues;
    }

    function simulateLoadingWithFilters() {
        isLoading = true;
        setTimeout(() => {
            issues = generateIssues(44);
            if (selectedFilter.label !== "Operable/Not Operable") {
                if (selectedFilter.label === "Operable") {
                    issues = issues.filter((issue) => issue.operable === "Yes");
                } else if (selectedFilter.label === "Not Operable") {
                    issues = issues.filter((issue) => issue.operable === "No");
                }
            }
            if (selectedCategory.label !== "All categories") {
                issues = issues.filter(
                    (issue) => issue.status === selectedCategory.label,
                );
            }
            isLoading = false;
        }, 1200);
    }

    $effect(() => {
        if (!$isIssuesHistoryHidden) loadPage();
    });

    loadPage();
    let deleteIssuePopup = $state(false);
    let leaveCommentDrawerHidden = $state(true);
    let transitionParams = {
        x: -320,
        duration: 200,
        easing: sineIn,
    };

    async function changePage(next: boolean) {
        if (isLoading) return;
        setTimeout(() => {
            issuesScroller.scrollTo({ top: 0, behavior: "instant" });
        }, 100);
        isLoading = true;
        const totalPages = Math.ceil(issues.length / issuesPerPage);
        if (next) {
            currentPage = Math.min(totalPages, currentPage + 1);
        } else {
            currentPage = Math.max(1, currentPage - 1);
        }
    }

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
            for (const issue of issues) {
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
    bind:hidden={leaveCommentDrawerHidden}
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
    class="p-6 md:p-8 bg-white rounded-lg shadow-lg overflow-y-hidden"
    width="w-full"
    activateClickOutside={false}
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
                    issues = issues.filter(
                        (single_issue) =>
                            single_issue.id.toString() !==
                            delete_issue_id_confirm,
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

    <div class="flex items-center justify-between border-b">
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
            {t("Issues History")}
        </h2>
    </div>

    {#if showScrollUp}
        <button
            onclick={() => {
                issuesScroller.scrollTo({ top: 0, behavior: "smooth" });
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
                console.log("refreshing...");
                isRefreshing = true;
                await new Promise((res) => setTimeout(res, 800));
                setTimeout(() => {
                    translateY = 0;
                    pulling = false;
                    shouldRefresh = false;
                    console.log("refreshed...");
                    isRefreshing = false;
                }, 800);
            } else {
                translateY = 0;
                pulling = false;
                shouldRefresh = false;
            }
        }}
        class="refresher overflow-y-auto"
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
            class="content-wrapper{isLoading
                ? ' opacity-55 pointer-events-none'
                : ''}"
            style="transform: translateY({translateY}px);"
        >
            <!-- Search -->

            <form class="pr-[5px] pt-2">
                <Search
                    size="md"
                    class="rounded-none py-2.5"
                    placeholder="Search Issues..."
                    bind:value={searchQuery}
                >
                    <button
                        type="button"
                        onclick={isListening
                            ? stopVoiceSearch
                            : startVoiceSearch}
                        class="outline-none"
                    >
                        <MicrophoneSolid class="w-5 h-5 me-2" />
                    </button>
                </Search>
                <!-- Categories: -->
                <div class="relative w-full">
                    <Button
                        class="mt-2 whitespace-nowrap border w-full border-primary-700"
                        style="filter: invert({$darkModeEnabled ? '1' : '0'});"
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
                                class={selectedCategory.label === category.label
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
                <div class="relative w-full">
                    <Button
                        class="mt-2 whitespace-nowrap border w-full border-primary-700"
                        style="filter: invert({$darkModeEnabled ? '1' : '0'});"
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
                                        <X class="h-5 w-5 mr-2 text-red-500" />
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
            </form>
            <!-- Page Buttons Top -->
            <div
                class="pt-4 flex justify-between p-5 pr-3 pl-3 items-center border-b"
            >
                <span class="text-sm text-gray-500">
                    {#if issues.length > 0}
                        Page {currentPage} of {totalPages}
                        <br />
                        Results: {issues.length}
                    {/if}
                </span>
                {#if isLoading}
                    <div
                        class="icon"
                        style="animation-play-state: running; animation-duration: 1s"
                    ></div>
                {/if}
                <div class="flex gap-2">
                    <Button
                        onclick={() => changePage(false)}
                        disabled={isLoading || currentPage === 1}
                        class="btn"
                        style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                    >
                        <ArrowLeft class="h-5 w-5" />
                    </Button>
                    <Button
                        onclick={() => changePage(true)}
                        disabled={isLoading ||
                            currentPage * issuesPerPage >= issues.length}
                        class="btn"
                        style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                    >
                        <ArrowRight class="h-5 w-5" />
                    </Button>
                </div>
            </div>
            <!-- Issues Loop -->
            {#await loadPage(currentPage) then rows}
                {#each rows as issue, issue_number}
                    <div
                        class="p-4 border-b justify-between items-start issue-item relative select-none"
                        class:multiSelectMode
                        role="button"
                        tabindex="0"
                        onclick={() => toggleSelect(issue)}
                        onkeypress={() => toggleSelect(issue)}
                        onmousedown={startMultiSelect}
                        onmouseup={stopMultiSelect}
                        ontouchstart={startMultiSelect}
                        ontouchend={stopMultiSelect}
                    >
                        <!-- ID Tag -->
                        {#if issue.gse_id}
                            <div
                                class="font-medium h-fit inline-flex items-center justify-center px-2.5 py-0.5 text-xs border bg-purple-100 text-purple-800 dark:bg-gray-700 dark:text-purple-400 border-purple-400 dark:border-purple-400 rounded"
                                style="filter: invert({$darkModeEnabled
                                    ? '1'
                                    : '0'});"
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
                                    <Plane class="h-3 w-3 text-navy-800" />
                                </div>
                                <!-- Gate Info -->
                                <div class="ml-2 text-xs font-bold text-black">
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
                            <p class="text-sm font-bold">{t("Operable:")}</p>
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
                        <!-- Status -->
                        <div class="flex items-center mt-0"></div>
                        <!-- Progress bar -->
                        <div class="mt-2 mb-1">
                            <div class="relative">
                                <div class="flex justify-between">
                                    <div
                                        class="text-sm font-bold relative left-0 top-[2px]"
                                    >
                                        Estimated Time:
                                    </div>
                                    <span
                                        class="text-xs font-bold absolute right-0 top-[-20px] border-b pb-1"
                                        >{issue.estimated_date
                                            ? issue.estimated_date
                                            : ""}</span
                                    >
                                    <span
                                        class="text-xs font-bold relative right-0 top-[3px]"
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
                                                    onclick={() => {
                                                        if (
                                                            editIssue !==
                                                            issue.id.toString()
                                                        )
                                                            return;
                                                        issues = issues.map(
                                                            (single_issue) => {
                                                                if (
                                                                    issue.id ===
                                                                    single_issue.id
                                                                ) {
                                                                    single_issue.status =
                                                                        status;
                                                                }
                                                                return single_issue;
                                                            },
                                                        );
                                                        console.warn(
                                                            "WIP tell server",
                                                        );
                                                    }}
                                                    onkeypress={() => {}}
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
                                        {statuses[issue.status].label} - {calculateProgress(
                                            statusKeys.indexOf(issue.status),
                                            statusKeys.length,
                                        )}%
                                    </span>
                                </div>
                            </div>
                        </div>
                        <!-- Spacer -->
                        <hr class="mb-2 mt-2 w-[80%] m-auto" />
                        <!-- Edit Delete -->
                        {#if editIssue === issue.id.toString()}
                            <div class="text-black mb-2 issue date-picker">
                                <Datepicker
                                    inline
                                    showActionButtons
                                    autohide={false}
                                    on:clear={() => {}}
                                    on:apply={(event) => {
                                        issues = issues.map((single_issue) => {
                                            if (issue.id === single_issue.id) {
                                                single_issue.estimated_date =
                                                    event.detail
                                                        ? event.detail.toLocaleDateString()
                                                        : undefined;
                                            }
                                            return single_issue;
                                        });
                                        console.warn("WIP tell server");
                                        editIssue = "";
                                    }}
                                    on:click={(event) => {
                                        console.log(event.target);
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
                        <div class="flex gap-2">
                            <Button
                                class="bg-blue-600 w-full"
                                onclick={(event: Event) =>
                                    handleEdit(event, issue)}
                                style="filter: invert({$darkModeEnabled
                                    ? '1'
                                    : '0'});"
                            >
                                <Edit class="h-5 w-5 mr-2" />
                                Edit
                            </Button>
                            <Button
                                class="bg-red-600 hover:bg-red-800 w-full"
                                onclick={(event: Event) =>
                                    handleDelete(event, issue)}
                                style="filter: invert({$darkModeEnabled
                                    ? '1'
                                    : '0'});"
                            >
                                <Trash2 class="h-5 w-5 mr-2" />
                                Close Case
                            </Button>
                        </div>
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
                            Leave a Comment
                        </Button>
                    </div>
                {/each}
            {:catch}
                <p>Could not load the next page...</p>
            {/await}
            <!-- Page Buttons Bottom -->
            <div
                class="mt-8 flex justify-between p-5 pr-3 pl-3 pt-0 items-center{!isLoading && issues.length >
                5
                    ? ''
                    : ' hidden'}"
            >
                <span class="text-sm text-gray-500">
                    Page {currentPage} of {totalPages}
                    <br />
                    Results: {issues.length}
                </span>
                <div class="flex gap-2">
                    <Button
                        onclick={() => changePage(false)}
                        disabled={isLoading || currentPage === 1}
                        class="btn"
                        style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                    >
                        <ArrowLeft class="h-5 w-5" />
                    </Button>
                    <Button
                        onclick={() => changePage(true)}
                        disabled={isLoading ||
                            currentPage * issuesPerPage >= issues.length}
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
    .refresher {
        height: calc(100vh - 24px - 40px - 24px);
        background-position: 70%;
        position: relative;
        background: rgb(240, 240, 240);
        background: linear-gradient(
            180deg,
            rgba(240, 240, 240, 1) 0%,
            rgba(224, 224, 224, 1) 13%,
            rgba(255, 255, 255, 1) 100%
        );
        opacity: 0.8;
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
        margin: auto;
        width: 35px;
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
