
import { writable, type Writable } from "svelte/store";

class FileUploadStore {
  constructor(
    public wiggleModeJustPressed: Writable<boolean> = writable(false),
    public wiggleModeEnabled: Writable<boolean> = writable(false),
    public isDragging: Writable<boolean> = writable(false),
    public pressTimer: Writable<NodeJS.Timeout> = writable(),
  ) { }
}

export const fileUploadStore = new FileUploadStore();

export const startWiggle = () => {
  let isDragging = false;
  const unsubscribe = fileUploadStore.isDragging.subscribe((value) => {
    isDragging = value;
  });
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
    unsubscribe();
  }, 500);
  fileUploadStore.pressTimer.set(timer);
};

export const stopWiggle = () => {
  let pressTimer: NodeJS.Timeout | null = null;
  const unsubscribe = fileUploadStore.pressTimer.subscribe((timer) => {
    pressTimer = timer;
  });
  if (pressTimer) clearTimeout(pressTimer);
  document.removeEventListener("mousemove", () => { });
  document.removeEventListener("touchmove", () => { });
  setTimeout(() => {
    fileUploadStore.wiggleModeJustPressed.set(false);
  }, 100);
  unsubscribe();
};