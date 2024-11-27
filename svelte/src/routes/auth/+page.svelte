<script lang="ts">
    import { onMount } from "svelte";
    import { toast } from "svelte-sonner";
    import { Toaster } from "$lib/components/ui/sonner/index.js";
    import type { TranslationKeys } from "$lib/locales"; 
    import { translations } from "$lib/locales";

    let authMode: "email" | "credentials" = "email";
    let email = "";
    let username = "";
    let password = "";
    let selectedLanguage: keyof typeof translations = "en";

    const languages = [
        { code: "en", label: "English" },
        { code: "da", label: "Dansk" },
        { code: "no", label: "Norsk" },
        { code: "sv", label: "Svenska" },
    ];

function t(key: TranslationKeys): string {
    const langTranslations = translations[selectedLanguage];
    return langTranslations[key] || key;
}


    function handleSubmit() {
        if (authMode === "email" && !email) {
            toast.error(t("emailError"));
        } else if (authMode === "credentials" && (!username || !password)) {
            toast.error(t("credentialsError"));
        } else {
            const successMessage =
                authMode === "email"
                    ? t("emailSuccess").replace("{email}", email)
                    : t("loginSuccess");
            toast.success(successMessage);
        }
    }

    onMount(() => {
        console.log("Component mounted in the client");
    });
</script>


<div class="container">
    <Toaster />
    <div class="form">
        <div class="form-header">{t("authHeader")}</div>

        <div class="form-group">
            <label for="language-selector">{t("languageLabel")}</label>
            <select id="language-selector" bind:value={selectedLanguage}>
                {#each languages as { code, label }}
                    <option value={code}>{label}</option>
                {/each}
            </select>
        </div>

        <form on:submit|preventDefault={handleSubmit}>
            {#if authMode === "email"}
                <div class="form-group">
                    <label for="email">{t("emailLabel")}</label>
                    <input
                        id="email"
                        type="email"
                        bind:value={email}
                        placeholder={t("emailPlaceholder")}
                    />
                </div>
            {:else}
                <div class="form-group">
                    <label for="username">{t("usernameLabel")}</label>
                    <input
                        id="username"
                        type="text"
                        bind:value={username}
                        placeholder={t("usernamePlaceholder")}
                    />
                </div>
                <div class="form-group">
                    <label for="password">{t("passwordLabel")}</label>
                    <input
                        id="password"
                        type="password"
                        bind:value={password}
                        placeholder={t("passwordPlaceholder")}
                    />
                </div>
            {/if}

            <div class="form-footer">
                <button type="submit" class="btn">{t("submitButton")}</button>
                <span
                    class="toggle-link"
                    tabindex="0"
                    role="button"
                    on:click={() =>
                        (authMode = authMode === "email" ? "credentials" : "email")}
                    on:keydown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                            e.preventDefault();
                            authMode = authMode === "email" ? "credentials" : "email";
                        }
                    }}
                >
                    {authMode === "email" ? t("toggleToCredentials") : t("toggleToEmail")}
                </span>
            </div>
        </form>
    </div>
</div>

<style>
    .container {
        padding: 1rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        background-color: #1a1a1a;
        color: #f9f9f9;
    }
    .form {
        width: 100%;
        max-width: 400px;
        padding: 1.5rem;
        background: #2a2a2a;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .form-header {
        margin-bottom: 1.5rem;
        text-align: center;
        font-size: 1.25rem;
        font-weight: bold;
    }
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
