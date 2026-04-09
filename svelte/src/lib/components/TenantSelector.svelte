<script lang="ts">
    import { onMount } from "svelte";
    import Spinner from "flowbite-svelte/Spinner.svelte";
    import Button from "flowbite-svelte/Button.svelte";
    import { listTenants, registerTenant } from "$lib/helpers/server-requests";
    import { languages } from "$lib/locales";
    import Building2 from "lucide-svelte/icons/building-2";
    import ChevronRight from "lucide-svelte/icons/chevron-right";
    import ArrowLeft from "lucide-svelte/icons/arrow-left";
    import CheckCircle from "lucide-svelte/icons/check-circle";
    import PlusCircle from "lucide-svelte/icons/plus-circle";

    // ── mode: "select" | "create" | "success" ────────────────────────────
    type Mode = "select" | "create" | "success";
    let mode: Mode = "select";

    // ── select mode ───────────────────────────────────────────────────────
    let tenants: { slug: string; name: string }[] = [];
    let selectedSlug = "";
    let loadingTenants = true;
    let fetchError = "";

    onMount(async () => {
        const result = await listTenants();
        if (result.length > 0) {
            tenants = result;
            selectedSlug = result[0].slug;
        }
        loadingTenants = false;
    });

    function navigate() {
        if (!selectedSlug) return;
        const { protocol, hostname, port } = window.location;
        const portSuffix = port ? `:${port}` : "";
        window.location.href = `${protocol}//${selectedSlug}.${hostname}${portSuffix}`;
    }

    // ── create mode ───────────────────────────────────────────────────────
    const baseDomain: string =
        typeof window !== "undefined" ? window.location.host : "localhost";

    let name = "";
    let slug = "";
    let email = "";
    let language = "en";
    let logoFile: File | null = null;
    let logoPreviewUrl: string | null = null;
    let creating = false;
    let createError = "";

    function deriveSlug(input: string): string {
        return input
            .toLowerCase()
            .trim()
            .replace(/\s+/g, "-")
            .replace(/[^a-z0-9-]/g, "")
            .replace(/^-+|-+$/g, "");
    }

    function onNameInput() {
        slug = deriveSlug(name);
    }

    function onLogoChange(e: Event) {
        const input = e.target as HTMLInputElement;
        const file = input.files?.[0] ?? null;
        logoFile = file;
        if (logoPreviewUrl) URL.revokeObjectURL(logoPreviewUrl);
        logoPreviewUrl = file ? URL.createObjectURL(file) : null;
    }

    function resetCreate() {
        name = "";
        slug = "";
        email = "";
        language = "en";
        logoFile = null;
        if (logoPreviewUrl) { URL.revokeObjectURL(logoPreviewUrl); logoPreviewUrl = null; }
        creating = false;
        createError = "";
    }

    async function submitCreate() {
        createError = "";
        if (!name.trim()) { createError = "Organisation name is required."; return; }
        if (!slug.trim()) { createError = "Workspace slug is required."; return; }
        if (!email.trim() || !email.includes("@")) { createError = "Enter a valid email address."; return; }

        creating = true;
        const result = await registerTenant(name.trim(), slug.trim(), email.trim().toLowerCase(), language, logoFile ?? undefined);
        creating = false;

        if ("error" in result) {
            createError = result.error;
        } else {
            mode = "success";
        }
    }
</script>

