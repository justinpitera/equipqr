<script lang="ts">
    import LightbulbOff from "lucide-svelte/icons/lightbulb-off";
    import Lightbulb from "lucide-svelte/icons/lightbulb";
    import Menu from "lucide-svelte/icons/menu";
    import X from "lucide-svelte/icons/x";
    import Snowflake from "lucide-svelte/icons/snowflake";
    import Play from "lucide-svelte/icons/play";
    import { onMount } from "svelte";
    import { disableContextMenu } from "$lib/helpers/basics";
    import { destroyScanner, selectOverlayItem, stopOverlayScanner, getZoomCapabilities, setZoom, setFrozen } from "$lib/helpers/camera";
    import { t } from "$lib/locales";
    import store from "$lib/store";
    const {
        flashlightOn,
        flashlightDisabled,
        startQRScanner,
        darkModeEnabled,
        qrOverlayItems,
    } = store;

    async function closeScanner() {
        frozen = false;
        setFrozen(false);
        stopOverlayScanner();
        startQRScanner.set(false);
        store.showLoader.set(false);
        await destroyScanner();
    }

    // ── Freeze frame ──────────────────────────────────────────────────────────
    let frozen = false;

    function toggleFreeze() {
        frozen = !frozen;
        setFrozen(frozen);
    }

    function handleCardClick(item: QROverlayItem) {
        if (item.loading) return;
        selectOverlayItem(item.gse_id);
    }

    // ── Pinch-to-zoom ─────────────────────────────────────────────────────────
    let scannerEl: HTMLDivElement;
    let zoomLevel = 1;
    let zoomMin = 1;
    let zoomMax = 10;
    let showZoomIndicator = false;
    let zoomFadeTimer: ReturnType<typeof setTimeout> | null = null;

    let pinchStartDist = 0;
    let pinchStartZoom = 1;

    function pinchDist(touches: TouchList): number {
        const dx = touches[0].clientX - touches[1].clientX;
        const dy = touches[0].clientY - touches[1].clientY;
        return Math.sqrt(dx * dx + dy * dy);
    }

    function handleTouchStart(e: TouchEvent) {
        if (e.touches.length !== 2) return;
        const caps = getZoomCapabilities();
        if (caps) { zoomMin = caps.min; zoomMax = caps.max; }
        pinchStartDist = pinchDist(e.touches);
        pinchStartZoom = zoomLevel;
    }

    function handleTouchMove(e: TouchEvent) {
        if (e.touches.length !== 2) return;
        e.preventDefault(); // block browser page zoom (requires non-passive listener)
        const dist = pinchDist(e.touches);
        if (pinchStartDist === 0) return;
        const newZoom = Math.min(zoomMax, Math.max(zoomMin, pinchStartZoom * (dist / pinchStartDist)));
        if (Math.abs(newZoom - zoomLevel) < 0.05) return;
        zoomLevel = newZoom;
        setZoom(zoomLevel);
        showZoomIndicator = true;
        if (zoomFadeTimer) clearTimeout(zoomFadeTimer);
        zoomFadeTimer = setTimeout(() => { showZoomIndicator = false; }, 1500);
    }

    function handleTouchEnd(e: TouchEvent) {
        if (e.touches.length < 2) pinchStartDist = 0;
    }

    // Use a non-passive touchmove listener so e.preventDefault() is allowed
    onMount(() => {
        const el = scannerEl;
        const onMove = (e: TouchEvent) => handleTouchMove(e);
        el.addEventListener('touchmove', onMove, { passive: false });
        return () => el.removeEventListener('touchmove', onMove);
    });
</script>

<div
    bind:this={scannerEl}
    id="qrScanner"
    class="relative w-[100svw] h-[100svh] bg-black overflow-hidden"
    style="filter: invert({$darkModeEnabled ? '1' : '0'});"
    ontouchstart={handleTouchStart}
    ontouchend={handleTouchEnd}
