<script lang="ts">
    import ArrowLeft from "lucide-svelte/icons/arrow-left";
    import Building2 from "lucide-svelte/icons/building-2";
    import CheckCircle from "lucide-svelte/icons/check-circle";
    import Drawer from "flowbite-svelte/Drawer.svelte";
    import { flyTransitionParamsBottom } from "$lib/helpers/fly";
    import { notify } from "$lib/helpers/notify";
    import { registerTenant } from "$lib/helpers/server-requests";
    import { languages } from "$lib/locales";
    import store from "$lib/store";

    const { isSignupDrawerHidden } = store;

    // -----------------------------------------------------------------------
    // Steps: "form" | "success"
    // -----------------------------------------------------------------------
    type Step = "form" | "success";
    let step: Step = "form";

    let name = "";
    let slug = "";
    let email = "";
    let language = "en";
    let logoFile: File | null = null;
    let logoPreviewUrl: string | null = null;
    let loading = false;

    /** The base domain used to construct the workspace URL shown after signup. */
    const baseDomain: string =
        typeof window !== "undefined" ? window.location.host : "localhost";

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

    function reset() {
        step = "form";
        name = "";
        slug = "";
        email = "";
        language = "en";
        logoFile = null;
        if (logoPreviewUrl) {
            URL.revokeObjectURL(logoPreviewUrl);
            logoPreviewUrl = null;
        }
        loading = false;
    }

    function close() {
        isSignupDrawerHidden.set(true);
        reset();
    }

    async function submit() {
        if (!name.trim()) {
            notify("Missing name", "Organisation name is required.", "warning", 4000, true);
            return;
        }
        if (!slug.trim()) {
            notify("Missing slug", "Workspace slug is required.", "warning", 4000, true);
            return;
        }
        if (!email.trim() || !email.includes("@")) {
            notify("Invalid email", "Enter a valid email address.", "warning", 4000, true);
            return;
        }

        loading = true;
        const result = await registerTenant(name.trim(), slug.trim(), email.trim().toLowerCase(), language, logoFile ?? undefined);
        loading = false;

        if ("error" in result) {
            notify("Error", result.error, "error", 6000, true);
        } else {
            if (result.warning) {
                notify("Almost there", result.warning, "warning", 8000, true);
            }
            step = "success";
        }
    }
</script>

<Drawer
    id="signup-drawer"
    placement="bottom"
    bind:hidden={$isSignupDrawerHidden}
    backdrop={true}
    class="drawer-box p-0 bg-gray-100 dark:bg-gray-900 rounded-lg shadow-lg max-w-[600px] m-auto"
    width="w-full"
    transitionType="fly"
    transitionParams={flyTransitionParamsBottom}
    activateClickOutside={true}
