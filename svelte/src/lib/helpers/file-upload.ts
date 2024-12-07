
import { writable, type Writable } from "svelte/store";

class FileUploadStore {
  constructor(
    public mediaFiles: Writable<MediaFile[]> = writable([]),
    public fullscreenViewer: Writable<HTMLElement | null> = writable(null),
    public fullscreenImage: Writable<HTMLImageElement | null> = writable(null),
    public fullscreenVideo: Writable<HTMLVideoElement | null> = writable(null),
    public wiggleModeJustPressed: Writable<boolean> = writable(false),
    public wiggleModeEnabled: Writable<boolean> = writable(false),
    public isDragging: Writable<boolean> = writable(false),
    public pressTimer: Writable<NodeJS.Timeout> = writable(),
  ) { }
}

export const fileUploadStore = new FileUploadStore();

let fullscreenViewer: HTMLElement | null = null;
fileUploadStore.fullscreenViewer.subscribe((value) => {
  fullscreenViewer = value;
});

let fullscreenImage: HTMLImageElement | null = null;
fileUploadStore.fullscreenImage.subscribe((value) => {
  fullscreenImage = value;
});

let fullscreenVideo: HTMLVideoElement | null = null;
fileUploadStore.fullscreenVideo.subscribe((value) => {
  fullscreenVideo = value;
});

let isDragging = false;
fileUploadStore.isDragging.subscribe((value) => {
  isDragging = value;
});

let wiggleModeJustPressed = false;
fileUploadStore.wiggleModeJustPressed.subscribe((value) => {
  wiggleModeJustPressed = value;
});

let wiggleModeEnabled = false;
fileUploadStore.wiggleModeEnabled.subscribe((value) => {
  wiggleModeEnabled = value;
});

let pressTimer: NodeJS.Timeout | null = null;
fileUploadStore.pressTimer.subscribe((timer) => {
  pressTimer = timer;
});

export const startWiggle = () => {
  fileUploadStore.isDragging.set(false);
  const onMove = () => {
    fileUploadStore.isDragging.set(true);
    document.removeEventListener("mousemove", onMove);
    document.removeEventListener("touchmove", onMove);
  };
  document.addEventListener("mousemove", onMove);
  document.addEventListener("touchmove", onMove);
  const timer = setTimeout(() => {
    if (!isDragging) {
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("touchmove", onMove);
      fileUploadStore.wiggleModeJustPressed.set(true);
      fileUploadStore.wiggleModeEnabled.set(true);
    }
  }, 500);
  fileUploadStore.pressTimer.set(timer);
};

export const stopWiggle = () => {
  if (pressTimer) clearTimeout(pressTimer);
  document.removeEventListener("mousemove", () => { });
  document.removeEventListener("touchmove", () => { });
  setTimeout(() => {
    fileUploadStore.wiggleModeJustPressed.set(false);
  }, 100);
};

export const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target?.files) {
    const newFiles: MediaFile[] = [];
    for (const file_obj of Array.from(target.files)) {
      const file = file_obj as File;
      const url = URL.createObjectURL(file);
      const newMedia: MediaFile = {
        file,
        url,
        type: file.type,
        deleteFile: (e: Event) => {
          e.stopPropagation();
          fileUploadStore.wiggleModeJustPressed.set(false);
          fileUploadStore.wiggleModeEnabled.set(false);
          const confirmDelete = confirm(
            "Are you sure you want to delete this file?",
          );
          if (confirmDelete) fileUploadStore.mediaFiles.update((files) =>
            files.filter((item) => item.url !== url),
          );
        },
        handleClick: () => {
          if (!fullscreenVideo || !fullscreenImage || !fullscreenViewer)
            return;
          if (wiggleModeJustPressed) return;
          if (wiggleModeEnabled) {
            fileUploadStore.wiggleModeJustPressed.set(false);
            fileUploadStore.wiggleModeEnabled.set(false);
          } else {
            fullscreenViewer.classList.remove("hidden");
            fullscreenViewer.classList.add("flex");
            if (file.type.startsWith("image/")) {
              fullscreenImage.src = url;
              fullscreenImage.classList.remove("hidden");
              fullscreenVideo.classList.add("hidden");
            } else if (file.type.startsWith("video/")) {
              fullscreenVideo.src = url;
              fullscreenVideo.classList.remove("hidden");
              fullscreenImage.classList.add("hidden");
            }
          }
        },
      };
      newFiles.push(newMedia);
    }
    fileUploadStore.mediaFiles.update((files) => [...files, ...newFiles]);
    target.value = "";
  }
};

export const closeFullscreen = () => {
  if (!fullscreenVideo || !fullscreenImage || !fullscreenViewer) return;
  fullscreenViewer.classList.add("hidden");
  fullscreenViewer.classList.remove("flex");
  fullscreenImage.src = "";
  fullscreenVideo.src = "";
};
