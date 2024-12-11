<script lang="ts">
    import {
        Button,
        Drawer,
        Dropdown,
        DropdownItem,
        Search,
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
    } from "lucide-svelte";
    import { homePageStore } from "$lib/helpers/homepage";
    import { langChecker, translations } from "$lib/locales";
    import {
        CheckOutline,
        ChevronDownOutline,
        MicrophoneSolid,
    } from "flowbite-svelte-icons";
    import { onDestroy } from "svelte";
    import { DEBUG_MODE } from "$lib/config";
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
    const issuesPerPage = 50;
    let isLoading = $state(false);
    let multiSelectMode = $state(false);
    let showScrollUp = $state(false);
    let searchDropdownOpen = $state(false);
    let clickTimer: NodeJS.Timeout | undefined;

    const search_categories: {
        label: string;
        icon?: string;
        color?: string;
    }[] = [
        {
            label: "All categories",
        },
    ];
    for (const status in statuses) {
        search_categories.push({
            label: statuses[status].label,
            icon: statuses[status].icon,
            color: statuses[status].color,
        });
    }

    let selectCategory = $state(search_categories[0]);
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
        selectCategory = search_categories[0];
        searchQuery = "";
        searchDropdownOpen = false;
        isListening = false;
        startY = 0;
        currentY = 0;
        pulling = false;
        rotateDeg = 0;
        shouldRefresh = false;
        isRefreshing = false;
        translateY = 0;
        issues = [];
        currentPage = 1;
        isLoading = false;
        multiSelectMode = false;
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
        ];
        const randomGSEIDs = [
            "AH 10001",
            "CH 20005",
            "BH 50006",
            "DH 40004",
            "RH 60003",
        ];
        const randomStatuses = Object.keys(statuses) as Status[];

        return Array.from({ length: count }, (_, i) => ({
            id: i + 1,
            gse_id: randomGSEIDs[
                Math.floor(Math.random() * randomGSEIDs.length)
            ],
            name: randomNames[Math.floor(Math.random() * randomNames.length)],
            issue: randomIssues[
                Math.floor(Math.random() * randomIssues.length)
            ],
            operable: Math.random() > 0.5 ? "Yes" : "No",
            files: [],
            status: randomStatuses[
                Math.floor(Math.random() * randomStatuses.length)
            ],
        }));
    }

    $effect(() => {
        if ($isIssuesHistoryHidden) {
            isLoading = true;
            setTimeout(() => {
                issues = generateIssues(150);
                isLoading = false;
            }, 1200);
        }
    });

    function getIssuesForPage(page: number) {
        const start = (page - 1) * issuesPerPage;
        const end = page * issuesPerPage;
        return issues.slice(start, end);
    }

    async function changePage(next: boolean) {
        if (isLoading) return;
        setTimeout(() => {
            issuesScroller.scrollTo({ top: 0, behavior: "instant" });
        }, 100);
        isLoading = true;
        await new Promise((res) => setTimeout(res, 400));
        isLoading = false;
        const totalPages = Math.ceil(issues.length / issuesPerPage);
        if (next) {
            currentPage = Math.min(totalPages, currentPage + 1);
        } else {
            currentPage = Math.max(1, currentPage - 1);
        }
    }

    function toggleSelect(issue: HistoryIssue) {
        console.log("Viewing issue details:", issue);
    }

    function startMultiSelect() {
        clickTimer = setTimeout(() => {
            multiSelectMode = true;
        }, 800);
    }

    function stopMultiSelect() {
        if (clickTimer) {
            clickTimer = undefined;
            clearTimeout(clickTimer);
            multiSelectMode = false;
        }
    }

    function handleDelete(event: Event, issue: HistoryIssue) {
        event.stopPropagation();
        console.log("Delete Issue", issue);
    }

    function handleEdit(event: Event, issue: HistoryIssue) {
        event.stopPropagation();
        console.log("Edit Issue", issue);
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

    onDestroy(() => {
        resetDrawer();
        stopVoiceSearch();
        if (!DEBUG_MODE) isIssuesHistoryHidden.set(true);
    });
    issues = generateIssues(150);
</script>

<Drawer
    id="issue-history-drawer"
    placement="right"
    bind:hidden={$isIssuesHistoryHidden}
    backdrop={true}
    class="p-6 md:p-8 bg-white rounded-lg shadow-lg overflow-y-hidden"
    width="w-full"
    activateClickOutside={false}
>
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
        <h2 class="text-xl font-bold text-gray-800">{t("Issues History")}</h2>
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

            <form class="pr-[5px] pt-3">
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
                <div class="relative w-full">
                    <Button
                        class="mt-2 whitespace-nowrap border w-full border-primary-700"
                    >
                        <div class="flex items-center mt-0">
                            {#if selectCategory.icon === "OctagonAlert"}
                                <OctagonAlert class="h-5 w-5 mr-2" />
                            {:else if selectCategory.icon === "Cog"}
                                <Cog class="h-5 w-5 mr-2" />
                            {:else if selectCategory.icon === "Loader"}
                                <Loader class="h-5 w-5 mr-2" />
                            {:else if selectCategory.icon === "KeyRound"}
                                <KeyRound class="h-5 w-5 mr-2" />
                            {:else if selectCategory.icon === "CircleCheckBig"}
                                <CircleCheckBig class="h-5 w-5 mr-2" />
                            {/if}
                            <span class="font-semibold">
                                {selectCategory.label}
                            </span>
                        </div>
                        <ChevronDownOutline class="w-4 h-4 ms-1" />
                    </Button>
                    <Dropdown
                        classContainer="w-80"
                        bind:open={searchDropdownOpen}
                    >
                        {#each search_categories as category}
                            <DropdownItem
                                onclick={() => {
                                    selectCategory = category;
                                    searchDropdownOpen = false;
                                }}
                                class={selectCategory.label === category.label
                                    ? "underline"
                                    : ""}
                            >
                                <div class="flex items-center mt-0">
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
            </form>
            <!-- Page Buttons Top -->
            <div
                class="pt-4 flex justify-between p-5 pr-3 pl-3 items-center border-b"
            >
                <span class="text-sm text-gray-500">
                    {#if issues.length > 0}
                        Page {currentPage} of {Math.ceil(
                            issues.length / issuesPerPage,
                        )}
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
                    >
                        <ArrowLeft class="h-5 w-5" />
                    </Button>
                    <Button
                        onclick={() => changePage(true)}
                        disabled={isLoading ||
                            currentPage * issuesPerPage >= issues.length}
                        class="btn"
                    >
                        <ArrowRight class="h-5 w-5" />
                    </Button>
                </div>
            </div>
            <!-- Issues Loop -->
            {#each getIssuesForPage(currentPage) as issue}
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
                    <div class="flex justify-between">
                        <h3 class="text-lg font-semibold">{issue.name}</h3>
                        {#if issue.gse_id}
                            <div
                                class="font-medium relative top-8 right-[-5px] inline-flex items-center justify-center px-2.5 py-0.5 text-xs border bg-purple-100 text-purple-800 dark:bg-gray-700 dark:text-purple-400 border-purple-400 dark:border-purple-400 rounded"
                                style="filter: invert({$darkModeEnabled
                                    ? '1'
                                    : '0'});"
                            >
                                {issue.gse_id}
                            </div>
                        {/if}
                    </div>
                    <p class="text-gray-600">{issue.issue}</p>
                    <p class="text-sm text-gray-500 flex items-center">
                        {t("Operable:")}
                        {#if issue.operable.toLowerCase() === "yes"}
                            <CheckOutline class="ml-2 h-4 w-4 text-green-500" />
                        {:else}
                            <X class="ml-2 h-4 w-4 text-red-500" />
                        {/if}
                    </p>
                    <!-- Status -->
                    <div class="flex items-center mt-0"></div>
                    <!-- Progress bar -->
                    <div class="mt-2 mb-1">
                        <div class="relative">
                            <div
                                class="flex m-auto w-fit text-center items-center mb-2"
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
                                        ></div>
                                        <div
                                            class="mt-4 flex flex-col items-center"
                                        >
                                            <div
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
                                            <span
                                                class={`mt-2 text-sm font-medium text-center transition-all duration-300 ${
                                                    index ===
                                                        statusKeys.indexOf(
                                                            issue.status,
                                                        ) ||
                                                    index <
                                                        statusKeys.indexOf(
                                                            issue.status,
                                                        )
                                                        ? `text-${statuses[status].color}-500`
                                                        : "text-gray-500"
                                                }`}
                                            >
                                                {statuses[status].label}
                                            </span>
                                        </div>
                                    </div>
                                {/each}
                            </div>
                        </div>
                    </div>
                    <!-- Edit Delete -->
                    <div class="flex gap-2 absolute top-4 right-2">
                        <button
                            class="text-blue-600"
                            onclick={(event) => handleEdit(event, issue)}
                        >
                            <Edit class="h-5 w-5" />
                        </button>
                        <button
                            class="text-red-600"
                            onclick={(event) => handleDelete(event, issue)}
                        >
                            <Trash2 class="h-5 w-5" />
                        </button>
                    </div>
                </div>
            {/each}
            <!-- Page Buttons Bottom -->
            <div
                class="mt-8 flex justify-between p-5 pr-3 pl-3 pt-0 items-center{issues.length >
                5
                    ? ''
                    : ' hidden'}"
            >
                <span class="text-sm text-gray-500">
                    Page {currentPage} of {Math.ceil(
                        issues.length / issuesPerPage,
                    )}
                </span>
                <div class="flex gap-2">
                    <Button
                        onclick={() => changePage(false)}
                        disabled={isLoading || currentPage === 1}
                        class="btn"
                    >
                        <ArrowLeft class="h-5 w-5" />
                    </Button>
                    <Button
                        onclick={() => changePage(true)}
                        disabled={isLoading ||
                            currentPage * issuesPerPage >= issues.length}
                        class="btn"
                    >
                        <ArrowRight class="h-5 w-5" />
                    </Button>
                </div>
            </div>
        </div>
    </div>
</Drawer>

<style>
    .issue-item.multiSelectMode {
        background-color: rgba(0, 123, 255, 0.1);
    }
    .issue-item:active,
    .issue-item.active {
        background-color: rgba(0, 123, 255, 0.3);
    }
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