>
    <!-- Header -->
    <div
        class="flex items-center justify-between p-4 pb-2 bg-white dark:bg-gray-900"
        style="filter: drop-shadow(0px 1px 3px rgba(0,0,0,0.2));"
    >
        <button
            type="button"
            onclick={close}
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-md"
        >
            <ArrowLeft class="h-6 w-6 text-gray-800 dark:text-white" />
        </button>
        <div class="flex items-center gap-2">
            <Building2 class="h-5 w-5 text-blue-600 dark:text-blue-400" />
            <h2 class="text-xl font-bold text-gray-800 dark:text-white">Create Organisation</h2>
        </div>
        <div class="w-10"></div><!-- spacer -->
    </div>

    <div class="p-4 space-y-4 overflow-y-auto max-h-[80vh]">

        <!-- ---------------------------------------------------------------- -->
        <!-- Step: form                                                        -->
        <!-- ---------------------------------------------------------------- -->
        {#if step === "form"}
            <p class="text-sm text-gray-500 dark:text-gray-400">
                Set up your organisation in seconds. You'll receive a magic-link
                to your email to sign in as the account master.
            </p>

            <!-- Organisation Name -->
            <div>
                <label
                    class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1"
                    for="signup-name"
                >
                    Organisation Name
                </label>
                <input
                    id="signup-name"
                    type="text"
                    bind:value={name}
                    oninput={onNameInput}
                    placeholder="Acme Airlines"
                    class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm"
                />
            </div>

            <!-- Slug -->
            <div>
                <label
                    class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1"
                    for="signup-slug"
                >
                    Workspace Slug
                    <span class="normal-case font-normal text-gray-400">
                        — your URL will be <span class="font-mono text-blue-600 dark:text-blue-400">{slug || "acme"}.{baseDomain}</span>
                    </span>
                </label>
                <input
                    id="signup-slug"
                    type="text"
                    bind:value={slug}
                    placeholder="acme"
                    class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm font-mono"
                />
            </div>

            <!-- Email -->
            <div>
                <label
                    class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1"
                    for="signup-email"
                >
                    Your Email
                </label>
                <input
                    id="signup-email"
                    type="email"
                    bind:value={email}
                    placeholder="you@yourcompany.com"
                    class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm"
                />
            </div>

            <!-- Language -->
            <div>
                <label
                    class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1"
                    for="signup-language"
                >
                    Language
                </label>
                <select
                    id="signup-language"
                    bind:value={language}
                    class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm"
                >
                    {#each languages as { code, label }}
                        <option value={code}>{label}</option>
                    {/each}
                </select>
            </div>

            <!-- Logo upload (optional) -->
            <div>
                <label
                    class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1"
                    for="signup-logo"
                >
                    Logo <span class="normal-case font-normal text-gray-400">— optional</span>
                </label>
                {#if logoPreviewUrl}
                    <div class="flex justify-center mb-2">
                        <img
                            src={logoPreviewUrl}
                            alt="Logo preview"
                            class="h-20 object-contain rounded border border-gray-200 dark:border-gray-700 p-2" style="background: repeating-conic-gradient(#e5e7eb 0% 25%, #fff 0% 50%) 0 0 / 16px 16px;"
                        />
                    </div>
                {/if}
                <input
                    id="signup-logo"
                    type="file"
                    accept="image/png,image/jpeg,image/gif,image/webp,image/svg+xml"
                    onchange={onLogoChange}
                    class="w-full text-sm text-gray-700 dark:text-gray-300 file:mr-3 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-gray-700 dark:file:text-gray-200"
                />
            </div>

            <button
                type="button"
                onclick={submit}
                disabled={loading}
                class="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded-md text-sm transition-colors"
            >
                {loading ? "Creating…" : "Create Organisation"}
            </button>
        {/if}

        <!-- ---------------------------------------------------------------- -->
        <!-- Step: success                                                     -->
        <!-- ---------------------------------------------------------------- -->
        {#if step === "success"}
            <div class="flex flex-col items-center gap-4 py-6 text-center">
                <CheckCircle class="h-16 w-16 text-green-500" />
                <h3 class="text-xl font-bold text-gray-800 dark:text-white">
                    Organisation Created!
                </h3>
                <p class="text-sm text-gray-600 dark:text-gray-300 max-w-sm">
                    We've sent a magic-link to <span class="font-semibold">{email}</span>.
                    Click it to sign in as the master of your new workspace.
                </p>
                <div class="mt-2 px-4 py-3 bg-blue-50 dark:bg-blue-950 border border-blue-200 dark:border-blue-700 rounded-lg w-full">
                    <p class="text-xs text-gray-500 dark:text-gray-400 uppercase font-semibold mb-1">Your workspace URL</p>
                    <p class="font-mono text-blue-700 dark:text-blue-300 break-all">
                        {slug}.{baseDomain}
                    </p>
                </div>
                <p class="text-xs text-gray-400 dark:text-gray-500">
                    After signing in you can upload your logo and invite team members from the
                    <span class="font-semibold">Manage Team</span> card on the home screen.
                </p>
                <button
                    type="button"
                    onclick={close}
                    class="mt-2 py-2 px-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-md text-sm transition-colors"
                >
                    Close
                </button>
            </div>
        {/if}

    </div>
</Drawer>
