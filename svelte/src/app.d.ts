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
	interface GSEDetails {
		gse_id: string;
		gse_type: string;
		model: string;
		manufacturer: string;
		location: string;
		status: string;
		type_of_fuel: string;
		in_use: boolean;
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
