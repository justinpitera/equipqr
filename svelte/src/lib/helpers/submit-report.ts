import { fileUploadStore } from "$lib/helpers/file-upload";

let mediaFiles: MediaFile[] = [];
fileUploadStore.mediaFiles.subscribe((value) => {
    mediaFiles = value;
});

export function handleFormSubmit(event: Event): void {
    event.preventDefault();
    const uploadedFiles = mediaFiles.map(
        (file) => `${file.file.name} (${file.file.size} bytes)`,
    );
    alert(`Selected files:\n${uploadedFiles.join("\n")}`);
    const issueDescription = (
        document.getElementById("issue-description") as HTMLTextAreaElement
    ).value;
    alert(
        `Form submitted with the following details:\nIssue Description: ${issueDescription}\nNumber of Files: ${mediaFiles.length}`,
    );
}
