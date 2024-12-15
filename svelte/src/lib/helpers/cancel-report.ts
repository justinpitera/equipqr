import { sineIn } from "svelte/easing";
import { writable, type Writable } from "svelte/store";

class CancelReportStore {
    constructor(
        public closeReportHidden: Writable<boolean> = writable(true),
    ) { }
}

export const cancelReportStore = new CancelReportStore();

// let closeReportHidden = false;
// cancelReportStore.closeReportHidden.subscribe((value) => {
//     closeReportHidden = value;
// });

export let transitionParamsTop = {
    y: -320,
    duration: 200,
    easing: sineIn,
};