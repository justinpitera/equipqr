<script lang="ts">
    import ArrowLeft from "lucide-svelte/icons/arrow-left";
    import ImagePlus from "lucide-svelte/icons/image-plus";
    import UserPlus from "lucide-svelte/icons/user-plus";
    import Drawer from "flowbite-svelte/Drawer.svelte";
    import { flyTransitionParamsBottom } from "$lib/helpers/fly";
    import { notify } from "$lib/helpers/notify";
    import { uploadTenantLogo, inviteTenantMember, getTenantLogo } from "$lib/helpers/server-requests";
    import { languages } from "$lib/locales";
    import store from "$lib/store";

    const { isTenantMgmtDrawerHidden, tenantName, tenantLogoUrl } = store;

    type Tab = "logo" | "invite";
    let activeTab: Tab = "logo";

    // -----------------------------------------------------------------------
    // Logo tab
    // -----------------------------------------------------------------------
    let logoFile: File | null = null;
    let logoPreviewUrl: string | null = null;
    let logoLoading = false;

    function onLogoChange(e: Event) {
        const input = e.target as HTMLInputElement;
        const file = input.files?.[0] ?? null;
        logoFile = file;
        if (logoPreviewUrl) URL.revokeObjectURL(logoPreviewUrl);
        logoPreviewUrl = file ? URL.createObjectURL(file) : null;
    }

    async function submitLogo() {
        if (!logoFile) {
            notify("No file", "Please select an image file first.", "warning", 4000, true);
            return;
        }
        logoLoading = true;
        const result = await uploadTenantLogo(logoFile);
        logoLoading = false;
        if ("error" in result) {
            notify("Upload failed", result.error, "error", 6000, true);
        } else {
            notify("Logo updated", "Your organisation logo has been updated.", "success", 5000, true);
            // Refresh the logo in the header
            const url = await getTenantLogo();
            if (url) tenantLogoUrl.set(url);
            logoFile = null;
            if (logoPreviewUrl) {
                URL.revokeObjectURL(logoPreviewUrl);
                logoPreviewUrl = null;
            }
        }
    }

    // -----------------------------------------------------------------------
    // Invite tab
    // -----------------------------------------------------------------------
    let inviteEmail = "";
    let invitePosition = "employee";
    let inviteLanguage = "en";
    let inviteSendEmail = true;
    let inviteLoading = false;

    async function submitInvite() {
        if (!inviteEmail.trim() || !inviteEmail.includes("@")) {
            notify("Invalid email", "Enter a valid email address.", "warning", 4000, true);
            return;
        }
        inviteLoading = true;
        const result = await inviteTenantMember(
            inviteEmail.trim().toLowerCase(),
            invitePosition,
            inviteLanguage,
            inviteSendEmail,
        );
        inviteLoading = false;
        if ("error" in result) {
            notify("Error", result.error, "error", 6000, true);
        } else {
            const msg = result.warning
                ? result.warning
                : inviteSendEmail
                    ? `Invite sent to ${result.email}.`
                    : `${result.email} added (no email sent).`;
            notify("Member added", msg, result.warning ? "warning" : "success", 5000, true);
            inviteEmail = "";
        }
    }
</script>

