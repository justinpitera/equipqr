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
