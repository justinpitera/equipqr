<script lang="ts">
    import { homePageStore } from "$lib/helpers/homepage";
    import { notify } from "$lib/helpers/notify";
    const { isAuthDrawerHidden } = homePageStore;

    const { userRole } = homePageStore;

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
    <h4 class="text-2xl font-semibold text-gray-800 dark:text-white">
        Set User Role for Testing
    </h4>
    <p class="text-lg text-gray-600 dark:text-gray-400 mt-2">
        Choose a role below to simulate different user experiences
    </p>
</div>

<div class="grid gap-5 md:grid-cols-3">
    <!-- Set Role to Employee -->
    <div class="card p-1 pt-1 bg-white rounded-lg shadow-md">
        <button class="button" onclick={() => setRole("employee")}>
            Set Role to Employee
        </button>
    </div>

    <!-- Set Role to Mechanic -->
    <div class="card p-1 pt-1 bg-white rounded-lg shadow-md">
        <button class="button" onclick={() => setRole("mechanic")}>
            Set Role to Mechanic
        </button>
    </div>

    <!-- Set Role to Master -->
    <div class="card p-1 pt-1 bg-white rounded-lg shadow-md">
        <button class="button" onclick={() => setRole("master")}>
            Set Role to Master
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

    .card-content {
        text-align: center;
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
