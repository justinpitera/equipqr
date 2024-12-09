import { writable, type Writable } from "svelte/store";

class ReportUIStore {
    constructor(
        public employee_name: Writable<string> = writable(''),
        public issue_description: Writable<string> = writable(''),
        public operable: Writable<string> = writable(''),
        public selected_gate_type: Writable<string> = writable(''),
        public selected_gate_name: Writable<string> = writable(''),
        public is_gate_type_dropdown_open: Writable<boolean> = writable(false),
        public showSuccessStamp: Writable<boolean> = writable(false),
        public gates: Writable<{ value: string; name: string }[]> = writable([]),
    ) { }
}

export const reportUIStore = new ReportUIStore();

export let gate_types: Record<string, string[]> = {
    GA: ["103 Apn"],
    Airline: ["A11"],
    None: ["G110"],
    Cargo: ["G126"],
};

export function build_gate_options(gate: string, forceSelect?: string) {
    reportUIStore.selected_gate_type.set(gate);
    reportUIStore.is_gate_type_dropdown_open.set(false);
    reportUIStore.gates.set([]);
    reportUIStore.gates.update((currentGates) => {
        for (const gate_type in gate_types) {
            if (gate_type.toLowerCase() !== gate.toLowerCase()) continue;
            const gate_names = gate_types[gate_type];
            for (const gate_name of gate_names) {
                currentGates.push({
                    value: gate_name,
                    name: gate_name,
                });
            }
        }
        return currentGates;
    });
    setTimeout(() => {
        const selectGateName = document.getElementById("select-gate-name") as HTMLSelectElement;
        if (selectGateName) {
            if (forceSelect) {
                selectGateName.selectedIndex = 0;
                let i = 0;
                for (const option of selectGateName.getElementsByTagName('option')) {
                    if (option.value === forceSelect) selectGateName.selectedIndex = i;
                    i += 1;
                }
            }

        }
    }, 10);
}