>
    <!-- <div id="loadingMessage" hidden>🎥 {t("Loading Camera...")}</div> -->
    <!-- svelte-ignore a11y_media_has_caption -->
    <div id="video_streams" class="absolute inset-0 w-full h-full"></div>

    <!-- VisPick-style overlay cards -->
    {#each $qrOverlayItems as item (item.gse_id)}
        {@const hasIssue = !!item.gseDetails?.most_recent_issue}
        {@const cardColor = item.loading
            ? 'bg-gray-800/80 border-gray-400'
            : hasIssue
                ? 'bg-red-900/85 border-red-400'
                : 'bg-green-900/85 border-green-400'}
        <!-- svelte-ignore a11y_click_events_have_key_events -->
        <!-- svelte-ignore a11y_no_static_element_interactions -->
        <div
            class="absolute z-30 rounded-xl border-2 {cardColor} text-white text-xs shadow-lg cursor-pointer select-none transition-all duration-200 active:scale-95"
            style="
                left: {item.x}%;
                top: {item.y}%;
                width: max(80px, {item.width}%);
                transform: translateY(-110%);
                backdrop-filter: blur(4px);
                -webkit-backdrop-filter: blur(4px);
            "
            onclick={() => handleCardClick(item)}
        >
            <!-- Connector line pointing down to the QR code -->
            <div
                class="absolute left-1/2 -translate-x-1/2 bottom-0 translate-y-full w-0.5 h-3 {hasIssue ? 'bg-red-400' : item.loading ? 'bg-gray-400' : 'bg-green-400'}"
            ></div>

            <div class="p-2">
                <div class="min-w-0 flex-1">
                    <p class="font-bold leading-tight truncate text-[11px]">{item.gse_id}</p>
                    {#if item.loading}
                        <p class="text-gray-300 text-[10px]">Loading…</p>
                    {:else if !item.gseDetails?.gse_id}
                        <p class="text-yellow-300 text-[10px]">Not found</p>
                    {:else if hasIssue}
                        <p class="text-red-200 text-[10px] font-semibold">Issue reported</p>
                        {#if item.gseDetails.most_recent_issue?.issue_description}
                            <p class="text-red-300 text-[9px] truncate mt-0.5">{item.gseDetails.most_recent_issue.issue_description}</p>
                        {/if}
                    {:else}
                        <p class="text-green-200 text-[10px]">In service</p>
                        {#if item.gseDetails.gse_type}
                            <p class="text-green-300 text-[9px] truncate">{item.gseDetails.gse_type}</p>
                        {/if}
                    {/if}
                    {#if !item.loading && item.gseDetails?.gse_id}
                        <p class="text-white/60 text-[9px] mt-0.5">Tap to report</p>
                    {/if}
                </div>
            </div>
        </div>
    {/each}

    <!-- Zoom level indicator (appears during pinch, fades out) -->
    {#if showZoomIndicator}
        <div
            class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 bg-black/60 text-white text-base font-semibold px-4 py-2 rounded-full pointer-events-none select-none"
            style="backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);"
        >
            {zoomLevel.toFixed(1)}×
        </div>
    {/if}

    <!-- Controls bar: portrait → bottom strip, landscape → right side panel -->
    <div class="ctrl-bar" aria-label="Scanner controls">
        <!-- Close -->
        <button
            type="button"
            class="ctrl-btn"
            onclick={closeScanner}
            onkeypress={async (e) => { if (e.key === 'Enter' || e.key === ' ') await closeScanner(); }}
            aria-label="Close scanner"
        >
            <X class="w-5 h-5" />
            <span class="ctrl-label">Close</span>
        </button>

        <!-- Flashlight (camera.ts controls visibility via classList) -->
        <button type="button" id="toggleFlashlight" class="ctrl-btn hidden" aria-label="Toggle flashlight">
            {#if $flashlightOn}
                <Lightbulb oncontextmenu={disableContextMenu} class="w-5 h-5 text-yellow-300" />
            {:else}
                <LightbulbOff oncontextmenu={disableContextMenu} class="w-5 h-5" />
            {/if}
            <span class="ctrl-label">{$flashlightOn ? 'Light on' : 'Light off'}</span>
        </button>

        <!-- Freeze -->
        <button
            type="button"
            class="ctrl-btn {frozen ? 'ctrl-btn--active' : ''}"
            onclick={toggleFreeze}
            aria-label={frozen ? 'Unfreeze camera' : 'Freeze frame'}
        >
            {#if frozen}
                <Play class="w-5 h-5" />
            {:else}
                <Snowflake class="w-5 h-5" />
            {/if}
            <span class="ctrl-label">{frozen ? 'Unfreeze' : 'Freeze'}</span>
        </button>

        <div id="output" hidden>
            <div id="outputMessage">{t("No QR code detected.")}</div>
            <div hidden><b>{t("Data:")}</b> <span id="outputData"></span></div>
        </div>
    </div>
</div>

<style>
    /* ── Controls bar ────────────────────────────────────────────────────────
       Portrait  → thin frosted strip along the bottom
       Landscape → narrow frosted panel on the right edge (where Android nav lives)
    ───────────────────────────────────────────────────────────────────────── */
    .ctrl-bar {
        position: absolute;
        z-index: 40;
        display: flex;
        align-items: center;
        justify-content: space-around;
        gap: 4px;

        background: rgba(15, 15, 20, 0.55);
        backdrop-filter: blur(18px) saturate(160%);
        -webkit-backdrop-filter: blur(18px) saturate(160%);
        border: 1px solid rgba(255, 255, 255, 0.12);

        /* Portrait: bottom strip */
        bottom: 0;
        left: 0;
        right: 0;
        flex-direction: row;
        padding: 10px 16px calc(10px + env(safe-area-inset-bottom)) 16px;
        border-radius: 20px 20px 0 0;
    }

    @media (orientation: landscape) {
        .ctrl-bar {
            /* Landscape: right-side panel (Android nav side) */
            bottom: 0;
            top: 0;
            right: 0;
            left: auto;
            flex-direction: column;
            padding: 16px calc(10px + env(safe-area-inset-right)) 16px 10px;
            border-radius: 20px 0 0 20px;
            width: auto;
        }
    }

    .ctrl-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 3px;
        padding: 10px 14px;
        border-radius: 14px;
        border: none;
        cursor: pointer;
        color: rgba(255, 255, 255, 0.9);
        background: rgba(255, 255, 255, 0.08);
        transition: background 0.15s ease, transform 0.1s ease;
        -webkit-tap-highlight-color: transparent;
        user-select: none;
    }

    .ctrl-btn:hover,
    .ctrl-btn:focus-visible {
        background: rgba(255, 255, 255, 0.16);
        outline: none;
    }

    .ctrl-btn:active {
        transform: scale(0.92);
        background: rgba(255, 255, 255, 0.22);
    }

    .ctrl-btn--active {
        background: rgba(59, 130, 246, 0.5);
        color: #fff;
    }

    .ctrl-btn--active:hover {
        background: rgba(59, 130, 246, 0.65);
    }

    .ctrl-label {
        font-size: 9px;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        color: rgba(255, 255, 255, 0.65);
        line-height: 1;
    }
</style>
