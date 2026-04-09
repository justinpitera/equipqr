<script lang="ts">
    import { Toaster } from "svelte-sonner";
</script>

<Toaster
    position="bottom-center"
    richColors
    closeButton
    expand={false}
    visibleToasts={4}
    toastOptions={{
        style: "font-family: inherit; border-radius: 12px;",
        classes: {
            toast: "!shadow-xl !border !border-white/10 !backdrop-blur-sm",
            title: "!font-semibold !text-sm",
            description: "!text-xs !opacity-80",
            closeButton: "!border !border-white/20",
        },
    }}
/>
