import { toast } from "svelte-sonner";
import { t } from "$lib/locales";
import store from "$lib/store";

let notificationsEnabled: boolean = typeof window !== 'undefined' ? localStorage.getItem('notificationsEnabled') !== 'false' : true;
store.notificationsEnabled.subscribe((value) => {
	notificationsEnabled = value;
});

export type NotifyType = "success" | "error" | "info" | "warning";

export function notify(
	title: string,
	description: string,
	type: NotifyType,
	duration = 4000,
	ignore_translate = false,
) {
	if (!notificationsEnabled) return console.log(title, description);
	const resolvedTitle = ignore_translate ? title : t(title);
	const resolvedDesc = ignore_translate ? description : t(description);

	const opts = { description: resolvedDesc, duration };

	switch (type) {
		case "success": toast.success(resolvedTitle, opts); break;
		case "error":   toast.error(resolvedTitle, opts);   break;
		case "warning": toast.warning(resolvedTitle, opts); break;
		default:        toast.info(resolvedTitle, opts);    break;
	}
}
