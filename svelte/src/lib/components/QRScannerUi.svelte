<script lang="ts">
    import LightbulbOff from "lucide-svelte/icons/lightbulb-off";
    import Lightbulb from "lucide-svelte/icons/lightbulb";
    import Menu from "lucide-svelte/icons/menu";
    import { disableContextMenu } from "$lib/helpers/basics";
    import { destroyScanner } from "$lib/helpers/camera";
    import { t } from "$lib/locales";
    import store from "$lib/store";
    const {
        flashlightOn,
        flashlightDisabled,
        startQRScanner,
        darkModeEnabled,
        cameraDevicesList,
        showLoader,
    } = store;
</script>

<div
    id="qrScanner"
    class="relative w-[100svw] h-[100svh] flex items-center justify-center bg-black"
    style="filter: invert({$darkModeEnabled ? '1' : '0'});"
>
    <div
        class="absolute bottom-4 left-4 z-50 p-3 bg-white rounded-full cursor-pointer shadow-md hover:bg-gray-300"
        class:hide={$showLoader}
        onclick={async () => {
            startQRScanner.set(false);
            store.showLoader.set(false);
            await destroyScanner();
        }}
        onkeypress={async (event) => {
            if (event.key === "Enter" || event.key === " ") {
                startQRScanner.set(false);
                await destroyScanner();
            }
        }}
        role="button"
        tabindex="0"
    >
        <Menu class="w-6 h-6 text-black" />
    </div>
    <div id="loadingMessage">🎥 {t("Loading Camera...")}</div>
    <canvas
        id="canvas"
        hidden
        style="max-width: 100%;position: absolute; top: 0; left: 0; width: 100svw; height: 100svh;"
    ></canvas>
    <div id="output" hidden>
        <div id="outputMessage">{t("No QR code detected.")}</div>
        <div hidden><b>{t("Data:")}</b> <span id="outputData"></span></div>
    </div>
    {#if $cameraDevicesList && $cameraDevicesList.length > 0}
        <select
            id="videoSource"
            class:hide={$showLoader}
            class="absolute top-[20px] right-[80px] z-50 p-2 bg-white rounded-md shadow-md"
        >
            {#each $cameraDevicesList as deviceInfo}
                {#if deviceInfo.kind === "videoinput"}
                    <option value={deviceInfo.deviceId}>
                        {deviceInfo.label || `Camera ${deviceInfo.deviceId}`}
                    </option>
                {/if}
            {/each}
        </select>
    {/if}
    <!-- Switch Camera: -->
    <!-- <button
        class="absolute top-4 right-4 z-50 p-3 bg-white rounded-full cursor-pointer shadow-md hover:bg-gray-300"
        class:hide={$showLoader}
        onclick={() => {
            if (typeof document !== "undefined") {
                const videoSelect = document.querySelector(
                    "select#videoSource",
                ) as HTMLSelectElement;
                if (videoSelect) {
                    const currentIndex = videoSelect.selectedIndex;
                    const nextIndex =
                        (currentIndex + 1) % videoSelect.options.length;
                    videoSelect.selectedIndex = nextIndex;
                    videoSelect.dispatchEvent(new Event("change"));
                    switchCamera(videoSelect.value);
                }
            }
        }}
        aria-label="Switch Camera"
    >
        <svg
            class="w-6 h-6 text-black"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
        >
            <path
                d="M23 7v10a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h18a2 2 0 0 1 2 2z"
            />
            <rect x="2" y="9" width="20" height="6" />
        </svg>
    </button> -->
    <!-- Flashlight: -->
    {#if !$flashlightDisabled}
        <button
            type="button"
            id="toggleFlashlight"
            class="select-none hidden"
            class:hide={$showLoader}
        >
            {#if $flashlightOn}
                <Lightbulb
                    oncontextmenu={disableContextMenu}
                    class="flashlight-btn animate-pulse w-8 h-8"
                    style="filter: drop-shadow(0px 0px 6px yellow) blur(0.2px)"
                />
            {:else}
                <LightbulbOff
                    oncontextmenu={disableContextMenu}
                    class="flashlight-btn w-8 h-8"
                    style="filter: drop-shadow(0px 0px 6px black) blur(0.2px)"
                />
            {/if}
        </button>
    {/if}
</div>
