<script lang="ts">
    import ArrowLeft from "lucide-svelte/icons/arrow-left";
    import LogOut from "lucide-svelte/icons/log-out";
    import LogIn from "lucide-svelte/icons/log-in";
    import Button from "flowbite-svelte/Button.svelte";
    import Drawer from "flowbite-svelte/Drawer.svelte";
    import Spinner from "flowbite-svelte/Spinner.svelte";
    import { notify } from "$lib/helpers/notify";
    import { langChecker, languages, translations } from "$lib/locales";
    import store from "$lib/store";
    import { sineIn } from "svelte/easing";
    import RoleTester from "./RoleTester.svelte";
    import { writable } from "svelte/store";
    import { login, logout } from "$lib/helpers/server-requests";
    import { onDestroy } from "svelte";

    let email = "";
    let isLoading = writable(false);

    const {
        isLoggedIn,
        isAuthDrawerHidden,
        selectedLanguage,
        darkModeEnabled,
    } = store;

    const transitionParamsBottom = {
        y: 320,
        duration: 200,
        easing: sineIn,
    };

    function t(key: string): string {
        const langTranslations = translations[$selectedLanguage];
        langChecker(key);
        return langTranslations?.[key] || key;
    }

    onDestroy(() => {
        isAuthDrawerHidden.set(true);
    });

    async function handleSubmit(e: Event) {
        e.preventDefault();
        if (!email) {
            notify("Error", "Please enter a valid email address.", "error");
        } else {
            isLoading.set(true);
            const isLoggedSuccess = await login(email);
            isLoading.set(false);
            console.log("isLoggedSuccess", isLoggedSuccess);
            if (isLoggedSuccess) {
                console.log("Login Response Message:", isLoggedSuccess.message);
                const successMessage = t("Email sent to {email}").replace(
                    "{email}",
                    email,
                );
                notify("Success", successMessage, "success");
                isAuthDrawerHidden.set(true);
            } else {
                notify("Error", "Could not login.", "error");
            }
        }
    }
</script>

<Drawer
    id="auth-drawer"
    placement="bottom"
    bind:hidden={$isAuthDrawerHidden}
    activateClickOutside={false}
    backdrop={true}
    class="drawer-box p-6 md:p-8 bg-gray-100 rounded-lg shadow-lg max-w-[600px] m-auto"
    width="w-full"
    transitionType="fly"
    transitionParams={transitionParamsBottom}
>
    {#if $isLoading}
        <div class="flex justify-center space-y-4 p-4 pt-5">
            <Spinner color="blue" class="w-14 h-14" />
        </div>
    {/if}
    <div class="flex items-center justify-between {$isLoading ? 'hidden' : ''}">
        <button
            type="button"
            onclick={() => isAuthDrawerHidden.set(true)}
            class="p-2 hover:bg-gray-200 rounded-md"
        >
            <ArrowLeft class="h-6 w-6 text-gray-800" />
        </button>
    </div>

    <div class={!$isLoggedIn || $isLoading ? "hidden" : ""}><RoleTester /></div>

    <div class="mt-6 {$isLoggedIn || $isLoading ? 'hidden' : ''}">
        <div class="flex flex-col items-center">
            <div class="mt-2 bg-white p-6 rounded-lg shadow-lg">
                <h2 class="text-2xl font-semibold text-gray-800">
                    {t("Authentication")}
                </h2>

                <div class="mt-4">
                    <div class="form-group">
                        <label for="language-selector">{t("Language")}</label>
                        <select
                            id="language-selector"
                            bind:value={$selectedLanguage}
                            onchange={() => {
                                localStorage.setItem(
                                    "savedLang",
                                    $selectedLanguage,
                                );
                            }}
                        >
                            {#each languages as { code, label }}
                                <option value={code}>{label}</option>
                            {/each}
                        </select>
                    </div>
                </div>

                <form onsubmit={handleSubmit} class="mt-4">
                    <div class="form-group">
                        <label for="email">{t("Email")}</label>
                        <input
                            id="email"
                            type="email"
                            bind:value={email}
                            placeholder={t("Enter your email")}
                            required
                        />
                    </div>

                    <div class="form-footer mt-6">
                        <button
                            type="submit"
                            class="btn"
                            style="filter: invert({$darkModeEnabled
                                ? '1'
                                : '0'});">{t("Submit")}</button
                        >
                    </div>
                </form>
            </div>
        </div>
    </div>

    <div class="mt-6 flex {$isLoading ? 'hidden' : ''} justify-between">
        <Button
            on:click={async () => {
                isLoading.set(true);
                const didLogout = await logout();
                // if (!didLogout) isLoading.set(false);
                location.reload();
                // if (window.location.hostname === "localhost")
                //     return location.reload();
                // if (didLogout) {
                //     location.reload();
                // } else {
                //     isLoading.set(false);
                // }
            }}
            class="bg-red-500 hover:bg-red-600 text-white rounded-full px-6 py-2{!$isLoggedIn
                ? ' hidden'
                : ''}"
            style="filter: invert({$darkModeEnabled ? '1' : '0'});"
        >
            {t("Logout")}
            <LogOut class="w-4 h-4 ml-2" />
        </Button>
        <Button
            on:click={async () => {
                isLoading.set(true);

                document.cookie = "auth=true;";
                location.reload();
            }}
            class="bg-blue-500 hover:bg-blue-600 text-white rounded-full px-6 py-2{$isLoggedIn
                ? ' hidden'
                : ''}"
            style="filter: invert({$darkModeEnabled ? '1' : '0'});"
        >
            {t("Login as Guest")}
            <LogIn class="w-4 h-4 ml-2" />
        </Button>
    </div>
</Drawer>

<style>
    .form-group {
        margin-bottom: 1rem;
    }
    .form-group label {
        font-size: 0.875rem;
        display: block;
        margin-bottom: 0.5rem;
    }
    .form-group input,
    .form-group select {
        width: 100%;
        padding: 0.75rem;
        font-size: 1rem;
        color: #fff;
        background: #333;
        border: 1px solid #444;
        border-radius: 4px;
    }
    .form-group input:focus,
    .form-group select:focus {
        outline: none;
        border-color: #007bff;
        box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
    }
    .form-footer {
        margin-top: 1rem;
    }
    .btn {
        width: 100%;
        padding: 0.75rem;
        font-size: 1rem;
        font-weight: bold;
        color: #fff;
        background: #007bff;
        border: none;
        border-radius: 4px;
        cursor: pointer;
    }
    .btn:hover {
        background: #0056b3;
    }
</style>
