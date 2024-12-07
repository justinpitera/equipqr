<script lang="ts">
    import { LightbulbOff, Lightbulb } from "lucide-svelte";
    import { disableContextMenu } from "$lib/helpers/basics";
    import { qrScannerStore } from "$lib/helpers/camera";
    const { flashlightOn } = qrScannerStore;
</script>

<div
    id="qrScanner"
    class="relative w-full h-screen flex items-center justify-center bg-black"
>
    <div id="loadingMessage">
        🎥 Unable to access video stream (please make sure you have a webcam
        enabled)
    </div>
    <canvas
        id="canvas"
        hidden
        style="position: absolute; top: 0; left: 0; width: 100vw; height: 100vh;"
    ></canvas>
    <div id="output" hidden>
        <div id="outputMessage">No QR code detected.</div>
        <div hidden><b>Data:</b> <span id="outputData"></span></div>
    </div>
    <button
        type="button"
        id="toggleFlashlight"
        class="select-none"
        onclick={() => {
            flashlightOn.set(!$flashlightOn);
        }}
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
</div>