<main class="min-h-screen flex items-center justify-center bg-slate-100 dark:bg-gray-950 px-4">
    <div class="w-full max-w-sm bg-white dark:bg-gray-900 rounded-2xl shadow-lg p-8 flex flex-col items-center gap-6">

        <!-- Logo — always shown -->
        <img
            src="/Fejlemingsapp_logo.png"
            alt="EquipQR"
            width="96"
            height="auto"
            class="dark:invert"
        />

        <!-- ── SELECT ──────────────────────────────────────────────────── -->
        {#if mode === "select"}
            <div class="text-center">
                <h1 class="text-xl font-bold text-gray-800 dark:text-white">Select your organization</h1>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Choose your organization to continue</p>
            </div>

            {#if loadingTenants}
                <Spinner color="blue" class="w-8 h-8" />
            {:else}
                {#if fetchError}
                    <p class="text-sm text-red-500 text-center">{fetchError}</p>
                {/if}

                {#if tenants.length > 0}
                    <div class="w-full">
                        <label for="org-select" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">
                            <span class="flex items-center gap-1.5">
                                <Building2 class="h-4 w-4" />
                                Organization
                            </span>
                        </label>
                        <select
                            id="org-select"
                            bind:value={selectedSlug}
                            class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                            {#each tenants as tenant}
                                <option value={tenant.slug}>{tenant.name}</option>
                            {/each}
                        </select>
                    </div>

                    <Button
                        color="blue"
                        class="w-full flex items-center justify-center gap-2"
                        onclick={navigate}
                        disabled={!selectedSlug}
                    >
                        Continue
                        <ChevronRight class="h-4 w-4" />
                    </Button>

                    <div class="w-full flex items-center gap-3">
                        <hr class="flex-1 border-gray-200 dark:border-gray-700" />
                        <span class="text-xs text-gray-400">or</span>
                        <hr class="flex-1 border-gray-200 dark:border-gray-700" />
                    </div>
                {/if}

                <button
                    type="button"
                    onclick={() => { resetCreate(); mode = "create"; }}
                    class="w-full flex items-center justify-center gap-2 py-2 px-4 border border-dashed border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                    <PlusCircle class="h-4 w-4" />
                    Create new organization
                </button>
            {/if}

        <!-- ── CREATE ──────────────────────────────────────────────────── -->
        {:else if mode === "create"}
            <div class="w-full flex items-center gap-3">
                <button
                    type="button"
                    onclick={() => mode = "select"}
                    class="p-1.5 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300"
                    aria-label="Back"
                >
                    <ArrowLeft class="h-5 w-5" />
                </button>
                <div>
                    <h1 class="text-xl font-bold text-gray-800 dark:text-white">Create organization</h1>
                    <p class="text-xs text-gray-500 dark:text-gray-400">You'll receive a magic-link to sign in</p>
                </div>
            </div>

            <div class="w-full space-y-4">
                <!-- Name -->
                <div>
                    <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1" for="cs-name">
                        Organisation Name
                    </label>
                    <input
                        id="cs-name"
                        type="text"
                        bind:value={name}
                        oninput={onNameInput}
                        placeholder="Acme Airlines"
                        class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm"
                    />
                </div>

                <!-- Slug -->
                <div>
                    <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1" for="cs-slug">
                        Workspace Slug
                        <span class="normal-case font-normal text-gray-400">
                            — <span class="font-mono text-blue-600 dark:text-blue-400">{slug || "acme"}.{baseDomain}</span>
                        </span>
                    </label>
                    <input
                        id="cs-slug"
                        type="text"
                        bind:value={slug}
                        placeholder="acme"
                        class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm font-mono"
                    />
                </div>

                <!-- Email -->
                <div>
                    <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1" for="cs-email">
                        Your Email
                    </label>
                    <input
                        id="cs-email"
                        type="email"
                        bind:value={email}
                        placeholder="you@yourcompany.com"
                        class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm"
                    />
                </div>

                <!-- Language -->
                <div>
                    <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1" for="cs-lang">
                        Language
                    </label>
                    <select
                        id="cs-lang"
                        bind:value={language}
                        class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm"
                    >
                        {#each languages as { code, label }}
                            <option value={code}>{label}</option>
                        {/each}
                    </select>
                </div>

                <!-- Logo (optional) -->
                <div>
                    <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1" for="cs-logo">
                        Logo <span class="normal-case font-normal text-gray-400">— optional</span>
                    </label>
                    {#if logoPreviewUrl}
                        <div class="flex justify-center mb-2">
                            <img
                                src={logoPreviewUrl}
                                alt="Logo preview"
                                class="h-16 object-contain rounded border border-gray-200 dark:border-gray-700 p-2"
                                style="background: repeating-conic-gradient(#e5e7eb 0% 25%, #fff 0% 50%) 0 0 / 16px 16px;"
                            />
                        </div>
                    {/if}
                    <input
                        id="cs-logo"
                        type="file"
                        accept="image/png,image/jpeg,image/gif,image/webp,image/svg+xml"
                        onchange={onLogoChange}
                        class="w-full text-sm text-gray-700 dark:text-gray-300 file:mr-3 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-gray-700 dark:file:text-gray-200"
                    />
                </div>

                {#if createError}
                    <p class="text-sm text-red-500">{createError}</p>
                {/if}

                <button
                    type="button"
                    onclick={submitCreate}
                    disabled={creating}
                    class="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded-md text-sm transition-colors"
                >
                    {creating ? "Creating…" : "Create Organisation"}
                </button>
            </div>

        <!-- ── SUCCESS ─────────────────────────────────────────────────── -->
        {:else}
            <div class="flex flex-col items-center gap-4 text-center">
                <CheckCircle class="h-14 w-14 text-green-500" />
                <h2 class="text-xl font-bold text-gray-800 dark:text-white">Organisation Created!</h2>
                <p class="text-sm text-gray-600 dark:text-gray-300">
                    We've sent a magic-link to <span class="font-semibold">{email}</span>.
                    Click it to sign in as the master of your new workspace.
                </p>
                <div class="w-full px-4 py-3 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-700 rounded-lg">
                    <p class="text-xs text-gray-500 dark:text-gray-400 uppercase font-semibold mb-1">Your workspace URL</p>
                    <p class="font-mono text-blue-700 dark:text-blue-300 break-all">{slug}.{baseDomain}</p>
                </div>
                <button
                    type="button"
                    onclick={() => { resetCreate(); mode = "select"; }}
                    class="mt-2 py-2 px-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-md text-sm transition-colors"
                >
                    Back to login
                </button>
            </div>
        {/if}

    </div>
</main>