<Drawer
    id="tenant-mgmt-drawer"
    placement="bottom"
    bind:hidden={$isTenantMgmtDrawerHidden}
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
            onclick={() => isTenantMgmtDrawerHidden.set(true)}
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-md"
        >
            <ArrowLeft class="h-6 w-6 text-gray-800 dark:text-white" />
        </button>
        <h2 class="text-xl font-bold text-gray-800 dark:text-white">
            {$tenantName ? `Manage — ${$tenantName}` : "Manage Team"}
        </h2>
        <div class="w-10"></div><!-- spacer -->
    </div>

    <div class="p-4 space-y-4 overflow-y-auto max-h-[80vh]">

        <!-- Tabs -->
        <div class="flex gap-2 border-b border-gray-200 dark:border-gray-700">
            <button
                type="button"
                onclick={() => activeTab = "logo"}
                class="flex items-center gap-1.5 px-4 py-2 text-sm font-medium border-b-2 transition-colors {activeTab === 'logo'
                    ? 'border-blue-600 text-blue-600 dark:text-blue-400 dark:border-blue-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'}"
            >
                <ImagePlus class="h-4 w-4" />
                Logo
            </button>
            <button
                type="button"
                onclick={() => activeTab = "invite"}
                class="flex items-center gap-1.5 px-4 py-2 text-sm font-medium border-b-2 transition-colors {activeTab === 'invite'
                    ? 'border-blue-600 text-blue-600 dark:text-blue-400 dark:border-blue-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'}"
            >
                <UserPlus class="h-4 w-4" />
                Invite Member
            </button>
        </div>

        <!-- ---------------------------------------------------------------- -->
        <!-- Tab: Logo                                                         -->
        <!-- ---------------------------------------------------------------- -->
        {#if activeTab === "logo"}
            <div class="space-y-3">
                <p class="text-sm text-gray-500 dark:text-gray-400">
                    Upload a PNG, JPEG, WebP, GIF, or SVG logo (max 5 MB).
                    It will appear on the home screen for all team members.
                </p>

                <!-- Preview -->
                {#if logoPreviewUrl}
                    <div class="flex justify-center">
                        <img
                            src={logoPreviewUrl}
                            alt="Logo preview"
                            class="h-24 object-contain rounded border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-2"
                        />
                    </div>
                {:else if $tenantLogoUrl}
                    <div class="flex flex-col items-center gap-1">
                        <p class="text-xs text-gray-400 dark:text-gray-500 uppercase font-semibold">Current logo</p>
                        <img
                            src={$tenantLogoUrl}
                            alt="Current tenant logo"
                            class="h-20 object-contain rounded border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-2"
                        />
                    </div>
                {/if}

                <div>
                    <label
                        class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1"
                        for="logo-file"
                    >
                        Choose image
                    </label>
                    <input
                        id="logo-file"
                        type="file"
                        accept="image/png,image/jpeg,image/gif,image/webp,image/svg+xml"
                        onchange={onLogoChange}
                        class="w-full text-sm text-gray-700 dark:text-gray-300 file:mr-3 file:py-1.5 file:px-3 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-gray-700 dark:file:text-gray-200"
                    />
                </div>

                <button
                    type="button"
                    onclick={submitLogo}
                    disabled={logoLoading || !logoFile}
                    class="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded-md text-sm transition-colors"
                >
                    {logoLoading ? "Uploading…" : "Upload Logo"}
                </button>
            </div>
        {/if}

        <!-- ---------------------------------------------------------------- -->
        <!-- Tab: Invite Member                                                -->
        <!-- ---------------------------------------------------------------- -->
        {#if activeTab === "invite"}
            <div class="space-y-3">
                <p class="text-sm text-gray-500 dark:text-gray-400">
                    Invite someone to your organisation. A magic-link will be
                    emailed to them so they can log in straight away.
                </p>

                <!-- Email -->
                <div>
                    <label
                        class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1"
                        for="tm-invite-email"
                    >
                        Email
                    </label>
                    <input
                        id="tm-invite-email"
                        type="email"
                        bind:value={inviteEmail}
                        placeholder="user@example.com"
                        class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm"
                    />
                </div>

                <!-- Role -->
                <div>
                    <label
                        class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1"
                        for="tm-invite-position"
                    >
                        Role
                    </label>
                    <select
                        id="tm-invite-position"
                        bind:value={invitePosition}
                        class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm"
                    >
                        <option value="employee">Employee</option>
                        <option value="mechanic">Mechanic</option>
                        <option value="master">Supervisor (Master)</option>
                    </select>
                </div>

                <!-- Language -->
                <div>
                    <label
                        class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1"
                        for="tm-invite-language"
                    >
                        Language
                    </label>
                    <select
                        id="tm-invite-language"
                        bind:value={inviteLanguage}
                        class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm"
                    >
                        {#each languages as { code, label }}
                            <option value={code}>{label}</option>
                        {/each}
                    </select>
                </div>

                <!-- Send invite checkbox -->
                <label class="flex items-center gap-2 cursor-pointer text-sm text-gray-700 dark:text-gray-300">
                    <input
                        type="checkbox"
                        bind:checked={inviteSendEmail}
                        class="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-400"
                    />
                    Send magic-link invite email
                </label>

                <button
                    type="button"
                    onclick={submitInvite}
                    disabled={inviteLoading}
                    class="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded-md text-sm transition-colors"
                >
                    {inviteLoading ? "Inviting…" : "Invite Member"}
                </button>
            </div>
        {/if}

    </div>
</Drawer>
