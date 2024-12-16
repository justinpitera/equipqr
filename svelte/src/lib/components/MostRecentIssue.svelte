<script lang="ts">
    import { onDestroy, onMount, tick } from "svelte";
    import { disableContextMenu } from "$lib/helpers/basics";
    import { BACKEND_URL, DEBUG_MODE } from "$lib/config";
    import { langChecker, translations } from "$lib/locales";
    import Checkbox from "flowbite-svelte/Checkbox.svelte";
    import Drawer from "flowbite-svelte/Drawer.svelte";
    import ArrowLeft from "lucide-svelte/icons/arrow-left";
    import Copy from "lucide-svelte/icons/copy";
    import { Button } from "flowbite-svelte";
    import store from "$lib/store";
    const {
        fullscreenViewer,
        fullscreenImage,
        fullscreenVideo,
        isFullScreenMode,
        selectedLanguage,
        darkModeEnabled,
        isRecentIssueDrawerHidden,
        detectedGSE,
        isAutoOpenMostRecentIssue,
        showPopup,
        issue_description,
    } = store;

    function t(key: string): string {
        const langTranslations = translations[$selectedLanguage];
        langChecker(key);
        return langTranslations?.[key] || key;
    }

    let interval: NodeJS.Timeout;
    let timeAgo = "";
    function calculateTimeAgo(reportedAt: string): string {
        const now = new Date();
        const reportedDate = new Date(reportedAt);
        const diff = Math.max(0, now.getTime() - reportedDate.getTime());
        const years = Math.floor(diff / (1000 * 60 * 60 * 24 * 365));
        const months = Math.floor(
            (diff % (1000 * 60 * 60 * 24 * 365)) / (1000 * 60 * 60 * 24 * 30),
        );
        const days = Math.floor(
            (diff % (1000 * 60 * 60 * 24 * 30)) / (1000 * 60 * 60 * 24),
        );
        const hours = Math.floor(
            (diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60),
        );
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((diff % (1000 * 60)) / 1000);
        const parts = [
            years > 0 ? `${years} year${years > 1 ? "s" : ""}` : "",
            months > 0 ? `${months} month${months > 1 ? "s" : ""}` : "",
            days > 0 ? `${days} day${days > 1 ? "s" : ""}` : "",
            hours > 0 ? `${hours} hour${hours > 1 ? "s" : ""}` : "",
            minutes > 0 ? `${minutes} minute${minutes > 1 ? "s" : ""}` : "",
            seconds > 0 ? `${seconds} second${seconds > 1 ? "s" : ""}` : "",
        ];
        const timeAgoOutput = parts
            .filter(Boolean)
            .reduce((acc, part, index, array) => {
                if (index === array.length - 1 && array.length > 1) {
                    return `${acc} ${t("and")} ${part}`;
                }
                return acc ? `${acc}, ${part}` : part;
            }, "");
        return timeAgoOutput ? `${timeAgoOutput} ${t("ago")}` : t("just now");
    }

    function handleAttachmentClick(url: string, type: "video" | "img") {
        if (!$fullscreenVideo || !$fullscreenImage || !$fullscreenViewer)
            return;
        $fullscreenViewer.classList.remove("hidden");
        $fullscreenViewer.classList.add("flex");
        isFullScreenMode.set(true);
        if (type === "img") {
            $fullscreenImage.src = url;
            $fullscreenImage.classList.remove("hidden");
            $fullscreenVideo.classList.add("hidden");
        } else if (type === "video") {
            $fullscreenVideo.src = url;
            $fullscreenVideo.classList.remove("hidden");
            $fullscreenImage.classList.add("hidden");
        }
    }

    function openAttachment(attachment: string) {
        if (attachment.split("img:")[1]) {
            handleAttachmentClick(
                `${BACKEND_URL}/api/media/attachment?id=${attachment.split("img:")[1]}`,
                "img",
            );
        } else if (attachment.split("video:")[1]) {
            handleAttachmentClick(
                `${BACKEND_URL}/api/media/attachment?id=${attachment.split("video:")[1]}`,
                "video",
            );
        }
    }

    const toggleAutoOpenRecentIssue = (event: Event) => {
        isAutoOpenMostRecentIssue.set(
            ((event as CustomEvent<boolean>).target as HTMLInputElement)
                .checked,
        );
        if (typeof window !== "undefined")
            localStorage.setItem(
                "autoOpenMostRecentIssue",
                String($isAutoOpenMostRecentIssue),
            );
    };

    $: if ($detectedGSE?.most_recent_issue?.reported_at) {
        timeAgo = calculateTimeAgo($detectedGSE.most_recent_issue.reported_at);
    }

    const selectIssue = (): void => {
        isRecentIssueDrawerHidden.set(true);
        if ($detectedGSE?.most_recent_issue?.issue_description)
            issue_description.set(
                $detectedGSE.most_recent_issue.issue_description,
            );
        // operable.set(issue.is_operable.toLowerCase());
        // if (issue.gate_type) {
        //     const gate_type = issue.gate_type.toLowerCase();
        //     selected_gate_type.set(gate_type);
        //     if (issue.gate_name) {
        //         build_gate_options(gate_type, issue.gate_name);
        //         selected_gate_name.set(issue.gate_name);
        //     } else {
        //         selected_gate_name.set("");
        //         build_gate_options(gate_type);
        //     }
        // } else {
        //     selected_gate_type.set("");
        // }
    };

    onMount(() => {
        interval = setInterval(async () => {
            if ($detectedGSE?.most_recent_issue?.reported_at) {
                timeAgo = calculateTimeAgo(
                    $detectedGSE.most_recent_issue.reported_at,
                );
                await tick();
            }
        }, 1000);

        return () => clearInterval(interval);
    });
    onDestroy(() => {
        isRecentIssueDrawerHidden.set(true);
    });
