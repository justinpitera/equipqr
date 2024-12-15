<script lang="ts">
    import Drawer from "flowbite-svelte/Drawer.svelte";
    import ArrowLeft from 'lucide-svelte/icons/arrow-left'
    import Plane from 'lucide-svelte/icons/plane'
    import X from 'lucide-svelte/icons/x'
    import CheckOutline from "flowbite-svelte-icons/CheckOutline.svelte";
    import { homePageStore } from "$lib/helpers/homepage";
    import {
        build_gate_options,
        gate_types,
        reportUIStore,
    } from "$lib/helpers/report-ui-store";
    const { isPastIssuesForSpecificIDHidden } = homePageStore;
    import { langChecker, translations } from "$lib/locales";
    import { onDestroy } from "svelte";
    const { selectedLanguage, darkModeEnabled } = homePageStore;

    function t(key: string): string {
        const langTranslations = translations[$selectedLanguage];
        langChecker(key);
        return langTranslations?.[key] || key;
    }
    const {
        issue_description,
        operable,
        selected_gate_type,
        selected_gate_name,
    } = reportUIStore;

    let issues: PastIssue[] = Array.from({ length: 20 }, (_, i) => ({
        gse_id: i + 1,
        worker_id: `${t('Employee')} ${i + 1}`,
        issue_description: `${t('Issue description')} ${i + 1}`,
        is_operable: i % 2 === 0 ? "Yes" : "No",
        date: Date.now(),
    }));

    issues.forEach((issue) => {
        if (issue.is_operable === "No") {
            const gate_keys = Object.keys(gate_types);
            const selected_gate_type =
                gate_keys[Math.floor(Math.random() * gate_keys.length)];
            issue.gate_type = selected_gate_type;
            issue.gate_name =
                gate_types[selected_gate_type][
                    Math.floor(
                        Math.random() * gate_types[selected_gate_type].length,
                    )
                ];
        }
    });

    const selectIssue = (issueId: number): void => {
        const issue = issues.find((i) => i.gse_id === issueId);
        if (issue) {
            isPastIssuesForSpecificIDHidden.set(true);
            issue_description.set(issue.issue_description);
            operable.set(issue.is_operable.toLowerCase());
            if (issue.gate_type) {
                const gate_type = issue.gate_type.toLowerCase();
                selected_gate_type.set(gate_type);
                if (issue.gate_name) {
                    build_gate_options(gate_type, issue.gate_name);
                    selected_gate_name.set(issue.gate_name);
                } else {
                    selected_gate_name.set("");
                    build_gate_options(gate_type);
                }
            } else {
                selected_gate_type.set("");
            }
        }
    };
    onDestroy(() => {
        isPastIssuesForSpecificIDHidden.set(true);
    });
</script>

<!-- Past Issues Drawer -->
<Drawer
    id="past-issues-drawer"
    placement="right"
    bind:hidden={$isPastIssuesForSpecificIDHidden}
    backdrop={true}
    class="drawer-box p-6 md:p-8 bg-white rounded-lg shadow-lg"
    width="w-80"
    transitionParams={{
        duration: 0,
        easing: undefined,
    }}
>
    <div class="flex items-center justify-between">
        <h2 class="text-lg font-bold text-gray-800">{t("Past Issues")}</h2>
        <button
            type="button"
            onclick={() => isPastIssuesForSpecificIDHidden.set(true)}
            class="p-2 hover:bg-gray-200 rounded-md"
        >
            <ArrowLeft class="h-5 w-5 text-gray-800" />
        </button>
    </div>

    <div class="mt-4 overflow-y-auto max-h-[calc(97svh-76px-15px)] space-y-2">
        {#each issues as issue (issue.gse_id)}
            <div
                class="p-3 bg-gray-100 rounded-lg hover:bg-gray-200 cursor-pointer transition relative flex items-center justify-between"
                onclick={() => selectIssue(issue.gse_id)}
                onkeypress={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                        selectIssue(issue.gse_id);
                    }
                }}
                tabindex="0"
                role="button"
            >
                <!-- Issue Details -->
                <div>
                    <h3 class="text-md font-semibold">{issue.worker_id}</h3>
                    <p class="text-sm text-gray-500 flex items-center">
                        {t("Operable:")}
                        {#if issue.is_operable.toLowerCase() === "yes"}
                            <CheckOutline
                                class="ml-2 h-4 w-4 text-green-500"
                                style="filter: invert({$darkModeEnabled
                                    ? '1'
                                    : '0'});"
                            />
                        {:else}
                            <X
                                class="ml-2 h-4 w-4 text-red-500"
                                style="filter: invert({$darkModeEnabled
                                    ? '1'
                                    : '0'});"
                            />
                        {/if}
                    </p>
                    <p class="text-sm text-gray-600">
                        {issue.issue_description}
                    </p>
                </div>
                <!-- Gate Badge -->
                {#if issue.gate_type && issue.gate_name}
                    <div
                        class="flex items-center bg-yellow-300 border-2 border-navy-800 rounded-md px-2 py-1 ml-3 text-navy-900 shadow-sm"
                        style="width: fit-content; min-width: fit-content;filter: invert({$darkModeEnabled
                            ? '1'
                            : '0'});"
                    >
                        <!-- Airplane Icon -->
                        <div class="flex-shrink-0 rounded-md bg-yellow-400 p-1">
                            <Plane class="h-3 w-3 text-navy-800" />
                        </div>
                        <!-- Gate Info -->
                        <div class="ml-2 text-xs font-bold">
                            <p>{issue.gate_type}</p>
                            <p>{issue.gate_name}</p>
                        </div>
                    </div>
                {/if}
            </div>
        {/each}
    </div>
</Drawer>
