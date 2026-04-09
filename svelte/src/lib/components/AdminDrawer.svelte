<script lang="ts">
    import ArrowLeft from "lucide-svelte/icons/arrow-left";
    import Building2 from "lucide-svelte/icons/building-2";
    import UserPlus from "lucide-svelte/icons/user-plus";
    import Drawer from "flowbite-svelte/Drawer.svelte";
    import { flyTransitionParamsBottom } from "$lib/helpers/fly";
    import { notify } from "$lib/helpers/notify";
    import { adminCreateTenant, adminInviteUser } from "$lib/helpers/server-requests";
    import store from "$lib/store";

    const { isAdminDrawerHidden } = store;

    // -----------------------------------------------------------------------
    // Shared state
    // -----------------------------------------------------------------------
    type Tab = "tenant" | "invite";
    let activeTab: Tab = "tenant";

    // The admin secret is kept in-memory only (never written to localStorage).
    let adminSecret = "";

    // -----------------------------------------------------------------------
    // Create Tenant form
    // -----------------------------------------------------------------------
    let tenantName = "";
    let tenantSlug = "";
    let tenantLoading = false;

    // Auto-derive slug from name (lowercase, spaces → dashes, strip non-alphanumeric)
    function deriveSlug(name: string): string {
        return name
            .toLowerCase()
            .trim()
            .replace(/\s+/g, "-")
            .replace(/[^a-z0-9-]/g, "")
            .replace(/^-+|-+$/g, "");
    }

    function onTenantNameInput() {
        tenantSlug = deriveSlug(tenantName);
    }

    async function submitTenant() {
        if (!adminSecret) { notify("Missing secret", "Enter the admin secret first.", "warning", 4000, true); return; }
        if (!tenantName.trim()) { notify("Missing name", "Tenant name is required.", "warning", 4000, true); return; }
        if (!tenantSlug.trim()) { notify("Missing slug", "Tenant slug is required.", "warning", 4000, true); return; }

        tenantLoading = true;
        const result = await adminCreateTenant(adminSecret, tenantName.trim(), tenantSlug.trim());
        tenantLoading = false;

        if ("error" in result) {
            notify("Error", result.error, "error", 6000, true);
        } else {
            notify("Tenant created", `"${result.name}" (${result.slug}) created successfully.`, "success", 5000, true);
            tenantName = "";
            tenantSlug = "";
        }
    }

    // -----------------------------------------------------------------------
    // Invite User form
    // -----------------------------------------------------------------------
    let inviteEmail = "";
    let inviteTenantSlug = "";
    let invitePosition = "employee";
    let inviteLanguage = "en";
    let inviteSendEmail = true;
    let inviteLoading = false;

    async function submitInvite() {
        if (!adminSecret) { notify("Missing secret", "Enter the admin secret first.", "warning", 4000, true); return; }
        if (!inviteEmail.trim() || !inviteEmail.includes("@")) { notify("Invalid email", "Enter a valid email address.", "warning", 4000, true); return; }
        if (!inviteTenantSlug.trim()) { notify("Missing tenant", "Enter the tenant slug.", "warning", 4000, true); return; }

        inviteLoading = true;
        const result = await adminInviteUser(
            adminSecret,
            inviteEmail.trim().toLowerCase(),
            inviteTenantSlug.trim().toLowerCase(),
            invitePosition,
            inviteLanguage,
            inviteSendEmail,
        );
        inviteLoading = false;

        if ("error" in result) {
            notify("Error", result.error, "error", 6000, true);
        } else {
            const msg = inviteSendEmail
                ? `Invite sent to ${result.email}.`
                : `${result.email} added (no invite sent).`;
            notify("User invited", msg, "success", 5000, true);
            inviteEmail = "";
        }
    }
</script>

