<script lang="ts">
    import { ToastContainer, FlatToast } from "svelte-toasts";
</script>

<ToastContainer placement="bottom-center" let:data>
    <FlatToast {data} />
</ToastContainer>