</script>

<Drawer
    id="most-recent-issue-drawer"
    placement="bottom"
    bind:hidden={$isRecentIssueDrawerHidden}
    backdrop={true}
    class="drawer-box p-6 md:p-8 bg-white rounded-lg md:rounded-none shadow-lg max-w-[600px] m-auto"
    width="w-full"
    activateClickOutside={false}
    transitionParams={{
        duration: 0,
        easing: undefined,
    }}
>
    <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold text-gray-800">
            {t("Most Recent Issue")}
        </h2>
        <button
            type="button"
            onclick={() => isRecentIssueDrawerHidden.set(true)}
            class="p-2 hover:bg-gray-200 rounded-md"
        >
            <ArrowLeft class="h-6 w-6 text-gray-800" />
        </button>
    </div>

    <div class="mt-6">
        {#if $detectedGSE && $detectedGSE.most_recent_issue}
            <div class="space-y-4">
                {#if DEBUG_MODE}
                    <p class="text-sm text-gray-700 dark:text-gray-300">
                        <strong>{t("Issue ID:")}</strong><br />
                        {$detectedGSE.most_recent_issue.id}
                    </p>
                {/if}
                <p class="text-sm text-gray-700 dark:text-gray-300">
                    <strong>{t("Description:")}</strong><br />
                    {$detectedGSE.most_recent_issue.issue_description}
                </p>
                <Button
                    onclick={selectIssue}
                    style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                >
                    <Copy
                        class="h-5 w-5 text-gray-800"
                        style="filter: invert(1);"
                    />
                    Copy
                </Button>
                <p class="text-sm text-gray-700 dark:text-gray-300">
                    <strong>{t("Reported At:")}</strong><br />
                    {new Date(
                        $detectedGSE.most_recent_issue.reported_at,
                    ).toLocaleString()}<br />
                    <span>({timeAgo})</span>
                </p>
                {#if $detectedGSE.most_recent_issue.attachments}
                    <hr class="my-4" />
                    <div class="mt-2">
                        <strong
                            class="text-sm text-gray-700 dark:text-gray-300 mb-3 block"
                            >{t("Attachments:")}</strong
                        >
                        <div
                            id="gallery-container"
                            class="ignore-js"
                            style="filter: invert({$darkModeEnabled
                                ? '1'
                                : '0'});"
                        >
                            <div id="gallery" class="ignore-js">
                                {#each $detectedGSE.most_recent_issue.attachments.split(", ") as attachment}
                                    <div
                                        role="button"
                                        tabindex="0"
                                        class="gallery-item ignore-js select-none relative"
                                        onclick={() =>
                                            openAttachment(attachment)}
                                        onkeypress={(event) => {
                                            if (
                                                event.key === "Enter" ||
                                                event.key === " "
                                            ) {
                                                openAttachment(attachment);
                                            }
                                        }}
                                    >
                                        {#if attachment.split("img:")[1]}
                                            <img
                                                src={`${BACKEND_URL}/api/media/attachment?id=${attachment.split("img:")[1]}`}
                                                alt="media"
                                                class="disableSave ignore-js"
                                                draggable="false"
                                                oncontextmenu={disableContextMenu}
                                            />
                                        {:else if attachment.split("video:")[1]}
                                            <video
                                                src={`${BACKEND_URL}/api/media/attachment?id=${attachment.split("video:")[1]}`}
                                                controls={false}
                                                loop={true}
                                                autoplay={true}
                                                muted={true}
                                                class="disableSave ignore-js"
                                                draggable="false"
                                                oncontextmenu={disableContextMenu}
                                            ></video>
                                        {/if}
                                    </div>
                                {/each}
                            </div>
                        </div>
                    </div>
                {/if}
            </div>
        {:else}
            <p class="mt-4 text-sm text-gray-500 dark:text-gray-400">
                {t("No recent issues found for this GSE.")}
            </p>
        {/if}
        <div class="mt-6 flex justify-between">
            <div
                class="flex items-center space-x-4{$showPopup ? '' : ' hidden'}"
            >
                <label for="toggle" class="text-lg">{t("Auto Open:")}</label>
                <Checkbox
                    id="toggle"
                    class="mt-1"
                    checked={$isAutoOpenMostRecentIssue}
                    on:change={toggleAutoOpenRecentIssue}
                    color="blue"
                    style="filter: invert({$darkModeEnabled ? '1' : '0'});"
                >
                    {#if $isAutoOpenMostRecentIssue}
                        {t("On")}
                    {:else}
                        {t("Off")}
                    {/if}
                </Checkbox>
            </div>
            <Button
                onclick={() => isRecentIssueDrawerHidden.set(true)}
                class="bg-blue-500 hover:bg-blue-600 text-white rounded-full px-6 py-2"
                style="filter: invert({$darkModeEnabled ? '1' : '0'});"
            >
                {t("Close")}
            </Button>
        </div>
    </div>
</Drawer>
