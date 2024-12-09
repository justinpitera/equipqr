import type { Placement, Theme, ToastType } from "svelte-toasts/types/common";
import { toasts } from "svelte-toasts";
import { t_global } from "$lib/locales";
import { homePageStore } from "./homepage";

let notificationsEnabled: boolean = typeof window !== 'undefined' ? localStorage.getItem('notificationsEnabled') !== 'false' : true;
homePageStore.notificationsEnabled.subscribe((value) => {
	notificationsEnabled = value;
});

export function notify(
	title: string,
	description: string,
	type: ToastType,
	duration = 5000,
	ignore_translate = false,
	placement: Placement = "top-center",
	theme: Theme = "dark",
	showProgress = true,
) {
	if (!notificationsEnabled) return console.log(title, description);
	toasts.add({
		title: ignore_translate ? title : t_global(title),
		description: ignore_translate ? description : t_global(description),
		duration,
		placement,
		type,
		theme,
		showProgress,
		onClick: () => { },
		onRemove: () => { },
	});
}
