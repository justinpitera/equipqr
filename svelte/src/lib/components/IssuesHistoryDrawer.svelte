<script lang="ts">
    import { Button, Drawer } from "flowbite-svelte";
    import { Trash2, Edit, ArrowLeft } from "lucide-svelte";
    import { homePageStore } from "$lib/helpers/homepage";
    import { langChecker, translations } from "$lib/locales";
    const { selectedLanguage, isIssuesHistoryHidden } = homePageStore;

    function t(key: string): string {
        const langTranslations = translations[$selectedLanguage];
        langChecker(key);
        return langTranslations?.[key] || key;
    }

    interface Issue {
        id: number;
        name: string;
        issue: string;
        operable: string;
        files: string[];
    }

    let issues: Issue[] = [
        {
            id: 1,
            name: "John",
            issue: t("Broken screen"),
            operable: t("No"),
            files: ["file1.jpg", "file2.jpg"],
        },
        {
            id: 2,
            name: "Jane",
            issue: t("Battery not charging"),
            operable: t("Yes"),
            files: ["battery.jpg"],
        },
    ];

    let formData = {
        name: "",
        issue: "",
        operable: "",
        files: [] as File[],
    };

    const toggleIssueDetails = (issueId: number): void => {
        const issue = issues.find((i) => i.id === issueId);
        if (issue) {
            console.log("Viewing issue details:", issue);
        }
    };
</script>

<!-- Issues History Drawer -->
<Drawer
    id="issue-history-drawer"
    placement="right"
    bind:hidden={$isIssuesHistoryHidden}
    backdrop={true}
    class="p-6 md:p-8 bg-white rounded-lg shadow-lg"
    width="w-full"
>
    <div class="flex items-center justify-between">
        <h2 class="text-xl font-bold text-gray-800">{t("Issues History")}</h2>
        <button
            type="button"
            onclick={() => isIssuesHistoryHidden.set(true)}
            class="p-2 hover:bg-gray-200 rounded-md"
        >
            <ArrowLeft class="h-6 w-6 text-gray-800" />
        </button>
    </div>

    <div class="mt-6 space-y-4">
        {#each issues as issue (issue.id)}
            <div
                class="flex items-center justify-between border-b border-gray-300 pb-4"
            >
                <div class="flex-1">
                    <h3 class="text-lg font-semibold">{issue.name}</h3>
                    <p class="text-gray-600">{issue.issue}</p>
                    <p class="text-gray-500">{t("Operable:")} {issue.operable}</p>
                </div>
                <div class="flex items-center gap-2">
                    <Button
                        on:click={() => toggleIssueDetails(issue.id)}
                        class="text-white">{t("View Details")}</Button
                    >
                    <button class="text-red-600">
                        <Trash2 class="h-5 w-5" />
                    </button>
                    <button class="text-yellow-600">
                        <Edit class="h-5 w-5" />
                    </button>
                </div>
            </div>
        {/each}
    </div>
</Drawer>
