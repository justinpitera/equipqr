<script lang="ts">
    import { onMount, tick } from "svelte";
    // Utilities
    import { disableContextMenu } from "$lib/helpers/basics";
    // QR Scanner utilities
    import { qrScannerStore } from "$lib/helpers/camera";
    const { detectedGSE } = qrScannerStore;
    // File upload utilities
    import { fileUploadStore } from "$lib/helpers/file-upload";
    const { fullscreenViewer, fullscreenImage, fullscreenVideo } =
        fileUploadStore;
    // Details Drawer utilities
    import { BACKEND_URL, DEBUG_MODE } from "$lib/config";
    import { homePageStore } from "$lib/helpers/homepage";
    import { langChecker, translations } from "$lib/locales";
    import { Drawer } from "flowbite-svelte";
    import { ArrowLeft } from "lucide-svelte";
    const { selectedLanguage, darkModeEnabled, isRecentIssueDrawerHidden } =
        homePageStore;

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
        const timeAgoOutput = parts.filter(Boolean).join(", ");
        return timeAgoOutput ? `${timeAgoOutput} ago` : "just now";
    }

    function handleAttachmentClick(url: string, type: "video" | "img") {
        if (!$fullscreenVideo || !$fullscreenImage || !$fullscreenViewer)
            return;
        $fullscreenViewer.classList.remove("hidden");
        $fullscreenViewer.classList.add("flex");
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

    $: if ($detectedGSE?.most_recent_issue?.reported_at) {
        timeAgo = calculateTimeAgo($detectedGSE.most_recent_issue.reported_at);
    }

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
</script>

<Drawer
    id="most-recent-issue-drawer"
    placement="bottom"
    bind:hidden={$isRecentIssueDrawerHidden}
    backdrop={true}
    class="p-6 md:p-8 bg-white rounded-lg shadow-lg"
    width="w-full"
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
                                        onkeypress={() =>
                                            openAttachment(attachment)}
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
    </div>
</Drawer>
