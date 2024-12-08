import type { Placement, Theme, ToastType } from "svelte-toasts/types/common";
import { toasts } from "svelte-toasts";
import { langChecker, defaultLang, translations } from "$lib/locales";

function t_global(key: string): string {
	const langTranslations = translations[defaultLang];
	langChecker(key);
	return langTranslations[key] || key;
}

export function notify(
	title: string,
	description: string,
	type: ToastType,
	duration = 5000,
	placement: Placement = "top-center",
	theme: Theme = "dark",
	showProgress = true,
) {
	toasts.add({
		title: t_global(title),
		description: t_global(description),
		duration,
		placement,
		type,
		theme,
		showProgress,
		onClick: () => {},
		onRemove: () => {},
	});
}