<Drawer
    id="admin-drawer"
    placement="bottom"
    bind:hidden={$isAdminDrawerHidden}
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
            onclick={() => isAdminDrawerHidden.set(true)}
            class="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-md"
        >
            <ArrowLeft class="h-6 w-6 text-gray-800 dark:text-white" />
        </button>
        <h2 class="text-xl font-bold text-gray-800 dark:text-white">Admin</h2>
        <div class="w-10"></div><!-- spacer -->
    </div>

    <div class="p-4 space-y-4 overflow-y-auto max-h-[80vh]">
        <!-- Admin Secret -->
        <div>
            <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1" for="admin-secret">
                Admin Secret
            </label>
            <input
                id="admin-secret"
                type="password"
                bind:value={adminSecret}
                placeholder="••••••••"
                class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm"
            />
        </div>

        <!-- Tabs -->
        <div class="flex gap-2 border-b border-gray-200 dark:border-gray-700">
            <button
                type="button"
                onclick={() => activeTab = "tenant"}
                class="flex items-center gap-1.5 px-4 py-2 text-sm font-medium border-b-2 transition-colors {activeTab === 'tenant'
                    ? 'border-blue-600 text-blue-600 dark:text-blue-400 dark:border-blue-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'}"
            >
                <Building2 class="h-4 w-4" />
                New Tenant
            </button>
            <button
                type="button"
                onclick={() => activeTab = "invite"}
                class="flex items-center gap-1.5 px-4 py-2 text-sm font-medium border-b-2 transition-colors {activeTab === 'invite'
                    ? 'border-blue-600 text-blue-600 dark:text-blue-400 dark:border-blue-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'}"
            >
                <UserPlus class="h-4 w-4" />
                Invite User
            </button>
        </div>

        <!-- ---------------------------------------------------------------- -->
        <!-- Tab: New Tenant                                                   -->
        <!-- ---------------------------------------------------------------- -->
        {#if activeTab === "tenant"}
            <div class="space-y-3">
                <div>
                    <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1" for="tenant-name">
                        Tenant Name
                    </label>
                    <input
                        id="tenant-name"
                        type="text"
                        bind:value={tenantName}
                        oninput={onTenantNameInput}
                        placeholder="Acme Airlines"
                        class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm"
                    />
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1" for="tenant-slug">
                        Slug <span class="normal-case text-gray-400 font-normal">(subdomain, e.g. acme)</span>
                    </label>
                    <input
                        id="tenant-slug"
                        type="text"
                        bind:value={tenantSlug}
                        placeholder="acme"
                        class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm font-mono"
                    />
                </div>
                <button
                    type="button"
                    onclick={submitTenant}
                    disabled={tenantLoading}
                    class="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded-md text-sm transition-colors"
                >
                    {tenantLoading ? "Creating…" : "Create Tenant"}
                </button>
            </div>
        {/if}

        <!-- ---------------------------------------------------------------- -->
        <!-- Tab: Invite User                                                  -->
        <!-- ---------------------------------------------------------------- -->
        {#if activeTab === "invite"}
            <div class="space-y-3">
                <div>
                    <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1" for="invite-email">
                        Email
                    </label>
                    <input
                        id="invite-email"
                        type="email"
                        bind:value={inviteEmail}
                        placeholder="user@example.com"
                        class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm"
                    />
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1" for="invite-tenant">
                        Tenant Slug
                    </label>
                    <input
                        id="invite-tenant"
                        type="text"
                        bind:value={inviteTenantSlug}
                        placeholder="acme"
                        class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm font-mono"
                    />
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1" for="invite-position">
                        Role
                    </label>
                    <select
                        id="invite-position"
                        bind:value={invitePosition}
                        class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm"
                    >
                        <option value="employee">Employee</option>
                        <option value="mechanic">Mechanic</option>
                        <option value="master">Supervisor (Master)</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1" for="invite-language">
                        Language
                    </label>
                    <select
                        id="invite-language"
                        bind:value={inviteLanguage}
                        class="w-full px-3 py-2 border rounded-md bg-white dark:bg-gray-800 dark:text-white dark:border-gray-600 focus:ring-2 focus:ring-blue-400 text-sm"
                    >
                        <option value="en">English</option>
                        <option value="da">Dansk</option>
                        <option value="no">Norsk</option>
                        <option value="sv">Svenska</option>
                    </select>
                </div>
                <label class="flex items-center gap-2 cursor-pointer select-none">
                    <input type="checkbox" bind:checked={inviteSendEmail} class="w-4 h-4 rounded accent-blue-600" />
                    <span class="text-sm text-gray-700 dark:text-gray-300">Send magic-link invite email</span>
                </label>
                <button
                    type="button"
                    onclick={submitInvite}
                    disabled={inviteLoading}
                    class="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold rounded-md text-sm transition-colors"
                >
                    {inviteLoading ? "Sending…" : (inviteSendEmail ? "Add & Send Invite" : "Add User")}
                </button>
            </div>
        {/if}
    </div>
</Drawer>
