<script lang="ts">
    import { disableContextMenu } from "$lib/helpers/basics";
    import { fileUploadStore, closeFullscreen } from "$lib/helpers/file-upload";
    const { fullscreenViewer, fullscreenImage, fullscreenVideo } =
        fileUploadStore;
    import { homePageStore } from "$lib/helpers/homepage";
    const { darkModeEnabled } = homePageStore;
</script>

<div
    id="fullscreenViewer"
    bind:this={$fullscreenViewer}
    role="button"
    tabindex="0"
    class="fixed inset-0 bg-black bg-opacity-90 items-center justify-center select-none hidden"
    onclick={closeFullscreen}
    onkeypress={(event) => {
        if (event.key === "Enter" || event.key === " ") {
            closeFullscreen();
        }
    }}
    style="z-index: 100; filter: invert({$darkModeEnabled ? '1' : '0'});"
>
    <button
        id="closeButton"
        type="button"
        onclick={closeFullscreen}
        class="absolute select-none top-4 right-4 text-red text-3xl z-10 shadow-lg"
        >×</button
    >
    <div
        role="button"
        tabindex="0"
        onclick={(e) => {
            e.stopPropagation();
            e.preventDefault();
        }}
        onkeypress={(e) => {
            if (e.key === "Enter" || e.key === " ") {
                e.stopPropagation();
                e.preventDefault();
            }
        }}
    >
        <img
            id="fullscreenImage"
            bind:this={$fullscreenImage}
            alt=""
            class="max-w-full max-h-full hidden"
            oncontextmenu={disableContextMenu}
        />
        <video
            id="fullscreenVideo"
            bind:this={$fullscreenVideo}
            class="max-w-full max-h-full hidden"
            controls={true}
            loop={true}
            autoplay={true}
            muted={false}
        >
            <track kind="captions" />
        </video>
    </div>
</div>
