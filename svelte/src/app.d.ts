// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	interface MediaFile {
		file: File;
		url: string;
		type: string;
		deleteFile: (event: Event) => void;
		handleClick: () => void;
	}
	interface GSEDetails { // getGSEDetails - /api/gse/details
		gse_id?: string;
		old_gse_id?: string;
		gse_type?: string;
		model?: string;
		manufacturer?: string;
		location?: string;
		status?: string;
		issue_count?: string;
		type_of_fuel?: string;
		in_use?: boolean;
		most_recent_issue?: {
			id: string;
			gse_id: string;
			issue_description: string;
			reported_at: string;
			attachments: string;
		};
		lift_inspection_expires?: string | null;
		latest_service_chassi?: string | null;
		latest_service_unit?: string | null;
		capacity?: number | null;
		details?: string;
		error?: string;
	}
	interface Equipment {
		[key: string]: string;
	}
	interface CanvasRenderingContext2D extends CanvasRenderingContext2D {
		willReadFrequently?: boolean;
	}
	interface Issue {
		gse_id: number;
		employee_name: string;
		issue_description: string;
		is_operable: string;
		gate_type?: string;
		gate_name?: string;
	}
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}

	// Torch Capability:
	interface ExtendedMediaTrackConstraintSet extends MediaTrackConstraintSet {
		torch?: boolean;
	}
	interface ExtendedMediaTrackCapabilities extends MediaTrackCapabilities {
		torch?: boolean;
	}
	interface ITorchInfo {
		hasCamera: boolean;
		hasTorch: boolean;
		track?: MediaStreamTrack;
		stream?: MediaStream;
		screenWakeLock?: WakeLockSentinel;
	}
}

export { };
