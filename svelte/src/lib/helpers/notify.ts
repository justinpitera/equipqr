import type { Placement, Theme, ToastType } from "svelte-toasts/types/common";
import { toasts } from "svelte-toasts";

export function notify(
	title: string,
	description: string,
	type: ToastType,
	duration = 5000,
	placement: Placement = "bottom-right",
	theme: Theme = "dark",
	showProgress = true,
) {
	toasts.add({
		title,
		description,
		duration,
		placement,
		type,
		theme,
		showProgress,
		onClick: () => {},
		onRemove: () => {},
	});
}
