import { writable, type Writable } from "svelte/store";

class DetailsDrawerStore {
    constructor(
        public hideGSEDetail: Writable<boolean> = writable(true),
    ) { }
}

export const detailsDrawerStore = new DetailsDrawerStore();
