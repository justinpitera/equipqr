<script>
	import "../app.css";
	import NotifyUi from "$lib/components/NotifyUi.svelte";
	let { children } = $props();
</script>

<!-- Main content area -->
<div class="min-h-screen">
	{@render children()}
</div>
<NotifyUi />
