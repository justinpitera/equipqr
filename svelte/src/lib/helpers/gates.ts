import store from "$lib/store";

export let gate_types: Record<string, string[]> = {
    GA: ["103 Apn"],
    Airline: ["A11"],
    None: ["G110"],
    Cargo: ["G126"],
};

export function build_gate_options(gate: string, forceSelect?: string) {
    store.selected_gate_type.set(gate);
    store.is_gate_type_dropdown_open.set(false);
    store.gates.set([]);
    store.gates.update((currentGates) => {
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
