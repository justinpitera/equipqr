import type { Placement, Theme, ToastType } from "svelte-toasts/types/common";
import { toasts } from "svelte-toasts";
import { langChecker, defaultLang, translations, type LanguageKeys, t_global } from "$lib/locales";

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
	toasts.add({
		title: ignore_translate ? title : t_global(title),
		description: ignore_translate ? description : t_global(description),
		duration,
		placement,
		type,
		theme,
		showProgress,
		onClick: () => {},
		onRemove: () => {},
	});
}
