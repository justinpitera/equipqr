import { sineIn } from "svelte/easing";

export let flyTransitionParamsTop = {
    y: -320,
    duration: 200,
    easing: sineIn,
};

export const flyTransitionParamsBottom = {
    y: 320,
    duration: 200,
    easing: sineIn,
};