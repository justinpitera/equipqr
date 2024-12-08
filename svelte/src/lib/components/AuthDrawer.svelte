<script lang="ts">
    import { ArrowLeft } from "lucide-svelte";
    import { Button, Drawer } from "flowbite-svelte";
    import { notify } from "$lib/helpers/notify";
    import { langChecker, languages, translations } from "$lib/locales";
    import { homePageStore } from "$lib/helpers/homepage";
    import { sineIn } from "svelte/easing";
    import RoleTester from "./RoleTester.svelte";

    let authMode: "email" | "credentials" = "email";
    let email = "";
    let username = "";
    let password = "";

    const { isLoggedIn, isAuthDrawerHidden, selectedLanguage } = homePageStore;

    const transitionParamsBottom = {
        y: 320,
        duration: 200,
        easing: sineIn,
    };

    function t(key: string): string {
        const langTranslations = translations[$selectedLanguage];
        langChecker(key);
        return langTranslations[key] || key;
    }

    function handleSubmit(e: Event) {
        e.preventDefault();
        if (authMode === "email" && !email) {
            notify("Error", t("Please enter a valid email address."), "error");
        } else if (authMode === "credentials" && (!username || !password)) {
            notify(
                "Error",
                t("Please provide both username and password."),
                "error",
            );
        } else {
            const successMessage =
                authMode === "email"
                    ? t("Email sent to {email}").replace("{email}", email)
                    : t("Login successful!");
            notify("Success", successMessage, "success");
            isLoggedIn.set(!$isLoggedIn);
            isAuthDrawerHidden.set(true);
        }
    }
</script>

<Drawer
    id="auth-drawer"
    placement="bottom"
    bind:hidden={$isAuthDrawerHidden}
    on:close={() => isAuthDrawerHidden.set(true)}
    backdrop={true}
    class="p-6 md:p-8 bg-gray-100 rounded-lg shadow-lg"
    width="w-full"
    transitionType="fly"
    transitionParams={transitionParamsBottom}
>
    <div class="flex items-center justify-between">
        <button
            type="button"
            onclick={() => isAuthDrawerHidden.set(true)}
            class="p-2 hover:bg-gray-200 rounded-md"
        >
            <ArrowLeft class="h-6 w-6 text-gray-800" />
        </button>
    </div>

    <RoleTester />
    <div class="mt-6">
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
                        >
                            {#each languages as { code, label }}
                                <option value={code}>{label}</option>
                            {/each}
                        </select>
                    </div>
                </div>

                <form onsubmit={handleSubmit} class="mt-4">
                    {#if authMode === "email"}
                        <div class="form-group">
                            <label for="email">{t("Email")}</label>
                            <input
                                id="email"
                                type="email"
                                bind:value={email}
                                placeholder={t("Enter your email")}
                            />
                        </div>
                    {:else}
                        <div class="form-group">
                            <label for="username">{t("Username")}</label>
                            <input
                                id="username"
                                type="text"
                                bind:value={username}
                                placeholder={t("Enter your username")}
                            />
                        </div>
                        <div class="form-group">
                            <label for="password">{t("Password")}</label>
                            <input
                                id="password"
                                type="password"
                                bind:value={password}
                                placeholder={t("Enter your password")}
                            />
                        </div>
                    {/if}

                    <div class="form-footer mt-6">
                        <button type="submit" class="btn">{t("Submit")}</button>
                        <span
                            class="toggle-link"
                            tabindex="0"
                            role="button"
                            onclick={() =>
                                (authMode =
                                    authMode === "email"
                                        ? "credentials"
                                        : "email")}
                            onkeydown={(e) => {
                                if (e.key === "Enter" || e.key === " ") {
                                    e.preventDefault();
                                    authMode =
                                        authMode === "email"
                                            ? "credentials"
                                            : "email";
                                }
                            }}
                        >
                            {authMode === "email"
                                ? t("Switch to Credentials Login")
                                : t("Switch to Email Login")}
                        </span>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <div class="mt-6 flex">
        <Button
            on:click={() => isAuthDrawerHidden.set(true)}
            class="bg-blue-500 hover:bg-blue-600 text-white rounded-full px-6 py-2"
        >
            Close
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
    .toggle-link {
        display: block;
        margin-top: 1rem;
        font-size: 0.875rem;
        text-align: center;
        color: #007bff;
        cursor: pointer;
    }
</style>
