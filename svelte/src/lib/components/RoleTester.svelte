<script lang="ts">
    import { homePageStore } from "$lib/helpers/homepage";
    import { notify } from "$lib/helpers/notify";
    import { langChecker, translations } from "$lib/locales";
    const { isAuthDrawerHidden, selectedLanguage, userRole } = homePageStore;

    function t(key: string): string {
        const langTranslations = translations[$selectedLanguage];
        langChecker(key);
        return langTranslations?.[key] || key;
    }

    const setRole = (role: string) => {
        userRole.set(role);
        notify(
            "Success",
            `Role has been updated to ${role} successfully.`,
            "success",
        );
        isAuthDrawerHidden.set(true);
    };
</script>

<div class="text-center mb-4">
    <h4 class="text-xl font-semibold text-gray-800 dark:text-white">
        {t("Set User Role for Testing")}
    </h4>
    <p class="text-lg text-gray-600 dark:text-gray-400 mt-2">
        {t("Choose a role below to simulate different user experiences")}
    </p>
</div>

<div class="grid gap-1 md:grid-cols-3">
    <!-- Set Role to Employee -->
    <div class="card p-1 bg-white rounded-lg shadow-md">
        <button class="button" onclick={() => setRole("employee")}>
            {t("Set Role to Employee")}
        </button>
    </div>

    <!-- Set Role to Mechanic -->
    <div class="card p-1 bg-white rounded-lg shadow-md">
        <button class="button" onclick={() => setRole("mechanic")}>
            {t("Set Role to Mechanic")}
        </button>
    </div>

    <!-- Set Role to Master -->
    <div class="card p-1 bg-white rounded-lg shadow-md">
        <button class="button" onclick={() => setRole("master")}>
            {t("Set Role to Master")}
        </button>
    </div>
</div>

<style>
    .card {
        transition: all 0.3s ease;
    }

    .card:hover {
        background-color: #f1f5f9;
        cursor: pointer;
    }

    .button {
        padding: 0.75rem 1.5rem;
        border-radius: 0.375rem;
        background-color: #003965;
        color: #fff;
        border: none;
        font-size: 1rem;
        cursor: pointer;
        transition: background-color 0.3s ease;
        width: 100%;
    }

    .button:hover {
        background-color: #1d4ed8;
    }
</style>
